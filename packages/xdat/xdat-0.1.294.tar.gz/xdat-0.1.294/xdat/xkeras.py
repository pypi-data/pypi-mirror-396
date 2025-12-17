import hashlib
from functools import reduce
import operator
import weakref

from . import xparallel, xcv, xsettings

try:
    import tensorflow_probability as tfp
except ImportError:
    pass

import pickle
import portalocker
import os
import uuid
import gc
import time
from scriptine import path
import tensorflow as tf
from tensorflow.keras import backend as K
from tensorflow.keras.layers import Conv2D, Layer, Dense, GlobalAveragePooling2D, GlobalMaxPooling2D, Reshape, Activation, add, multiply, Normalization
from tensorflow.keras.models import clone_model
import numpy as np
import pandas as pd
from tensorflow.keras.preprocessing.image import load_img
from tensorflow.keras.utils import Sequence, register_keras_serializable
import imgaug.augmenters as iaa


def clone_keras_model(model):
    # Clone the model's architecture
    cloned_model = clone_model(model)

    # Compile the cloned model (use the same parameters as the original model)
    cloned_model.compile(optimizer=model.optimizer,
                         loss=model.loss,
                         metrics=model.metrics)

    return cloned_model


def copy_keras_layer(layer):
    # Create a new layer from the existing layer's configuration
    new_layer = layer.__class__.from_config(layer.get_config())

    # Check if the layer has weights to be set
    if hasattr(layer, 'get_weights') and layer.get_weights():
        # Create a dummy input to build the layer based on the input shape of the original layer
        if hasattr(layer, 'input_shape') and layer.input_shape:
            input_shape = layer.input_shape
            if input_shape[0] is None:  # Handle possible None in the batch dimension
                input_shape = (1,) + input_shape[1:]
            dummy_input = tf.random.normal(input_shape)
            new_layer(dummy_input)  # Build the layer

        # Now set the weights
        new_layer.set_weights(layer.get_weights())

    return new_layer


class DataSample:
    def __init__(self, inputs, outputs, weight=None):
        if isinstance(inputs, tuple):
            inputs = list(inputs)
        elif not isinstance(inputs, list):
            inputs = [inputs]

        if outputs is None:
            outputs = []
        elif isinstance(outputs, tuple):
            outputs = list(outputs)
        elif not isinstance(outputs, list):
            outputs = [outputs]

        self.inputs = inputs
        self.outputs = outputs
        self.weight = weight

    def __repr__(self):
        return f"<DataSample inputs={len(self.inputs)} outputs={len(self.outputs)} weight={self.weight is not None}>"


class SafePredictor:
    """
    Wrapper around a tf.keras.Model to avoid memory leaks vs model.predict()
    (e.g. for TF 2.13.1).

    Supported X:

      1. Single batch:
         - np.ndarray / tf.Tensor (single input)
         - list/tuple of np.ndarray / tf.Tensor (multi-input)

      2. Sequence of batches (e.g. tf.keras.utils.Sequence):
         - sequence[i] -> X
         - sequence[i] -> (X, y)
         - sequence[i] -> (X, y, w)
         where X is either:
           - np.ndarray / tf.Tensor
           - list/tuple of arrays for multi-input
    """

    def __init__(self, model: tf.keras.Model):
        assert isinstance(model, tf.keras.Model), type(model)
        self.model = model

        @tf.function
        def _infer(inputs):
            # Keras handles single vs multi-input
            return model(inputs, training=False)

        self.infer = _infer

    # ---------- Public API ----------

    def predict(self, X, **kwargs):
        # Case 1: single batch, single input
        if isinstance(X, (np.ndarray, tf.Tensor)):
            return self._predict_single_batch(X)

        # Case 2: single batch, multi-input (list/tuple of arrays)
        if isinstance(X, (list, tuple)) and self._looks_like_multi_input_batch(X):
            return self._predict_single_batch(X)

        # Case 3: Sequence of batches (e.g. Keras Sequence)
        if isinstance(X, Sequence):
            # Note: lists/tuples of arrays were already caught above,
            # so reaching here means "Sequence of batches"
            return self._predict_sequence(X)

        raise TypeError(
            f"Unsupported type for X: {type(X)}. "
            "Expected a numpy array / tensor, a list of arrays (multi-input), "
            "or a Sequence of batches."
        )

    # ---------- Helpers ----------

    def _looks_like_multi_input_batch(self, x):
        """
        Decide if x (a list/tuple) is a multi-input *batch* rather than
        a Sequence of batches.

        We assume multi-input batch if:
          - elements are arrays/tensors (or None),
          - and not themselves Sequences of batches.
        """
        if len(x) == 0:
            return False

        # if all elements are array/tensor-like (or None), treat as multi-input
        for elem in x:
            if elem is None:
                continue
            if not isinstance(elem, (np.ndarray, tf.Tensor)):
                # Could be a nested structure; be conservative.
                return False
        return True

    def _to_inputs(self, batch_X):
        """
        Normalize X for a single batch into Keras-acceptable input:
        - single input -> tensor
        - multi-input -> list of tensors
        """
        if isinstance(batch_X, (list, tuple)):
            # multi-input case
            return [tf.convert_to_tensor(x) for x in batch_X]
        else:
            return tf.convert_to_tensor(batch_X)

    # ---------- Single-batch predict ----------

    def _predict_single_batch(self, batch_X):
        inputs = self._to_inputs(batch_X)
        y = self.infer(inputs)

        # Multi-output -> list of numpy arrays
        if isinstance(y, (list, tuple)):
            return [o.numpy() for o in y]

        # Single-output -> single numpy array
        return y.numpy()

    # ---------- Sequence-of-batches predict ----------

    def _predict_sequence(self, seq: Sequence):
        """
        seq[i] returns:
          - X
          - (X, y)
          - (X, y, w)
        where X can itself be single- or multi-input.
        """
        n = len(seq)
        if n == 0:
            raise ValueError("Empty Sequence provided to SafePredictor.predict().")

        outputs = None

        for i in range(n):
            item = seq[i]

            # Extract X from (X), (X, y) or (X, y, w)
            if isinstance(item, tuple):
                if len(item) == 0:
                    raise ValueError("Sequence item is an empty tuple.")
                batch_X = item[0]
            else:
                batch_X = item

            inputs = self._to_inputs(batch_X)
            y = self.infer(inputs)

            if not isinstance(y, (list, tuple)):
                y = [y]

            if outputs is None:
                outputs = [[] for _ in y]

            for j, out_tensor in enumerate(y):
                outputs[j].append(out_tensor.numpy())

        merged = [np.concatenate(parts, axis=0) for parts in outputs]
        return merged[0] if len(merged) == 1 else merged


class CachedDataGenerator(Sequence):
    """
    A relatively simple way to build data generators for complex models.
    Bonus: has a build-in caching mechanism to optimize calculations (when needed)

    Memory requirements:
      - System memory (RAM): enough to hold all model data (train, val, test)
      - GPU memory: enough for a single batch
    """

    _CACHE_FOLDERS = dict()

    def __init__(self, data, batch_size=32, mode=None, n_jobs=1, n_jobs_batch_size=128, dtype=np.float16, cache_folder=None, verbose=False):
        """
        :param batch_size: the size of the batch ("typical" ML batch)
        :param n_jobs_batch_size: the batch sized used when creating dataset in parallel (faster get_sample() should have larger value)
        """

        if mode == 'train':
            mode = 'fit'

        assert mode in ['fit', 'val', 'test', 'prod'], mode

        self.data_orig = data
        self.df = None
        self.X, self.Y, self.w = None, None, None
        self.indices_df = None    # indices in df -- used to see which rows are relevant: get_sample() can return None
        self.indices_xyw = None   # indices in X, Y, w (numpy) -- used for fetching batches  (same length as self.indices_df)

        if cache_folder is None:
            cache_folder = xsettings.OUTPUT_PATH.joinpath('data_gen_cache')

        self._cache_folder = path(cache_folder)
        if mode == 'prod':
            temp_folder = str(uuid.uuid4())
            self._cache_folder = self._cache_folder.joinpath(temp_folder)

        self._cache_folder.ensure_dir()
        self._cache_miss_file = self._cache_folder.joinpath('CACHE_MISS_COUNT.TXT')

        self.batch_size = batch_size
        self.mode = mode
        self.n_jobs = n_jobs
        self.n_jobs_batch_size = n_jobs_batch_size
        self.dtype = dtype
        self.verbose = verbose
        self._last_log = time.time()

        self._count_cache = False   # if True, count cache hits/misses

        self._with_outputs = None   # gets set to True if there is a Y
        self._with_weight = None    # gets set to True if there is a w
        self._input_shapes = None
        self._output_shapes = None
        self._dtype = None

        self._curr_idx_count = 0
        self.curr_epoch = 0
        self.init()

    def log(self, text):
        if self.verbose:
            now = time.time()
            run_time, self._last_log = now - self._last_log, now

            print(f'{text}    [{run_time:.3f} sec]')

    def init(self):
        df_initial = self.data_orig
        df_initial = self.transform_data(df_initial)

        self.set_df(df_initial)
        self.on_epoch_end()
        self.update_XYw()

    def __del__(self):
        del self.X, self.Y, self.w
        del self.data_orig, self.df
        del self.indices_df, self.indices_xyw

        gc.collect()

    @property
    def df_data(self):
        """
        df for valid samples only (those that get_sample() returned a valid value)
        """

        return self.df[self.indices_df].reset_index(drop=True)

    def __len__(self):
        return int(np.ceil(len(self.indices_xyw) / float(self.batch_size)))

    def __getitem__(self, idx):
        #
        # implement on_epoch_start()
        if self._curr_idx_count == 0:
            self.curr_epoch += 1
            self._on_epoch_start()

        self._curr_idx_count += 1

        #
        # get current batch info
        batch_indices = self.indices_xyw[idx * self.batch_size:(idx + 1) * self.batch_size]

        X = [X[batch_indices] for X in self.X]
        Y = [Y[batch_indices] for Y in self.Y] if self._with_outputs else None
        w = self.w[batch_indices] if self._with_weight else None

        return X, Y, w

    def clear_XYw(self):
        self.indices_xyw, self.X, self.Y, self.w = None, None, None, None

    def update_XYw(self, force=False):
        if force and self.X is not None:
            self.clear_XYw()
            gc.collect()

        if self.X is None:
            self.X, self.Y, self.w, self.indices_df = self.calc_XYw(self.df)
            self.indices_xyw = np.arange(len(self.X[0]))

    def cache_miss_count_init(self):
        # clear cache miss file
        if self._cache_miss_file.exists():
            self._cache_miss_file.remove()

    def cache_miss_count_calc(self):
        if self._cache_miss_file.exists():
            with open(self._cache_miss_file, 'r') as f:
                text = f.read()
            cache_miss_count = sum(c == '1' for c in text)
            return cache_miss_count

    def calc_XYw(self, df, with_tqdm=None):
        iterrows = lambda dfx: (row for _, row in dfx.iterrows())

        arr_size = None
        if self.mode != 'prod':
            txt = ''
            if self.n_jobs == 1:
                txt = f', also n_jobs == 1'
            print(f'- INFO: about to calculate XYw (may be slow if not cached{txt}) [{self.mode}]')

            #
            # see if need to check cache, etc
            self._count_cache = self._curr_idx_count == 0 and self.n_jobs != 1

            #
            # see if should disable parallel
            self.cache_miss_count_init()

            xparallel.x_on_iter(iterrows(df[:1]), self._get_sample_wrapper, with_tqdm=False, n_jobs=1)
            cache_miss_count = self.cache_miss_count_calc()

            self._count_cache = False

            if cache_miss_count == 0:
                print(f"- INFO: disabling parallel, no cache misses [{self.mode}]")
                self.n_jobs = 1
            else:
                with_tqdm = True
                if self.n_jobs == 1:
                    print(f"- WARNING: about to calculate XYw, but n_jobs=1 (it's bad if get_sample() is slow) [{self.mode}]")

                else:
                    #
                    # gather the samples as a pre-fetch in parallel
                    print('- about to pre-calc samples in parallel')
                    self.log('- pre-gathering samples (in parallel)')
                    xparallel.x_on_iter(iterrows(df), self._get_sample_wrapper, with_tqdm=with_tqdm, total=len(df), n_jobs=self.n_jobs, batch_size=self.n_jobs_batch_size, tqdm_desc=f'calc XYw - {self.mode}', drop_results=True)

        #
        # prepare generator
        self.clear_cache('__calc_XYw_', warn_if_missing=False)
        def iterate_samples():
            for idx, row in enumerate(iterrows(df)):
                sample = self.cached('__calc_XYw_', self._get_sample_wrapper, row, _as_pickle=True)
                if sample is not None:
                    yield idx, sample

        #
        # getting sample0 for shape information
        sample0 = None
        for _, sample0 in iterate_samples():
            break

        assert sample0 is not None, "At least one sample should be DataSample"

        self.log('- calculating results size')
        indices_df = [idx for idx, _ in iterate_samples()]
        arr_size = len(indices_df)

        #
        # initialize data format:
        if self._with_weight is None:
            self.log('  + initializing data format')
            assert sample0.inputs
            inputs = sample0.inputs
            self._with_outputs = bool(sample0.outputs)
            self._with_weight = sample0.weight is not None
            self._dtype = inputs[0].dtype

            self._input_shapes = []
            self._output_shapes = []

            for arr in sample0.inputs:
                self._input_shapes.append(list(arr.shape))
                assert arr.dtype == self._dtype

            if self._with_outputs:
                for arr in sample0.outputs:
                    if isinstance(arr, np.ndarray):
                        self._output_shapes.append(list(arr.shape))
                        assert arr.dtype == self._dtype
                    else:
                        self._output_shapes.append([1])

        #
        # build data structures
        def stack_input_from_gen(gen, shape):
            arr = np.empty((arr_size, *shape), dtype=self.dtype)

            for idx, a in enumerate(gen):
                arr[idx] = a

            return arr

        final_inputs = []
        final_outputs = None
        final_weights = None
        self.log('  + stacking inputs')
        for idx, shape in enumerate(self._input_shapes):
            arr = stack_input_from_gen((s.inputs[idx] for _, s in iterate_samples()), shape)
            # arr = arr.reshape([arr_size]+shape)
            final_inputs.append(arr)

        self.log('  + stacking outputs')
        if self._with_outputs:
            final_outputs = []
            for idx, shape in enumerate(self._output_shapes):
                arr = stack_input_from_gen((s.outputs[idx] for _, s in iterate_samples()), shape)
                # arr = arr.reshape([arr_size]+shape)
                final_outputs.append(arr)

        self.log('  + preparing weights')
        if self._with_weight:
            final_weights = np.array([s.weight for _, s in iterate_samples()])

        self.clear_cache('__calc_XYw_')
        gc.collect()
        return final_inputs, final_outputs, final_weights, indices_df

    def cached(self, name, func, *args, _as_pickle=False, **kwargs):
        """
        Helper function, can use inside get_sample()
        Basically "smart" caching, in the sense that during the fit, if n_jobs > 1,
           but everything is in cache, then sets n_jobs = 1.

        Example:
        self.cached('load', self.load, img_path1)

        Can later call, if want:
        self.clear_cache('load')
        """

        cache_key = list(str(i) for i in args) + [f"{k}:{v}" for k,v in sorted(kwargs.items())]
        cache_key = "; ".join(cache_key)

        cache_hash = hashlib.md5(cache_key.encode('utf-8')).hexdigest()
        cache_subfolder = self._cache_folder.joinpath(name)
        cache_subfolder.ensure_dir()
        cache_file = cache_subfolder.joinpath(f"{cache_hash}.npy")
        cache_file_exists = cache_file.exists()

        if self._count_cache:
            cache_miss = int(not cache_file_exists)

            #
            # write cache misses to file
            with open(self._cache_miss_file, 'a') as file:
                # Acquire an exclusive lock on the file
                portalocker.lock(file, portalocker.LOCK_EX)
                try:
                    file.write(str(cache_miss))
                    file.flush()
                    os.fsync(file.fileno())  # Ensure data is written to disk
                finally:
                    # Release the lock
                    portalocker.unlock(file)

        if cache_file_exists:
            if _as_pickle:
                with open(cache_file, "rb") as f:
                    results = pickle.load(f)
            else:
                results = np.load(cache_file, allow_pickle=True)
            return results

        else:
            results = func(*args, **kwargs)
            if _as_pickle:
                with open(cache_file, "wb") as f:
                    pickle.dump(results, f)
            else:
                assert isinstance(results, np.ndarray), type(results)
                np.save(cache_file, results)

        return results

    def clear_cache(self, cache_name, warn_if_missing=True):
        """
        Helper function: can use inside on_epoch_start()
        Clears a cache folder (by name)
        """

        cache_subfolder = self._cache_folder.joinpath(cache_name)
        if not cache_subfolder.exists():
            if warn_if_missing:
                print(f'WARNING: {cache_name} not in {self._cache_folder}')
            return

        cache_subfolder.rmtree()
        self.clear_XYw()

    def clear_all_cache(self):
        if self._cache_folder.exists():
            self._cache_folder.rmtree()
        self.clear_XYw()

    def transform_data(self, data, **kwargs):
        """
        (used for both on train & predict)
        Converts input data into the main dataframe.
        By default, nothing happens, but it's a placeholder for business logic.
        Example use case: add weights // want to change the training set between epochs.
        """

        assert isinstance(data, pd.DataFrame), type(data)
        return data.copy()

    def set_df(self, df):
        """
        Updates the df to be used. Typically called with the df that transform_data() returns.
        Example use case: want to change the training set between epochs.
        """

        assert isinstance(df, pd.DataFrame)
        self.df = df.copy()
        self.clear_XYw()

    def _get_sample_wrapper(self, row):
        sample = self.get_sample(row)
        if sample is None:
            return None

        for idx in range(len(sample.inputs)):
            X = sample.inputs[idx]
            assert np.isnan(X).sum() == 0 and np.isinf(X).sum() == 0, row
            if isinstance(X, np.ndarray):
                sample.inputs[idx] = X.astype(self.dtype)

        for idx in range(len(sample.outputs)):
            Y = sample.outputs[idx]
            assert np.isnan(Y).sum() == 0 and np.isinf(Y).sum() == 0, row

            if isinstance(Y, np.ndarray):
                sample.outputs[idx] = Y.astype(self.dtype)

        return sample

    def get_sample(self, row):
        """
        Given a row (of the transformed dataframe), return a DataSample()
        Basically, converts a dataframe row to a model's inputs, outputs, and weight.
        Note: this MUST be implemented.
        Note: if get_sample() returns None (ok), need to call force_length() after

        Example:
        img1 = self.cached('load', self.load, img_path1)
        img2 = self.cached('load', self.load, img_path2)

        return DataSample([img1, img2], row.target, row.weight)

        :rtype: DataSample or None if this sample is not relevant for the model
        """
        raise NotImplementedError

    def force_length(self, a):
        """
        Useful to make sure that prediction length is same as input df.
        (For example, when not every row returns a valid get_sample())

                gen_test = self.get_gen(df_test, mode='test')
                y_pred = model.predict(gen_test)            # len(y_pred) may not equal len(df_test)
                y_pred = gen_test.force_length(y_pred)      # now len(y_pred) equals len(df_test), by inserting nulls
        """

        assert isinstance(a, np.ndarray)
        assert len(self.indices_df) == len(a)

        # total number of rows
        len_total = len(self.df)

        # Determine the shape of the output array
        output_shape = (len_total, *a.shape[1:])

        # Initialize an array of NaNs with the required shape
        a_with_nulls = np.full(output_shape, np.nan)

        # Use advanced indexing to place 'a' into 'a_with_nulls' at the correct indices
        a_with_nulls[self.indices_df, ...] = a

        return a_with_nulls

    def _on_epoch_start(self):
        self.update_XYw()

        if self.mode == 'fit':
            np.random.shuffle(self.indices_xyw)

        self.on_epoch_start()

    def on_epoch_start(self):
        """
        Hook to call before each new epoch.
        Example use cases: update the training set, clear caches, etc.

        Example:
        if self.curr_epoch % 4 == 0:
            self.clear_cache('aug')
        """
        pass

    def on_epoch_end(self):
        """
        Gets called at end of each epoch.
        If overwritten, must call (otherwise, on_epoch_start() will break...):
        super().one_epoch_end()
        """

        self._curr_idx_count = 0

    def as_XYw(self):
        """
        Transform the generator to full-memory X, Y, weights model inputs.
        (for when there isn't enough data to warrant actually building the model with a generator)
        """
        self.update_XYw()

        X = [X for X in self.X]
        Y = [Y for Y in self.Y] if self._with_outputs else None
        w = self.w if self._with_weight else None

        return X, Y, w


class ImageDataGenerator(Sequence):
    """
    batch_size=32
    target_size=(224,224)

    generator = ImageDataGenerator(df, batch_size, target_size)
    model.fit(generator, epochs=epochs)

    generator_for_prediction = ImageDataGenerator(df, batch_size, target_size, target_col=None, shuffle=False)
    predictions = model.predict(generator_for_prediction)

    There's a convenience function to put everything in memory (undo generator):
    X, y = generator.as_full_memory()
    """

    def __init__(self, dataframe, batch_size, target_size_hw=None, target_size_wh=None, shuffle=True, image_path_col='image_path', target_col='target', weight_col=None, process_image=None, aug_y=None, mult_input_proc=None, file_cache=None, rgb=True, scale_colors=True, with_aug=False, aug_seq=None, zoom=1, mode=None, check_cache_on_init=True, n_jobs=-1, parallel_one_epoch_only=True, dtype=np.float16):
        """
        :param dataframe:
        :param batch_size:
        :param target_size_hw: (height, width)
        :param target_size_wh: (width, height)
        :param shuffle: should be False for predictions
        :param image_path_col: where to find images
        :param target_col: target
        :param weight_col: weight (optional)
        :param process_image: how to process the image (optional)
        :param aug_y: how to augment y (in training only)
        :param zoom: how much to zoom in center (2 is twice as much)
        :param file_cache: (str, optional) path to save file cache
        :param mode: 'fit', 'val', 'predict-train', 'predict-test', 'memory'
        """

        if weight_col:
            assert target_col

        self.dataframe = dataframe
        self.batch_size = batch_size

        assert sum([bool(target_size_wh), bool(target_size_hw)]) == 1
        if target_size_wh:
            target_size_hw = tuple(reversed(target_size_wh))

        self.target_size_hw = target_size_hw
        self.target_size_wh = tuple(reversed(self.target_size_hw))

        self.shuffle = shuffle
        self.image_path_col = image_path_col
        self.target_col = target_col
        self.weight_col = weight_col
        self.file_cache = file_cache
        self.rgb = rgb
        self.scale_colors = scale_colors
        self.with_aug = with_aug
        self.zoom = zoom
        self.mult_input_proc = mult_input_proc
        self.check_cache_on_init = check_cache_on_init
        self.n_jobs = n_jobs
        self.parallel_one_epoch_only = parallel_one_epoch_only
        self.dtype = dtype
        self.very_first_batch = True

        self.aug_seq = aug_seq
        if self.aug_seq is None:
            self.aug_seq = iaa.geometric.Affine(
                scale=(1.0, 1.5),
                rotate=(0, 360),
                shear=(-20, 20),
            )

        if self.file_cache:
            self.file_cache = path(self.file_cache)
            self.file_cache.ensure_dir()

        self.indices = np.arange(len(dataframe))
        if process_image is not None:
            self.process_image = process_image

        self.aug_y = aug_y

        if mode == 'fit':
            self.set_mode_fit()
        elif mode in ['val', 'validation']:
            self.set_mode_validation()
        elif mode == 'predict-train':
            self.set_mode_predict(new_dataset=False)
        elif mode in ['predict-test', 'test']:
            self.set_mode_predict(new_dataset=True)
        elif mode == 'memory':
            self.set_mode_memory()
        else:
            raise ValueError(mode)

        print(f'- INFO: generator mode={mode}, shuffle={"on" if self.shuffle else "off"}, aug={"on" if self.with_aug else "off"}, aug_y={"on" if self.aug_y else "off"}, parallel={"off" if self.n_jobs == 1 else "on"}, file_cache={"on" if self.file_cache else "off"}')

        if self.shuffle:
            np.random.shuffle(self.indices)

    def set_mode_fit(self):
        self.shuffle = True
        if self.with_aug:
            self.file_cache = False

        self.n_jobs = -1
        assert self.target_col is not None

    def set_mode_validation(self):
        self.shuffle = False
        self.n_jobs = -1
        self.with_aug = False
        self.aug_y = None

    def set_mode_predict(self, new_dataset=True):
        self.shuffle = False
        self.n_jobs = -1 if new_dataset else 1
        self.target_col = None
        self.with_aug = False
        self.aug_y = None

    def set_mode_memory(self):
        self.shuffle = False
        self.n_jobs = -1

    def __len__(self):
        return int(np.ceil(len(self.dataframe) / float(self.batch_size)))

    def __getitem__(self, idx):
        batch_indices = self.indices[idx * self.batch_size:(idx + 1) * self.batch_size]
        batch_rows = [self.dataframe.iloc[i] for i in batch_indices]
        df_batch = pd.DataFrame(batch_rows)

        if self.very_first_batch and self.n_jobs != 1 and self.check_cache_on_init:
            num_cache = sum([self.load_and_preprocess_image(p, is_from_cache=True) for p in df_batch[self.image_path_col].tolist()])
            if num_cache == len(df_batch):
                print("- INFO: disabling parallel, all images in cache")
                self.n_jobs = 1

        self.very_first_batch = False

        images = xparallel.x_on_iter(batch_rows, lambda row: self.load_and_preprocess_image(row[self.image_path_col]), with_tqdm=False, n_jobs=self.n_jobs)
        images = np.array(images)
        X = images

        if self.mult_input_proc:
            X = self.mult_input_proc(df_batch, images)
            assert isinstance(X, list), type(X)
            assert len(X) > 1, len(X)

        if self.target_col is None:
            if not self.mult_input_proc:
                return X

            assert isinstance(X, list), type(X)
            assert len(X) > 1, len(X)
            # TODO: FIX THIS HELL:
            return X, df_batch.index.values

        res = [X]

        if isinstance(self.target_col, list) or isinstance(self.target_col, tuple):
            yy = df_batch[self.target_col].to_numpy()
            yy = [c for c in yy.T]
            yy2 = []
            for y in yy:
                if isinstance(y[0], list):
                    y = np.array(y.tolist(), dtype=self.dtype)
                else:
                    y = np.array(y, dtype=self.dtype)
                yy2.append(y)

            labels = yy2
        else:
            labels = df_batch[self.target_col].to_numpy()
            if isinstance(labels[0], list):
                labels = np.array(labels.tolist())
            labels = self.wrap_aug_y(labels)

        res.append(labels)

        if self.weight_col:
            if isinstance(self.weight_col, dict):
                weights = {k:df_batch[v].to_numpy() for k, v in self.weight_col.items()}
            else:
                weights = df_batch[self.weight_col].to_numpy()
            res.append(weights)

        return tuple(res)

    def as_full_memory(self, n_jobs=-1):
        self.indices = np.arange(len(self.dataframe))

        i0 = self[0]
        if self.target_col is not None:
            i0 = i0[0]

        img_shape = list(i0.shape)[1:]
        n_samples = len(self.dataframe)
        full_shape = [n_samples] + list(img_shape)
        mem_size = reduce(operator.mul, full_shape, 1)
        mem_size_mb = 4*mem_size / 1000000
        print(f"{mem_size_mb:.1f}Mb")

        X = np.zeros(full_shape, dtype=np.float32)   # TODO: may want np.float16

        def calc(batch_num):
            X_batch = self[batch_num]
            return batch_num, X_batch

        num_batches = len(self)
        for batch_num, X_batch in xparallel.x_on_iter_as_gen(range(num_batches), calc, total=num_batches, n_jobs=n_jobs):
            if self.target_col is not None:
                X_batch, y_batch = X_batch

            start_index = batch_num*self.batch_size
            X[start_index:start_index + X_batch.shape[0], :, :, :] = X_batch

        if not self.target_col:
            return X

        res = [X]
        res.append(self.dataframe[self.target_col])
        if self.weight_col:
            res.append(self.dataframe[self.weight_col])

        return tuple(res)

    def on_epoch_end(self):
        # TODO: put shuffle in on_epoch_start()
        if self.shuffle:
            np.random.shuffle(self.indices)

        if self.n_jobs != 1 and self.file_cache and self.parallel_one_epoch_only and not self.with_aug:
            print('- INFO: disabling parallelism in generator')
            self.n_jobs = 1

    def load_and_preprocess_image(self, image_path, is_from_cache=False):
        if self.file_cache:
            hash = hashlib.md5(image_path.encode()).hexdigest()
            hash_path = self.file_cache.joinpath(f"{hash}.npy")
            if hash_path.exists():
                if is_from_cache:
                    return True

                return np.load(hash_path)

            if is_from_cache:
                return False

            val = self._load_and_preprocess_image_do(image_path)
            np.save(hash_path, val)
            return val

        else:
            if is_from_cache:
                return False

            val = self._load_and_preprocess_image_do(image_path)
            return val

    def do_augmentation(self, img):
        img = self.aug_seq(images=[img])[0]
        return img

    def _load_and_preprocess_image_do(self, image_path):
        if image_path[-4:] == '.npy':
            img = np.load(image_path)
        else:
            img = load_img(image_path)

            if self.zoom > 1:
                img = xcv.crop_zoom_center(img, factor=self.zoom)

            if self.rgb:
                img = img.convert('RGB')

            img = np.array(img)

        if self.with_aug:
            img = self.do_augmentation(img)

        img = xcv.resize_and_center_crop(img, self.target_size_wh)

        if self.scale_colors:
            img = img / 255

        img = self.process_image(img)
        assert img.shape[:2] == self.target_size_hw, img.shape
        return img.astype(np.float32)

    def process_image(self, img):
        return img

    def wrap_aug_y(self, y):
        if not self.aug_y:
            return y

        return self.aug_y(y)


class SafeNormalizationLayer(Layer):
    def __init__(self, epsilon=1e-7, max_val=20.0, dtype=tf.float32, **kwargs):
        """
        Custom SafeNormalization layer with capping.

        Args:
            epsilon (float): Small value added to variance to prevent division by zero.
            max_val (float): Maximum cap value for the normalized output.
        """
        super(SafeNormalizationLayer, self).__init__(**kwargs)
        self.epsilon = epsilon
        self.max_val = max_val
        self.dtype_ = dtype
        self.mean = None
        self.variance = None

    def get_config(self):
        config = super(SafeNormalizationLayer, self).get_config()
        config.update({
            "epsilon": self.epsilon,
            "max_val": self.max_val,
            "dtype": self.dtype_,
        })
        return config

    def build(self, input_shape):
        self.mean = self.add_weight(
            shape=(input_shape[-1],), initializer="zeros", trainable=False, dtype=self.dtype_, name="mean"
        )
        self.variance = self.add_weight(
            shape=(input_shape[-1],), initializer="ones", trainable=False, dtype=self.dtype_, name="variance"
        )

    def adapt(self, data):
        # Build the layer if it hasn't been built yet
        if not self.built:
            self.build(data.shape)

        # Calculate the mean and variance of the data
        mean = tf.reduce_mean(data, axis=0)
        variance = tf.reduce_mean(tf.square(data - mean), axis=0)

        # Assign computed values to the layer's mean and variance
        self.mean.assign(mean)
        self.variance.assign(variance)

    def call(self, inputs):
        # Normalize with added epsilon to avoid division by zero
        stddev = K.sqrt(self.variance + self.epsilon)
        normalized = (inputs - self.mean) / stddev

        # Apply capping to the normalized values
        capped = tf.clip_by_value(normalized, -1.0*self.max_val, self.max_val)
        return capped


class SpatialAttentionLayer(Layer):
    def __init__(self, **kwargs):
        super(SpatialAttentionLayer, self).__init__(**kwargs)
        # Initialize the Conv2D layer with a single filter for spatial attention
        self.conv2d = Conv2D(1, (3, 3), activation='sigmoid', padding='same')

    def call(self, input_feature):
        # Apply the Conv2D layer to learn spatial attention
        attention = self.conv2d(input_feature)
        return attention * input_feature

    def get_config(self):
        return super(SpatialAttentionLayer, self).get_config()


class ChannelAttentionLayer(Layer):
    def __init__(self, ratio=8, **kwargs):
        super(ChannelAttentionLayer, self).__init__(**kwargs)
        self.ratio = ratio
        self.shared_layer_one = None
        self.shared_layer_two = None

    def build(self, input_shape):
        channel = input_shape[-1]
        # Initialize shared layers in the build method to ensure the channel dimension is known
        self.shared_layer_one = Dense(channel // self.ratio, activation='relu', kernel_initializer='he_normal', use_bias=True, bias_initializer='zeros')
        self.shared_layer_two = Dense(channel, kernel_initializer='he_normal', use_bias=True, bias_initializer='zeros')
        super(ChannelAttentionLayer, self).build(input_shape)

    def call(self, input_feature):
        channel = input_feature.shape[-1]
        avg_pool = GlobalAveragePooling2D()(input_feature)
        avg_pool = Reshape((1, 1, channel))(avg_pool)
        avg_pool = self.shared_layer_one(avg_pool)
        avg_pool = self.shared_layer_two(avg_pool)

        max_pool = GlobalMaxPooling2D()(input_feature)
        max_pool = Reshape((1, 1, channel))(max_pool)
        max_pool = self.shared_layer_one(max_pool)
        max_pool = self.shared_layer_two(max_pool)

        attention = add([avg_pool, max_pool])
        attention = Activation('sigmoid')(attention)

        return multiply([input_feature, attention])

    def get_config(self):
        config = super(ChannelAttentionLayer, self).get_config()
        config.update({"ratio": self.ratio})
        return config


class QuantileLayer(tf.keras.layers.Layer):
    """
    Computes quantiles for each channel, preserving the batch dimension.
    Input shape: (batch_size, height, width, channels)
    Output shape: (batch_size, channels, num_quantiles)
    """

    def __init__(self, num_quantiles, with_ends=False, **kwargs):
        super(QuantileLayer, self).__init__(**kwargs)
        self.num_quantiles = num_quantiles
        self.with_ends = with_ends

        if with_ends:
            self.quantiles = tf.linspace(0.0, 1.0, self.num_quantiles)
        else:
            self.quantiles = tf.linspace(0.0, 1.0, self.num_quantiles+2)[1:-1]

    def call(self, inputs):
        input_shape = tf.shape(inputs)
        batch_size = input_shape[0]
        channels = input_shape[-1]

        # Flatten the spatial dimensions and keep channels separate
        inputs_flat = tf.reshape(inputs, [batch_size, -1, channels])

        quantiles = tf.cast(self.quantiles, inputs.dtype)


        quantile_values = tf.map_fn(lambda x: tfp.stats.percentile(inputs_flat[..., x], quantiles * 100, axis=1, interpolation='linear'), elems=tf.range(channels), dtype=inputs.dtype)

        # quantile_values shape: [channels, num_quantiles, batch_size]

        # output shape is [batch_size, channels, num_quantiles]
        quantile_values = tf.transpose(quantile_values, [2, 0, 1])
        return quantile_values

    def compute_output_shape(self, input_shape):
        out_shape = (input_shape[0], input_shape[-1], self.num_quantiles)
        return out_shape

    @classmethod
    def test_layer(cls):
        l = QuantileLayer(num_quantiles=10)
        x1 = tf.random.normal(shape=(1, 5, 5, 1)) * 10
        x2 = tf.random.normal(shape=(1, 5, 5, 1))
        x = tf.concat([x1, x2], axis=3)
        y = l(x)
        print(y)


class ShuffleLayer(Layer):
    def __init__(self, **kwargs):
        super(ShuffleLayer, self).__init__(**kwargs)

    def call(self, inputs, training=None):
        if training:
            # Shuffle along the batch dimension
            return tf.random.shuffle(inputs)
        else:
            return inputs


class GradientReversalLayer(tf.keras.layers.Layer):
    """
    Useful for adversarial networks.
    """

    def __init__(self, alpha=-1.0, **kwargs):
        super().__init__(**kwargs)
        self.alpha = alpha
        self.is_enabled = True

    def call(self, inputs, *args, **kwargs):
        if self.is_enabled:
            return self.grad_reversal(inputs)
        else:
            return tf.identity(inputs)

    @tf.custom_gradient
    def grad_reversal(self, x):
        identity = tf.identity(x)
        return identity, self.custom_grad

    def custom_grad(self, dy):
        if self.is_enabled:
            return self.alpha * dy
        else:
            return dy

    def enable(self):
        self.is_enabled = True

    def disable(self):
        self.is_enabled = False

    def toggle(self):
        self.is_enabled = not self.is_enabled


class RGBtoHSVLayer(Layer):
    def __init__(self, **kwargs):
        super(RGBtoHSVLayer, self).__init__(**kwargs)

    def call(self, inputs):
        return tf.image.rgb_to_hsv(inputs)


class BestValReduceLRCallback(tf.keras.callbacks.Callback):
    """
    Checks validation loss, if increases, can either reduce learning rate or stop the training.

    Either way, it ends the training with weights of epoch with min validation loss.
    """

    def __init__(self, start_on=1, patience=0, reduce_rate=0.4, min_lr=1e-5, stop_on_incr=False, metric='val_loss', save_best=None):
        super().__init__()
        self.start_on = start_on
        self.patience = patience
        self.reduce_rate = reduce_rate   # closer to 0, faster the reduce rate.
        self.min_lr = min_lr
        self.stop_on_incr = stop_on_incr
        self.metric = metric
        self.save_best = save_best

        self.best_weights = None        # best weights
        self.wait = None                # how much we are waiting (patiently)
        self.best_loss = None           # our best loss thus far
        self.best_epoch = None

    def on_train_begin(self, logs=None):
        self.wait = 0
        self.best_loss = np.Inf

    def on_train_end(self, logs=None):
        if self.save_best and isinstance(self.save_best, str):
            self.model.save(self.save_best)

        elif self.save_best is True:
            self.model.save(xsettings.OUTPUT_PATH.joinpath("best_model.h5"))

    def rollback_to_best(self):
        self.model.set_weights(self.best_weights)

    def on_epoch_end(self, epoch, logs=None):
        current_val_loss = logs.get(self.metric)
        if epoch < self.start_on:
            return

        if np.less(current_val_loss, self.best_loss):
            self.best_loss = current_val_loss
            self.wait = 0
            self.best_weights = self.model.get_weights()            # update model weights
            self.best_epoch = epoch
        else:
            self.wait += 1
            if self.wait >= self.patience:
                # Restoring model weights from the end of the best epoch.
                self.rollback_to_best()

                if self.stop_on_incr:
                    self.model.stop_training = True
                    print(f"\nBestValReduceLRCallback: validation increased, restoring best weights and stopping the training. (best {self.metric}={self.best_loss:.4f}, on epoch={self.best_epoch})")
                    return

                # Reduce learning rate
                lr = float(tf.keras.backend.get_value(self.model.optimizer.lr))
                new_lr = max(lr * self.reduce_rate, self.min_lr)
                if new_lr < lr:
                    tf.keras.backend.set_value(self.model.optimizer.lr, new_lr)
                    print(f"\nBestValReduceLRCallback: Restoring best weights & reduced learning rate to {new_lr:.10f} (best {self.metric}={self.best_loss:.4f}, on epoch={self.best_epoch})")

                else:
                    print(f"\nBestValReduceLRCallback: reached minimum LR, but still not improving val. Restoring best weights & stopping the training. (best {self.metric}={self.best_loss:.4f}, on epoch={self.best_epoch})")
                    self.model.stop_training = True
                    return

                self.wait = 0


@register_keras_serializable()
def mape_loss(y_true, y_pred):
    epsilon = 1e-10  # Small constant to avoid division by zero
    return tf.reduce_mean(tf.abs(100*(y_true - y_pred) / (y_true + epsilon)))
    # return tf.reduce_mean(tf.abs((y_true - y_pred) / y_true))


def triplet_loss(margin=1.0):
    """
    Computes the triplet loss.
    margin: Defines how far apart the negative and positive pairs should be.
    """

    @register_keras_serializable()
    def loss(y_true, y_pred):
        # The output is of size 3 * embedding_dim  [batch_size, embedding_dim, 3]
        anchor, positive, negative = y_pred[:, :, 0], y_pred[:, :, 1], y_pred[:, :, 2]

        # Compute the L2 distance between anchor-positive and anchor-negative
        pos_dist = tf.reduce_sum(tf.square(anchor - positive), axis=-1)
        neg_dist = tf.reduce_sum(tf.square(anchor - negative), axis=-1)

        # Apply the triplet loss function
        loss = tf.maximum(neg_dist - pos_dist + margin, 0.0)
        return tf.reduce_mean(loss)

    return loss


@register_keras_serializable()
def ordinal_crossentropy_loss(y_true, y_pred):
    """
    Ordinal cross-entropy loss for ordinal regression.
    NOTE: NOT TESTED (GPT)

    Parameters:
    - y_true: A tensor of true labels, shape (batch_size, 1),
              where each label is an integer representing the ordinal class.
    - y_pred: A tensor of predicted probabilities, shape (batch_size, N),
              where N is the number of ordinal classes. Each row represents
              the cumulative probability of being in or below a given class.

    Returns:
    - A scalar tensor representing the average loss.
    """
    # Ensure y_pred is cumulative
    y_pred_cumulative = tf.cumsum(y_pred, axis=1)

    # Convert y_true to a binary matrix representation
    y_true_expanded = tf.cast(tf.range(1, tf.shape(y_pred)[1] + 1), dtype=y_true.dtype)
    y_true_expanded = tf.less_equal(y_true_expanded, tf.cast(tf.expand_dims(y_true, -1), y_true_expanded.dtype))
    y_true_expanded = tf.cast(y_true_expanded, dtype=y_pred.dtype)

    # Compute binary cross-entropy loss for each ordinal step
    losses = tf.keras.losses.binary_crossentropy(y_true_expanded, y_pred_cumulative, from_logits=False)

    # Average loss over all ordinal steps
    return tf.reduce_mean(losses)

@register_keras_serializable()
def r_squared(y_true, y_pred):
    SS_res =  K.sum(K.square(y_true - y_pred))
    SS_tot = K.sum(K.square(y_true - K.mean(y_true)))
    return (1 - SS_res/(SS_tot + K.epsilon()))


@register_keras_serializable()
def p_corr(y_true, y_pred):
    """
    Pearson correlation coefficient as a metric.
    """
    # Subtract the mean from both true and predicted values
    y_true_mean_subtracted = y_true - tf.reduce_mean(y_true)
    y_pred_mean_subtracted = y_pred - tf.reduce_mean(y_pred)

    # Calculate the numerator: the dot product of deviations
    numerator = tf.reduce_sum(y_true_mean_subtracted * y_pred_mean_subtracted)

    # Calculate the denominator
    denominator = tf.sqrt(tf.reduce_sum(tf.square(y_true_mean_subtracted))) * tf.sqrt(
        tf.reduce_sum(tf.square(y_pred_mean_subtracted)))

    # Pearson correlation coefficient
    correlation = numerator / denominator

    # To avoid NaN in division, handle cases where denominator is zero
    return tf.where(tf.math.is_nan(correlation), tf.zeros_like(correlation), correlation)
