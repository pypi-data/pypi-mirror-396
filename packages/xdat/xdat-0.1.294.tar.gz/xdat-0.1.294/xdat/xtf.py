import os
import gc
import tensorflow as tf
from tensorflow.keras import backend as K


def use_gpu(use_gpu="auto", mixed_precision=True):
    """
    :param use_gpu: when True, sets up the GPU (and makes sure it's there), False disables GPU, "auto" uses if there
    :param mixed_precision: when True, enables mixed-precision speedup
    """

    physical_devices = tf.config.list_physical_devices('GPU')
    if use_gpu and len(physical_devices):
        print(f"TF version: {tf.__version__}")

        for gpu in physical_devices:
            print("Num GPUs Available: ", len(tf.config.experimental.list_physical_devices('GPU')), ' [ENABLED]')
            try:
                tf.config.experimental.set_memory_growth(gpu, True)
            except RuntimeError:
                pass

        if mixed_precision:
            policy = tf.keras.mixed_precision.Policy('mixed_float16')
            tf.keras.mixed_precision.set_global_policy(policy)

    else:
        print("Num GPUs Available: ", len(tf.config.experimental.list_physical_devices('GPU')), ' [DISABLING]')
        assert not (use_gpu is True)
        os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
        tf.config.set_visible_devices([], "GPU")



_used_gpus = None
def free_memory(shallow=False):
    global _used_gpus
    K.clear_session()

    if shallow:
        gc.collect()
        return

    if _used_gpus is None:
        gpus = tf.config.list_physical_devices('GPU')
        try:
            gpus = [g.name.split(':', maxsplit=1)[-1] for g in gpus]
        except:
            print(f'cannot get GPU names from physical devices: {gpus}')
            gpus = []

        _used_gpus = []
        for gpu in gpus:
            try:
                tf.config.experimental.reset_memory_stats(gpu)
                _used_gpus.append(gpu)
            except Exception as e:
                print(f"Could not reset memory stats for {gpu}: {e}")

    for gpu in _used_gpus:
        tf.config.experimental.reset_memory_stats(gpu)

    gc.collect()
    K.clear_session()
    gc.collect()
