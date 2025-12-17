import numpy as np
import pandas as pd
from collections import namedtuple
from sklearn import model_selection, pipeline, metrics
from sklearn.base import clone, BaseEstimator, TransformerMixin
from sklearn.metrics import roc_curve, accuracy_score
try:
    from glm.glm import GLM
    from glm.simulation import Simulation
except ImportError:
    GLM = Simulation = None

import quantile_forest
import math

from tqdm import tqdm
from joblib import Parallel, delayed
import shap
from . import xutils, xmodels


Metric = namedtuple('Metric', ['name', 'func', 'args'])
METRICS = {
    'AUC': Metric(name='AUC', func=metrics.roc_auc_score, args=['target', 'prob_1']),
    'BAL_ACC': Metric(name="BAL_ACC", func=metrics.balanced_accuracy_score, args=['target', 'pred']),
    'F1': Metric(name="F1", func=metrics.f1_score, args=['target', 'pred']),
    'R2': Metric(name='R2', func=metrics.r2_score, args=['target', 'pred']),
    'MAPE': Metric(name='MAPE', func=metrics.mean_absolute_percentage_error, args=['target', 'pred']),
    'MAE': Metric(name='MAE', func=metrics.mean_absolute_error, args=['target', 'pred']),
    'MSE': Metric(name='MSE', func=metrics.mean_squared_error, args=['target', 'pred']),
    'MSLE': Metric(name='MSLE', func=metrics.mean_squared_log_error, args=['target', 'pred']),

}

for k,v in list(METRICS.items()):
    METRICS[k.lower()] = v


CVSplit = namedtuple("CVSplit", ['df_train', 'df_test', 'df_val', 'df_holdout', 'fold_num'])


def x_add_q_stratify_col(df, on_col, q=10):
    return pd.qcut(df[on_col], q=int(q), labels=False, duplicates='drop').to_numpy()


def cv_split_prep(df, n_splits=12, stratify_on=None, stratify_on_q=None, group_on=None, ts_split_on=None, random_state=None):
    """
    Various ways to split the data
    :param df:
    :param n_splits: eg: 8, 'max:10' (in case of 'max:10', it does as many splits as possible, but at most 10)
    :param stratify_on: a categorical value to stratify on
    :param stratify_on_q: a ratio value ot stratify on (creates quantiles)
    :param group_on: keep same-values together in split
    :param ts_split_on: time-series kind of split
    :return:
    """

    assert not (stratify_on and stratify_on_q), 'only one kind of stratify allowed'
    assert len(df) > 0, "Got an empty frame"

    if ts_split_on:
        assert stratify_on is None
        assert group_on is None
        df = df.sort_values(ts_split_on).reset_index(drop=True)
        groups = None
        y = None
        kfold = model_selection.TimeSeriesSplit(n_splits=n_splits)
        return df, groups, y, kfold, n_splits

    df = df.sample(frac=1., random_state=random_state).reset_index(drop=True)
    groups = df[group_on] if group_on else None
    y = df[stratify_on] if stratify_on else None

    if group_on is None:
        if n_splits == 'max':
            if not stratify_on:
                n_splits = len(df)
            else:
                n_splits = df.value_counts(stratify_on).min()
        elif isinstance(n_splits, str) and n_splits.startswith('max:'):
            max_limit = int(n_splits.split(':')[1])
            if not stratify_on:
                n_splits = min(len(df), max_limit)
            else:
                n_splits = min(df.value_counts(stratify_on).min(), max_limit)

        assert n_splits > 1
        if stratify_on:
            kfold = model_selection.StratifiedKFold(n_splits=n_splits)

        else:
            kfold = model_selection.KFold(n_splits=n_splits)

    else:
        num_groups = len(np.unique(groups))
        if n_splits == 'max':
            n_splits = num_groups
        elif isinstance(n_splits, str) and n_splits.startswith('max:'):
            max_limit = int(n_splits.split(':')[1])
            n_splits = min(num_groups, max_limit)

        n_splits = min(n_splits, num_groups)

        if stratify_on:
            kfold = model_selection.StratifiedGroupKFold(n_splits=n_splits)

        else:
            kfold = model_selection.GroupKFold(n_splits=n_splits)

    if stratify_on_q:
        group_size = 1
        if group_on:
            group_size = np.floor(df.groupby(group_on).size().quantile(0.8))

        quantiles = np.floor(np.floor(len(df) / group_size) / n_splits)
        y = x_add_q_stratify_col(df, stratify_on_q, q=quantiles)

    return df, groups, y, kfold, n_splits


def cv_split(df, n_splits=12, stratify_on=None, stratify_on_q=None, group_on=None, ts_split_on=None, val_size=0, holdout_size=0, random_state=None):
    """
    Various ways to split the data for cross validation
    :param df: input dataframe
    :param n_splits: eg: 8, 'max:10' (in case of 'max:10', it does as many splits as possible, but at most 10)
    :param val_size: eg 5. How much to take from training set in order to create validation.  This is a number of splits.  (5=20%, 4=25%, 10=10%, etc)
    :param holdout_size: eg 10, "max:10".  How much to take from entire set as a holdout set. This is a number of splits. (5=20%, 4=25%, 10=10%, etc).
    :param stratify_on: a categorical value to stratify on
    :param stratify_on_q: a ratio value ot stratify on (creates quantiles -- less accurate, but much faster)
    :param group_on: keep same-values together in split
    :param ts_split_on: time-series kind of split
    :return: iterates over all the splits
    """
    df_holdout = None
    if holdout_size:
        dfh, groups, y, kfold, n_hsplits = cv_split_prep(df, n_splits=holdout_size, stratify_on=stratify_on, stratify_on_q=stratify_on_q, group_on=group_on, ts_split_on=ts_split_on, random_state=random_state)
        target_size = int(len(df)/n_hsplits)
        folds = [(len(test_index), train_index, test_index) for (train_index, test_index) in kfold.split(df, y=y, groups=groups)]
        folds = sorted(folds)
        best_fold = folds[0]
        for fold in folds:
            if fold[0] > target_size:
                break
            best_fold = fold

        _, train_index, test_index = best_fold
        df = dfh.iloc[train_index].reset_index(drop=True)               # new dataset
        df_holdout = dfh.iloc[test_index].reset_index(drop=True)        # holdout dataset

        df = df.reset_index(drop=True)
        df_holdout = df_holdout.reset_index(drop=True)

    df, groups, y, kfold, n_splits = cv_split_prep(df, n_splits=n_splits, stratify_on=stratify_on, stratify_on_q=stratify_on_q, group_on=group_on, ts_split_on=ts_split_on, random_state=random_state)

    for fold_num, (train_index, test_index) in enumerate(kfold.split(df, y=y, groups=groups), start=1):
        df_train = df.iloc[train_index].reset_index(drop=True)
        df_test = df.iloc[test_index].reset_index(drop=True)
        df_val = None
        df_holdout_split = df_holdout.copy() if df_holdout is not None else None

        if val_size:
            assert isinstance(val_size, int), "needs to be the number of splits"
            val_split = train_test_split(df_train, n_splits=val_size, stratify_on=stratify_on, stratify_on_q=stratify_on_q, group_on=group_on, ts_split_on=ts_split_on, random_state=random_state)
            df_train, df_val = val_split.df_train, val_split.df_test

        yield CVSplit(df_train=df_train, df_test=df_test, df_val=df_val, df_holdout=df_holdout_split, fold_num=fold_num)


def train_test_split(df, n_splits=12, stratify_on=None, stratify_on_q=None, group_on=None, ts_split_on=None, val_size=0, random_state=None):
    """
    Various ways to create train, [optional val], and test splits.  (based on cv_split)
    :param df: input dataframe
    :param n_splits: instead of test size in terms of percentage, use splits.  (5=20%, 4=25%, 10=10%, etc)
    :param val_size: eg 5. How much to take from training set in order to create validation.  This is a number of splits.  (5=20%, 4=25%, 10=10%, etc)
    :param stratify_on: a categorical value to stratify on
    :param stratify_on_q: a ratio value ot stratify on (creates quantiles -- less accurate, but much faster)
    :param group_on: keep same-values together in split
    :param ts_split_on: time-series kind of split
    :return: a single split (train/val/test) of the data
    """

    for split in cv_split(df, n_splits=n_splits, stratify_on=stratify_on, stratify_on_q=stratify_on_q, group_on=group_on, ts_split_on=ts_split_on, val_size=val_size, random_state=random_state):
        return split

CVFold = namedtuple("CVFold", ['clf', 'df_train', 'df_test', 'feature_names', 'df_val', 'tm', 'xym'])


class TargetManipulation:
    def __init__(self, kind=None):
        assert kind in [None, 'log'], kind
        self.kind = kind

    def __repr__(self):
        return f"<TargetManipulation kind={self.kind}>"

    def pre(self, y):
        if self.kind is None:
            return y
        elif self.kind == 'log':
            return np.log(y)

    def post(self, y):
        if self.kind is None:
            return y
        elif self.kind == 'log':
            return np.e**y


class XYManipulation:
    def __init__(self, as_numpy=False, framework='sklearn'):
        self.as_numpy = as_numpy
        self.framework = framework

    def transform(self, X, y=None):
        if self.as_numpy:
            X = X.to_numpy()
            if y is not None:
                y = y.to_numpy()

        if self.framework == 'py-glm':
            intercept = np.ones([X.shape[0], 1])
            X = np.concatenate([intercept, X], axis=1)

        if y is None:
            return X

        return X, y


def train_cv(df, target_col, clf, n_splits='max:12', stratify_on=None, stratify_on_q=None, group_on=None, ordered_split=False, ts_split_on=None, del_cols=tuple(), feature_cols=tuple(), uid_col=None, sample_weight_col=None, eval_size=0.0, framework='auto', fit_params=None, post_fit=None, target_manipulation=None, with_confidence=False, with_q=None, with_tqdm=True, as_numpy=False, pred_col_prefix='', n_jobs=1):
    # fix feature names...
    df.columns = [str(c) if isinstance(c, str) else c for c in df.columns]
    assert not (del_cols and feature_cols), "should only specify features or del columns"
    assert framework in ['auto', 'sklearn', 'lightgbm', 'py-glm'], framework

    pred_col = f"{pred_col_prefix}pred"
    prob_1_col = f"{pred_col_prefix}prob_1"
    all_probs_col = f"{pred_col_prefix}all_probs"
    pred_conf_col = f"{pred_col_prefix}pred_conf"
    fold_num_col = f"{pred_col_prefix}fold_num"

    if framework == 'auto':
        clf2 = clf
        if isinstance(clf2, pipeline.Pipeline):
            clf2 = clf2[-1]

        if GLM is not None and isinstance(clf2, GLM):
            framework = 'py-glm'
        elif isinstance(clf2, quantile_forest.RandomForestQuantileRegressor):
            framework = 'qforest'
        elif isinstance(clf2, xmodels.QuantileLinearRegressor):
            framework = 'qlr'
        else:
            framework = 'sklearn'

    if eval_size:
        assert framework in ['lightgbm'], "need to specify proper framework param"
    else:
        eval_type = None

    if framework == 'py-glm':
        as_numpy = True

    quantiles = None
    if with_q:
        assert framework == 'qforest', "quantiles only work with quantile_forest"
        assert 0 <= with_q < 0.5, with_q
        quantiles = [with_q, 'mean', 1.0 - with_q]

    keep_cols = None
    if feature_cols:
        keep_cols = list(feature_cols) + [target_col]

    fit_params = dict() if fit_params is None else fit_params

    del_cols = set(del_cols)
    if uid_col:
        del_cols.add(uid_col)
    if sample_weight_col:
        del_cols.add(sample_weight_col)
    del_cols = sorted(del_cols)

    xym = XYManipulation(as_numpy=as_numpy, framework=framework)
    tm = TargetManipulation(target_manipulation)

    def calc_fold(fold_num, split_data: CVSplit):
        try:
            clf_fold = clone(clf)
        except TypeError:
            clf_fold = clf.clone()

        df_train = split_data.df_train
        df_train_data = df_train.copy()
        df_val = split_data.df_val
        df_val_data = None
        if df_val is not None:
            df_val_data = df_val.copy()

        df_test = split_data.df_test
        df_test_data = df_test.copy()
        test_tmp_uid = df_test[uid_col] if uid_col else None
        sample_weight_train = df_train[sample_weight_col] if sample_weight_col else None
        sample_weight_eval = df_val[sample_weight_col] if sample_weight_col and df_val is not None else None

        if ordered_split:
            assert group_on, 'group_on must be specified with ordered_split'
            assert n_splits == 'max', "ordered_split won't work well unless n_splits == 'max'"
            test_group = df_test[group_on].min()
            df_train = df_train[df_train[group_on] < test_group].reset_index(drop=True)
            assert (df_train[group_on] >= test_group).sum() == 0
            if len(df_train) == 0:
                return

        if del_cols:
            df_train_data = df_train.drop(columns=del_cols, errors='ignore')
            df_test_data = df_test.drop(columns=del_cols, errors='ignore')
            if df_val_data is not None:
                df_val_data = df_val_data.drop(columns=del_cols, errors='ignore')

        if keep_cols:
            df_train_data = df_train[keep_cols].copy()
            df_test_data = df_test[keep_cols].copy()
            if df_val_data is not None:
                df_val_data = df_val_data[keep_cols].copy()

        X_train, y_train = xutils.split_X_y(df_train_data, target_col)
        feature_names = X_train.columns
        y_train = tm.pre(y_train)
        X_train, y_train = xym.transform(X_train, y_train)

        X_eval, Y_eval = None, None
        if df_val_data is not None:
            X_eval, Y_eval = xutils.split_X_y(df_val_data, target_col)
            Y_eval = tm.pre(Y_eval)

        validation_data = (X_eval, Y_eval, sample_weight_eval) if df_val is not None else None
        xmodels.x_fit(clf_fold.fit, X_train, y_train, sample_weight=sample_weight_train, validation_data=validation_data)

        if post_fit is not None:
            clf_fold = post_fit(clf_fold)

        def capture_predict(df, X):
            if framework == 'qforest':
                qs = []
                for q in quantiles:
                    pred_q = clf_fold.predict(X, q).reshape(-1, 1)
                    qs.append(pred_q)

                pred = np.concatenate(qs, axis=1)
            else:
                pred = clf_fold.predict(X)

            pred = tm.post(pred)

            if framework == 'qforest':
                df[pred_col] = pred[:, 1]
                df[f"{pred_col}_low"] = pred[:, 0]
                df[f"{pred_col}_high"] = pred[:, 2]
            elif framework == 'qlr':
                df[pred_col] = pred[:, 1]
                df[f"{pred_col}_low"] = pred[:, 0]
                df[f"{pred_col}_high"] = pred[:, 2]
            elif len(pred.shape) == 1:
                df[pred_col] = pred
            elif len(pred.shape) == 2:
                df[pred_col] = pred.tolist()
            else:
                raise NotImplementedError(f"pred shape: {pred.shape}")

        def capture_predict_proba(df, X):
            if hasattr(clf_fold, "predict_proba"):
                all_probs = clf_fold.predict_proba(X)
                if len(all_probs.shape) == 1:   # flat prediction
                    prob_1 = all_probs
                elif all_probs.shape[1] == 1:  # 1d pred
                    prob_1 = all_probs[:, 0]
                elif all_probs.shape[1] == 2:   # 2d pred
                    prob_1 = all_probs[:, 1]
                else:                           # multi-d pred
                    prob_1 = all_probs.max(axis=1)
                    df[all_probs_col] = all_probs.tolist()

                df[prob_1_col] = prob_1

        capture_predict(df_train, X_train)
        capture_predict_proba(df_train, X_train)

        if eval_type:
            pred_eval = clf_fold.predict(X_eval)
            df_val[pred_col] = tm.post(pred_eval)
            if hasattr(clf_fold, "predict_proba"):
                prob_1 = clf_fold.predict_proba(X_eval)[:, 1]
                df_val[prob_1_col] = prob_1

        X_test, y_test = xutils.split_X_y(df_test_data, target_col)
        X_test, y_test = xym.transform(X_test, y_test)

        capture_predict(df_test, X_test)
        capture_predict_proba(df_test, X_test)

        if with_confidence:
            with xmodels._prepare_for_dist(clf_fold):
                df_train[pred_conf_col] = clf_fold.predict(X_train).tolist()
                df_test[pred_conf_col] = clf_fold.predict(X_test).tolist()
                if df_val is not None:
                    df_val[pred_conf_col] = clf_fold.predict(X_eval).tolist()

        df_test[fold_num_col] = fold_num
        if uid_col:
            df_test[uid_col] = test_tmp_uid

        fold = CVFold(clf=clf_fold, df_train=df_train, df_test=df_test, feature_names=feature_names, df_val=df_val, tm=tm, xym=xym)

        return fold

    _, _, _, _, total = cv_split_prep(df, n_splits=n_splits, stratify_on=stratify_on, stratify_on_q=stratify_on_q, group_on=group_on, ts_split_on=ts_split_on)
    splits = cv_split(df, n_splits=n_splits, stratify_on=stratify_on, stratify_on_q=stratify_on_q, group_on=group_on, ts_split_on=ts_split_on, val_size=eval_size)

    if with_tqdm:
        tqdm_splits = tqdm(enumerate(splits), total=total)
    else:
        tqdm_splits = enumerate(splits)

    if n_jobs == 1:
        all_folds = [calc_fold(fold_num, split_data) for fold_num, split_data in tqdm_splits]

    else:
        all_folds = Parallel(n_jobs=n_jobs)(delayed(calc_fold)(fold_num, split_data) for fold_num, split_data in tqdm_splits)

    all_folds = [fold for fold in all_folds if fold is not None]

    df_test = pd.concat([i[2] for i in all_folds], ignore_index=True)
    df_test = df_test.reset_index(drop=True)
    return df_test, all_folds


def eval_test(df_test, eval_per=None, metric_list=None, target_col='target', pred_col='pred', prob_1_col='prob_1'):
    """

    :type metrics: list[Metric|str]
    """

    lookup = {'target': target_col, 'pred': pred_col, 'prob_1': prob_1_col}

    df_test = df_test.copy()
    df_test['none'] = 'none'
    df_test['all'] = 'all'

    metric_list = [m if isinstance(m, Metric) else METRICS[m] for m in metric_list]

    if not isinstance(eval_per, list) and not isinstance(eval_per, tuple):
        eval_per = [eval_per]

    rows = []
    for curr_group in eval_per:
        if not curr_group:
            curr_group = 'none'

        for gval in df_test[curr_group].unique():
            df_g = df_test[df_test[curr_group] == gval]
            row = {m.name: m.func(*(df_g[lookup[arg]] for arg in m.args)) for m in metric_list}
            row['cv_grouping'] = curr_group
            row['cv_group_key'] = str(gval)
            row['cv_group_size'] = len(df_g)
            rows.append(row)

    df_res = pd.DataFrame(rows)
    return df_res


def calc_feature_importances(folds, flat=False, use_shap=False):
    """
    If use_shap=True, compute mean(|SHAP|) per feature for each fold.
    Otherwise, use model-native feature_importances_ / coef_.

    Notes:
      - Expects each fold to have `feature_names`.
      - For SHAP, it also needs some data on the fold (tries X_valid/X_val/X_test/X_train/X).
    """
    rows = []
    fi_var = None

    for fold in folds:
        model = fold.clf  # keep full pipeline if present (useful for SHAP in some cases)

        if use_shap:
            X = fold.df_test[fold.feature_names]

            # If it's a Pipeline, transform X to the estimator input space so that
            # fold.feature_names (often post-transform names) line up.
            estimator = model
            X_in = X
            if isinstance(model, pipeline.Pipeline):
                pre = model[:-1]
                estimator = model[-1]
                try:
                    X_in = pre.transform(X)
                except Exception:
                    # Fall back to using the whole pipeline directly (works for some explainers/models)
                    estimator = model
                    X_in = X

            explainer = shap.Explainer(estimator, X_in)
            shap_values = explainer(X_in)

            # Handle (n_samples, n_features) or (n_samples, n_features, n_outputs)
            sv = shap_values.values
            if sv is None:
                raise RuntimeError("SHAP explainer returned no values.")
            sv = np.asarray(sv)
            if sv.ndim == 3:
                # average over outputs (e.g., multiclass)
                sv = np.mean(np.abs(sv), axis=2)
            else:
                sv = np.abs(sv)

            fi = sv.mean(axis=0).flatten()
            fi_dict = dict(zip(fold.feature_names, fi))

        else:
            clf = model
            if isinstance(clf, pipeline.Pipeline):
                clf = clf[-1]

            if fi_var is None:
                for var in ("feature_importances_", "coef_"):
                    if hasattr(clf, var):
                        fi_var = var
                        break
                if not fi_var:
                    print("calc_feature_importances: Can't find attr in clf")
                    return

            fi = np.asarray(getattr(clf, fi_var)).flatten()
            fi_dict = dict(zip(fold.feature_names, fi))

        if flat:
            for k, v in fi_dict.items():
                rows.append({"feature_name": k, "feature_importance": float(v)})
        else:
            rows.append(fi_dict)

    df = pd.DataFrame(rows)

    # Only the "flat" shape has a 'feature_importance' column
    if flat and "feature_importance" in df.columns:
        df["feature_importance"] = np.abs(df["feature_importance"])

    return df

class ModelEnsemble:
    """
    To use with predict_dist(), have two options:
      1. Use any estimator, and the distribution is that of the different folds
      2. Use an estimator that has an 'estimators_' attribute (see xmodels.x_add_dist())
        (it's ok if it's at the end of a pipeline)
        In this case, all the sub-estimators will be called separately.

    """
    def __init__(self, all_folds, is_binary=True):
        self.is_binary = is_binary
        self.clfs = [f.clf for f in all_folds]

        fold0 = all_folds[0]
        assert isinstance(fold0, CVFold)
        self.tm = fold0.tm
        if is_binary:
            assert self.tm.kind is None, "can't do target manipulation with binary"

        self.xym = fold0.xym
        self.feature_names = fold0.feature_names

        self.with_bagging = xmodels._get_clf_with_estimators_(self.clfs[0]) is not None

    def prepare_X(self, df):
        df = df[self.feature_names].copy()
        df.columns = [str(c) if isinstance(c, str) else c for c in df.columns]

        df = self.xym.transform(df)
        return df

    def predict_quantiles(self, X, q=None):
        if q is not None:
            assert 0 <= q < 0.5
            X['pred'] = self.predict(X)
            X['pred_low'] = self.predict_quantile(X, q=q)
            X['pred_high'] = self.predict_quantile(X, q=(1-q))
        else:
            Y = self.predict_dist(X, with_bagging=False)
            X['pred'] = Y[:, 1, :].mean(axis=1)
            X['pred_low'] = Y[:, 0, :].min(axis=1)
            X['pred_high'] = Y[:, 2, :].max(axis=1)

        return X

    def predict_quantile(self, X, q=0.05):
        Y = self.predict_dist(X, q, with_bagging=False)

        if q < 0.5:
            Y = Y.min(axis=1)
        elif q == 0.5:
            Y = np.median(Y, axis=1)
        else:
            Y = Y.max(axis=1)

        return Y

    def predict(self, X):
        Y = self.predict_dist(X, with_bagging=False)

        if self.is_binary:
            pred = [np.bincount(y).argmax() for y in Y]
        else:
            pred = [np.mean(y) for y in Y]

        pred = np.array(pred)
        return pred

    def predict_binary(self, X, threshold=0.5):
        prob_1 = self.predict_proba(X)[:, 1]
        pred = prob_1 >= threshold
        return pred.astype(int)

    def predict_proba(self, X):
        y = self.predict_proba_dist(X, with_bagging=False)
        proba = y.mean(axis=2)
        return proba

    def _predict_x_dist(self, func_name, X, *args, with_bagging=None, axis=-1, **kwargs):
        with_bagging = with_bagging if with_bagging is not None else self.with_bagging
        X = self.prepare_X(X)

        if not with_bagging:
            all_y = [getattr(clf, func_name)(X, *args, **kwargs) for clf in self.clfs]

        else:
            all_y = []
            for clf in self.clfs:
                with xmodels._prepare_for_dist(clf):
                    all_y.append(getattr(clf, func_name)(X, *args, **kwargs).T)

            all_y = [y for l in all_y for y in l]

        if axis == -1:
            axis = len(all_y[0].shape)

        all_y = [y.reshape(y.shape + (1,)) for y in all_y]

        y = np.concatenate(all_y, axis=axis)

        if not self.is_binary:
            y = self.tm.post(y)

        return y

    def predict_proba_dist(self, X, with_bagging=None):
        return self._predict_x_dist('predict_proba', X, with_bagging=with_bagging, axis=2)

    def predict_dist(self, X, *args, with_bagging=None, **kwargs):
        return self._predict_x_dist('predict', X, with_bagging=with_bagging, axis=-1)

    def predict_confidence_deprecated(self, X, n_sim=1000, as_list=True):
        assert self.xym.framework == 'py-glm'
        X = self.prepare_X(X)

        num_per_clf = math.ceil(n_sim / len(self.clfs))
        all_clfs = []
        for clf in self.clfs:
            sim = Simulation(clf)

            new_clfs = sim.parametric_bootstrap(X, n_sim=num_per_clf)
            all_clfs.extend(new_clfs)

        all_y = [clf.predict(X) for clf in all_clfs]
        all_y = [a for a in all_y if np.isnan(a).sum() == 0]
        all_y = [self.tm.post(a) for a in all_y]
        all_y = [y.reshape(y.shape + (1,)) for y in all_y]
        y = np.concatenate(all_y, axis=1)

        if as_list:
            y = [i for i in y]
        return y


class ModelCVEnsembleBuilder(ModelEnsemble):
    """
    Builds an ensemble of models vs CV
    """

    def __init__(self):
        super().__init__(None)

        self.target_col = None
        self.uid_col = None
        self.del_cols = None
        self.df_train = None
        self.df_test = None
        self.df_eval = None
        self.all_folds = None

    def fit(self, df, target_col, clf, n_splits=12, stratify_on=None, group_on=None, ordered_split=False, del_cols=tuple(), uid_col=None, sample_weight_col=None, eval_size=0.0, eval_type=None, fit_params=None, with_tqdm=True, n_jobs=1):
        self.target_col = target_col
        self.uid_col = uid_col
        self.del_cols = del_cols
        self.df_test, self.all_folds = train_cv(df, target_col, clf, n_splits=n_splits, stratify_on=stratify_on, group_on=group_on, ordered_split=ordered_split, del_cols=del_cols, uid_col=uid_col, sample_weight_col=sample_weight_col, eval_size=eval_size, eval_type=eval_type, fit_params=fit_params, with_tqdm=with_tqdm, n_jobs=n_jobs)

        self.clfs = [f.clf for f in self.all_folds]

    def eval_cv_test(self, eval_per=None, metric_list=None):
        self.df_eval = eval_test(self.df_test, eval_per=eval_per, metric_list=metric_list)
        return self.df_eval

    def _transform(self, df):
        del_cols = list({self.target_col} | {self.uid_col} | set(self.del_cols))
        del_cols = [c for c in del_cols if c is not None]
        df2 = df.drop(columns=del_cols).copy()
        return df2

    def predict(self, X):
        X2 = self._transform(X)
        return super().predict(X2)

    def predict_proba(self, X):
        X2 = self._transform(X)
        return super().predict_proba(X2)


class BestThresholdRescaler(BaseEstimator, TransformerMixin):
    """
    Finds the threshold that maximizes accuracy, then defines a monotone linear rescaling of scores such that:
      - best threshold --> 0.5
      - scores are mapped into [0, 1] (with clipping)
    """

    def __init__(self):
        # will be set in fit()
        self.best_thr_ = None
        self.lo_ = None
        self.hi_ = None
        self.best_scaled_ = None
        self.a_ = None

    def fit(self, y_true, y_scores):
        y_true = np.asarray(y_true)
        y_scores = np.asarray(y_scores)

        # --- 1. Find best threshold (max accuracy over ROC thresholds) ---
        fpr, tpr, thr = roc_curve(y_true, y_scores)
        accs = [accuracy_score(y_true, y_scores >= t) for t in thr]
        self.best_thr_ = thr[np.argmax(accs)]

        # --- 2. Store basic stats for rescaling ---
        self.lo_ = float(np.min(y_scores))
        self.hi_ = float(np.max(y_scores))

        # Degenerate case: all scores equal
        if self.hi_ == self.lo_:
            # nothing to compute; transform() will just return 0.5
            self.best_scaled_ = 0.5
            self.a_ = 0.0
            return self

        # First scale to [0,1]
        # scaled = (y_scores - lo) / (hi - lo)
        # best_scaled is where the best threshold lands in that space
        self.best_scaled_ = (self.best_thr_ - self.lo_) / (self.hi_ - self.lo_)

        # Choose a global linear factor 'a' so that:
        #   y' = (scaled - best_scaled) * a + 0.5
        # stays in [0,1] for scaled in [0,1].
        # This requires:
        #   0.5 - a*best_scaled >= 0   (for scaled=0)
        #   0.5 + a*(1 - best_scaled) <= 1   (for scaled=1)
        # =>
        #   a <= 0.5 / best_scaled                (if best_scaled > 0)
        #   a <= 0.5 / (1 - best_scaled)          (if best_scaled < 1)
        # choose the min of the valid ones
        if self.best_scaled_ > 0:
            a1 = 0.5 / self.best_scaled_
        else:
            a1 = np.inf

        if self.best_scaled_ < 1:
            a2 = 0.5 / (1.0 - self.best_scaled_)
        else:
            a2 = np.inf

        self.a_ = float(min(a1, a2))

        return self

    def transform(self, y_scores):
        y_scores = np.asarray(y_scores)

        # If all scores were equal during fit, map everything to 0.5
        if self.hi_ == self.lo_ or self.a_ == 0.0:
            return np.full_like(y_scores, 0.5, dtype=float)

        # Scale using training lo_/hi_
        scaled = (y_scores - self.lo_) / (self.hi_ - self.lo_)

        # Linear, strictly increasing map:
        # y' = (scaled - best_scaled) * a + 0.5
        y_rescaled = (scaled - self.best_scaled_) * self.a_ + 0.5

        # Clip to [0,1] in case new scores are outside the original [lo_, hi_]
        y_rescaled = np.clip(y_rescaled, 0.0, 1.0)

        return y_rescaled

    def fit_transform(self, y_true, y_scores):
        return self.fit(y_true, y_scores).transform(y_scores)
