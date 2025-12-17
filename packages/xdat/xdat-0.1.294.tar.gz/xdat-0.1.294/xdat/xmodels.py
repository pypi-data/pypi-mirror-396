import inspect
import numpy as np
from sklearn.base import clone, BaseEstimator, RegressorMixin, OutlierMixin
from sklearn.linear_model import QuantileRegressor
from sklearn import metrics, ensemble, neighbors, preprocessing, pipeline, linear_model, decomposition
from scipy.stats import chi2
from munch import Munch as MunchDict
import contextlib
from scipy import optimize
from sklearn.base import ClassifierMixin
from sklearn.utils import resample
from sklearn.isotonic import IsotonicRegression

from . import xnp, xparallel


def x_fit(fit_func, X, y, sample_weight=None, validation_data=None, **fit_params):
    """
    An attempt at a generic "fit" function
    (that supports sklearn, lightgbm, keras, xdat, etc.)
    """
    fit_params = fit_params.copy()
    signature = inspect.signature(fit_func)

    if 'sample_weight' in signature.parameters:
        fit_params['sample_weight'] = sample_weight
    elif sample_weight is not None:
        print('WARNING (x_fit): sample_weight is given, but fit_func() does not accept it.')

    if validation_data is not None:
        if 'validation_data' in signature.parameters:
            # keras, xdat, etc.
            return fit_func(X, y,  validation_data=validation_data, **fit_params)

        if 'eval_set' in signature.parameters:
            # lightgbm
            X_eval, Y_eval, w_eval = validation_data
            eval_set = [[X_eval, Y_eval]]
            return fit_func(X, y, eval_set=eval_set, eval_sample_weight=w_eval, **fit_params)

    return fit_func(X, y, **fit_params)


class ProbabilityEstimatorWrapper(BaseEstimator, ClassifierMixin):
    """
    Given binary classification pipeline, create a better estimation of probabilities:
    - resample the model building process
    - probability calibration (isotonic fit)
    - fit() accepts validation_data=(X, y)
    """

    def __init__(
        self,
        pipeline,
        n_bootstrap=100,
        aggregator="median",
        n_jobs=-1,
    ):
        self.pipeline = pipeline
        self.n_bootstrap = n_bootstrap
        self.aggregator = aggregator
        self.n_jobs = n_jobs

    def fit(self, X, y, sample_weight=None, validation_data=None):
        self.boot_models_ = []

        def get_models(i):
            indices = resample(np.arange(len(X)), replace=True)
            try:
                X_boot, y_boot = X.iloc[indices], y.iloc[indices]
            except AttributeError:
                X_boot, y_boot = X[indices], y[indices]

            # fit the main model
            model_clone = clone(self.pipeline)
            x_fit(model_clone.fit, X_boot, y_boot, sample_weight=sample_weight, validation_data=validation_data)

            if validation_data:
                X_val, y_val, w_val = validation_data
            else:
                X_val, y_val = X_boot, y_boot

            # calibrate the probabilities:
            p_val_raw = model_clone.predict_proba(X_val)[:, 1]
            iso_calibrator = IsotonicRegression(out_of_bounds='clip')
            iso_calibrator.fit(p_val_raw, y_val, sample_weight=sample_weight)
            return model_clone, iso_calibrator

        self.boot_models_ = xparallel.x_on_iter(list(range(self.n_bootstrap)), get_models, different_seeds=True, n_jobs=self.n_jobs, with_tqdm=False)
        return self

    def predict_proba(self, X):
        p_pos = self.predict_stats(X)[self.aggregator]

        p_neg = 1 - p_pos
        return np.column_stack([p_neg, p_pos])

    def predict(self, X):
        probas_agg = self.predict_proba(X)
        return (probas_agg[:, 1] >= 0.5).astype(int)

    def predict_posterior(self, X):
        all_probas = []
        for (model, iso_calibrator) in self.boot_models_:
            p_raw = model.predict_proba(X)[:, 1]
            p_cal = iso_calibrator.transform(p_raw)
            all_probas.append(p_cal)

        all_probas = np.array(all_probas)
        return all_probas

    def predict_stats(self, X, alpha=0.1):
        all_probas = self.predict_posterior(X)

        lower_percentile = (alpha / 2) * 100
        upper_percentile = (1 - alpha / 2) * 100

        lower = np.percentile(all_probas, lower_percentile, axis=0)
        median = np.median(all_probas, axis=0)
        mean = np.mean(all_probas, axis=0)
        upper = np.percentile(all_probas, upper_percentile, axis=0)

        stats = MunchDict()
        stats['lower'] = lower
        stats['median'] = median
        stats['mean'] = mean
        stats['upper'] = upper
        return stats


class MahalanobisNoveltyDetector(BaseEstimator, OutlierMixin):
    def __init__(self, contamination=0.01, add_noise=0.0):
        self.contamination = contamination
        self.add_noise = add_noise
        self.dof = None

    def fit(self, X, y=None):
        X = X.to_numpy().astype(float)
        self.dof = X.shape[1]
        if self.add_noise:
            X += np.random.uniform(low=-1*self.add_noise, high=self.add_noise, size=X.shape)

        self.mean_ = np.mean(X, axis=0)
        self.covariance_ = np.cov(X, rowvar=False)
        self.inverse_covariance_ = np.linalg.inv(self.covariance_)

        # Calculate the threshold based on the contamination parameter
        self.threshold_ = chi2.ppf((1 - self.contamination), df=self.dof)

        return self

    def mahalanobis_distance(self, X):
        diff = X - self.mean_
        md = np.sqrt(np.sum(diff @ self.inverse_covariance_ * diff, axis=1))
        return md

    def predict(self, X):
        X = X.to_numpy()

        distances = self.mahalanobis_distance(X)
        predictions = np.where(distances ** 2 > self.threshold_, 1, -1)
        return predictions

    def score(self, X):
        X = X.to_numpy()
        distances = self.mahalanobis_distance(X)
        score = distances**2
        return score

    def predict_proba(self, X):
        scores = self.score(X)
        scores /= self.threshold_
        p_values = chi2.cdf(scores, self.dof)
        return p_values

    def decision_function(self, X):
        distances = self.mahalanobis_distance(X)
        return distances ** 2 - self.threshold_

    def decision_function2(self, X):
        scores = self.score(X)
        v = (scores - self.threshold_) / self.threshold_
        return v



class CustomFit:
    """
    Fits a custom fit-function on a dataframe
    """
    def __init__(self, param_names, maxiter=1000, loss='rmse'):
        self.param_names = param_names
        self.initial_guess = [0] * len(param_names)
        self.maxiter = maxiter
        self.loss_kind = loss

        self.df_x = None
        self.y = None
        self.params = None

    def clone(self):
        return CustomFit(param_names=self.param_names, maxiter=self.maxiter, loss=self.loss_kind)

    def predict_func(self, params, row):
        """
        This needs to be implemented by the subclass.
        Think of this as the "forward pass"

        Args:
            params: the fitted parameters
            row: the dataframe's row

        Returns: predicted value (float)

        """
        raise NotImplementedError

    def loss(self, params):
        params = MunchDict(zip(self.param_names, params))
        total_err = 0
        for (_, row), true_val in zip(self.df_x.iterrows(), self.y):
            pred_val = self.predict_func(params, row)
            if self.loss_kind == 'rmse':
                err = (true_val - pred_val)**2
            elif self.loss_kind == 'mae':
                err = abs(pred_val / true_val - 1)
            else:
                raise KeyError(self.loss_kind)

            total_err += err

        return total_err

    def transform(self, df):
        """
        A convenience function that can be overwritten
        Transforms the df (returns a new one)
        """
        return df

    def fit(self, df_x, y):
        self.df_x = self.transform(df_x)
        self.y = y
        res = optimize.minimize(self.loss, np.array(self.initial_guess), options={'maxiter': self.maxiter})
        self.params = MunchDict(zip(self.param_names, res.x))

    def predict(self, df_x):
        df_x = self.transform(df_x)
        preds = []
        for _, row in df_x.iterrows():
            pred = self.predict_func(self.params, row)
            preds.append(pred)

        return np.array(preds)


class MultiModelRegressor(BaseEstimator, RegressorMixin):
    def __init__(self, models=None):
        assert models is not None
        self.models = models

    def fit(self, X, y):
        for clf in self.models:
            clf.fit(X, y)
        return self

    def predict(self, X):
        preds = []
        for clf in self.models:
            preds.append(clf.predict(X))

        return np.column_stack(preds)

    def get_params(self, deep=True):
        return {"models": [reg.get_params(deep) for reg in self.models]}

    def set_params(self, **params):
        if 'models' in params:
            self.models = [reg.set_params(**param) for reg, param in zip(self.models, params['models'])]
        return self

class MultiQuantileLinearRegressor(MultiModelRegressor):
    def __init__(self, quantiles=None, alpha=0):
        assert quantiles is not None
        self.quantiles = quantiles
        self.alpha = alpha

        models = []
        for q in quantiles:
            if q == 'mean':
                models.append(linear_model.Ridge(alpha=alpha))
            else:
                models.append(QuantileRegressor(quantile=q, solver='highs', alpha=alpha))

        super().__init__(models=models)

    def get_params(self, deep=True):
        return {'quantiles': self.quantiles, 'alpha': self.alpha}

    def set_params(self, **params):
        if 'quantiles' in params:
            self.quantiles = params['quantile']

        if 'alpha' in params:
            self.quantiles = params['alpha']


class QuantileLinearRegressor(MultiQuantileLinearRegressor):
    def __init__(self, q=0.05, alpha=0):
        assert 0 <= q < 0.5
        self.q = q
        self.alpha = alpha
        quantiles = [q, 'mean', 1-q]
        super().__init__(quantiles)

    def get_params(self, deep=True):
        return {'q': self.q, 'alpha': self.alpha}

    def set_params(self, **params):
        if 'q' in params:
            self.quantiles = params['q']

        if 'alpha' in params:
            self.quantiles = params['alpha']

def _get_clf_with_estimators_(pipe):
    clf = pipe
    if isinstance(clf, pipeline.Pipeline):
        clf = clf[-1]

    if hasattr(clf, 'predict_dist'):
        return clf
    elif hasattr(clf, 'estimators_'):
        return clf

    return None

@contextlib.contextmanager
def _prepare_for_dist(pipe):
    clf = _get_clf_with_estimators_(pipe)
    if not clf:
        raise AttributeError('estimator is missing predict_dist(), probably also missing attribute: estimators_')

    x_add_dist(clf)
    _predict_orig = clf.predict
    clf.predict = clf.predict_dist

    try:
        yield

    finally:
        clf.predict = _predict_orig


def x_add_dist(clf):
    """
    Wraps (a trained) clf that has the attribute estimators_ (think bagging) so that individual predictions can be accessed.

    TODO: add predict_proba_dist()
    """

    def predict_dist(self, X):
        assert hasattr(self, 'estimators_')
        all_y_hat = [est.predict(X) for est in self.estimators_]

        y_dist = np.array(all_y_hat)
        y_dist = y_dist.T
        return y_dist

    clf.predict_dist = lambda X: predict_dist(clf, X)
    return clf


def MonotonicBoostingClassifier(*args, **kwargs):
    return ensemble.HistGradientBoostingClassifier(*args, monotonic_cst=[1, -1], **kwargs)


def prune_rf_monotonic(clf):
    """
    Warning: this overwrites clf
    """
    clf.estimators_ = [prune_tree_monotonic(e) for e in clf.estimators_]
    return clf


def prune_tree_monotonic(tree):
    """
    Credit: https://stackoverflow.com/questions/68506704/prune-sklearn-decision-tree-to-ensure-monotony
    """

    # We will define a traversal algorithm which will scan the nodes and leaves from left to right
    # The traversal is recursive, we declare global lists to collect values from each recursion
    traversal = []  # List to collect traversal steps
    parents = []  # List to collect the parents of the collected nodes or leaves
    is_leaves = []  # List to collect if the collected traversal item are leaves or not

    def is_leaf(tree, node):
        if tree.tree_.children_left[node] == -1:
            return True
        else:
            return False

    # A function to do postorder tree traversal
    def postOrderTraversal(tree, root, parent):
        if root != -1:
            # Recursion on left child
            postOrderTraversal(tree, tree.tree_.children_left[root], root)
            # Recursion on right child
            postOrderTraversal(tree, tree.tree_.children_right[root], root)
            traversal.append(root)  # Collect the name of node or leaf
            parents.append(parent)  # Collect the parent of the collected node or leaf
            is_leaves.append(is_leaf(tree, root))  # Collect if the collected object is leaf

    def positive_ratio(tree):  # The frequency of 1 values of leaves in binary classification tree:
        # Number of samples with value 1 in leaves/total number of samples in nodes/leaves
        return tree.tree_.value[:, 0, 1] / np.sum(tree.tree_.value.reshape(-1, 2), axis=1)

    def min_samples_node(tree, nodes): #Finds the node with the minimum number of samples among the provided list
      #Make a dictionary of number of samples of given nodes, and their index in the nodes list
      samples_dict={tree.tree_.n_node_samples[node]:i for i,node in enumerate(nodes)}
      min_samples=min(samples_dict.keys()) #The minimum number of samples among the samples of nodes
      i_min=samples_dict[min_samples] #Index of the node with minimum number of samples
      return nodes[i_min] #The number of node with the minimum number of samples


    def prune_nonmonotonic(tree): #Prune non-monotonic nodes of a binary classification tree
      while True: #Repeat until monotonicity is sustained
        #Clear the traversal lists for a new scan
        traversal.clear()
        parents.clear()
        is_leaves.clear()
        #Do a post-order traversal of tree so that the leaves will be returned in order from left to right
        postOrderTraversal(tree,0,None)
        #Filter the traversal outputs by keeping only leaves and leaving out the nodes
        leaves=[traversal[i] for i,leaf in enumerate(is_leaves) if leaf == True]
        leaves_parents=[parents[i] for i,leaf in enumerate(is_leaves) if leaf == True]
        pos_ratio=positive_ratio(tree) #List of positive samples ratio of the nodes of binary classification tree
        leaves_pos_ratio=[pos_ratio[i] for i in leaves] #List of positive samples ratio of the traversed leaves
        #Detect the non-monotonic pairs by comparing the leaves side-by-side
        nonmonotone_pairs=[[leaves[i],leaves[i+1]] for i,ratio in enumerate(leaves_pos_ratio[:-1]) if (ratio>=leaves_pos_ratio[i+1])]
        #Make a flattened and unique list of leaves out of pairs
        nonmonotone_leaves=[]
        for pair in nonmonotone_pairs:
          for leaf in pair:
            if leaf not in nonmonotone_leaves:
              nonmonotone_leaves.append(leaf)
        if len(nonmonotone_leaves)==0: #If all leaves show monotonic properties, then break
          break
        #List the parent nodes of the non-monotonic leaves
        nonmonotone_leaves_parents=[leaves_parents[i] for i in [leaves.index(leave) for leave in nonmonotone_leaves]]
        node_min=min_samples_node(tree, nonmonotone_leaves_parents) #The node with minimum number of samples
        #Prune the tree by removing the children of the detected non-monotonic and lowest number of samples node
        tree.tree_.children_left[node_min]=-1
        tree.tree_.children_right[node_min]=-1
      return tree

    return prune_nonmonotonic(tree)


class OrdinalClassifier(BaseEstimator):
    """
    Based on classifier that returns binary probability, builds a bunch of classifiers that together solve the ordinal classifier problem.

    Credits:
      https://www.cs.waikato.ac.nz/~eibe/pubs/ordinal_tech_report.pdf
      https://stackoverflow.com/questions/57561189/multi-class-multi-label-ordinal-classification-with-sklearn
    """

    def __init__(self, clf):
        """
        :param clf: binary classifier with 'predict_proba()'
        """

        self.clf = clf
        self.clfs = {}
        self.unique_class = None

    def fit(self, X, y):
        self.unique_class = np.sort(np.unique(y))
        assert self.unique_class.shape[0] > 2, 'looks like a binary problem'

        for i in range(self.unique_class.shape[0]-1):
            # for each k - 1 ordinal value we fit a binary classification problem
            binary_y = (y > self.unique_class[i]).astype(np.uint8)
            clf = clone(self.clf)
            clf.fit(X, binary_y)
            self.clfs[i] = clf

    def predict_proba(self, X):
        clfs_predict = {k: self.clfs[k].predict_proba(X) for k in self.clfs}
        predicted = []
        for i, y in enumerate(self.unique_class):
            if i == 0:
                # V1 = 1 - Pr(y > V1)
                predicted.append(1 - clfs_predict[i][:,1])
            elif i in clfs_predict:
                # Vi = Pr(y > Vi-1) - Pr(y > Vi)
                 predicted.append(clfs_predict[i-1][:,1] - clfs_predict[i][:,1])
            else:
                # Vk = Pr(y > Vk-1)
                predicted.append(clfs_predict[i-1][:,1])
        return np.vstack(predicted).T

    def predict(self, X):
        return np.argmax(self.predict_proba(X), axis=1)

    def score(self, X, y, sample_weight=None):
        _, indexed_y = np.unique(y, return_inverse=True)
        return metrics.accuracy_score(indexed_y, self.predict(X), sample_weight=sample_weight)


def balanced_PCA(X, round2=1000, **kwargs):
    """
    Build a PCA model in two steps:
    1. Normal PCA
    2. Take a subsample of X based on RMSE, build another PCA
    """

    pca = decomposition.PCA(**kwargs)
    pca.fit(X)
    X_features = pca.transform(X)
    X_hat = pca.inverse_transform(X_features)

    df = pd.DataFrame({
        'X_orig': pd.Series([r for r in X]),
        'X_tr': pd.Series([r for r in X_hat])
    })

    df['rmse'] = df.apply(lambda r: xnp.x_rmse(r.X_orig, r.X_tr), axis=1)
    df = df.sort_values('rmse').reset_index(drop=True)

    if not round2:
        print('Warning: balanced PCA disabled, doing regular PCA')
        return  pca, df

    if isinstance(round2, float):
        round2 = int(len(df)*round2)

    idx = np.linspace(0, len(X)-1, round2).astype(int)
    df['train'] = np.isin(df.index.values, idx)

    X_small = np.vstack(df.iloc[idx].X_orig)

    pca = decomposition.PCA(**kwargs)
    pca.fit(X_small)

    X = np.vstack(df.X_orig)
    X_features = pca.transform(X)
    X_hat = pca.inverse_transform(X_features)

    df['X_tr'] = pd.Series([r for r in X_hat])
    df['rmse'] = df.apply(lambda r: xnp.x_rmse(r.X_orig, r.X_tr), axis=1)

    return pca, df


class KNeighborsMixinTrain(neighbors._base.KNeighborsMixin):
    """
    The problem with KNN is that "training" score is biased (up to perfection) because nearest neighbor is always self. This is remedied by ignoring the nearest neighbor (on the training set only.)
    """

    _orig_kneighbors = neighbors._base.KNeighborsMixin.kneighbors

    def _train_kneighbors(self, X=None, n_neighbors=None, return_distance=True):
        n_neighbors = n_neighbors or self.n_neighbors
        res = self._orig_kneighbors(X, n_neighbors=n_neighbors+1, return_distance=return_distance)
        if return_distance:
            neigh_dist, neigh_ind = res
            neigh_dist = neigh_dist[:, 1:]
            neigh_ind = neigh_ind[:, 1:]
            return neigh_dist, neigh_ind

        neigh_ind = res
        neigh_ind = neigh_ind[:, 1:]
        return neigh_ind

    def fit_predict(self, X, y):
        self.fit(X, y)
        return self.predict_train(X)

    def predict_train(self, X):
        self.kneighbors = self._train_kneighbors
        try:
            return self.predict(X)
        finally:
            self.kneighbors = self._orig_kneighbors

    def predict_proba_train(self, X):
        self.kneighbors = self._train_kneighbors
        try:
            return self.predict_proba(X)
        finally:
            self.kneighbors = self._orig_kneighbors

    def score_train(self, X, y):
        self.kneighbors = self._train_kneighbors
        try:
            return self.score(X, y)
        finally:
            self.kneighbors = self._orig_kneighbors


class KNeighborsClassifierWithTrain(neighbors.KNeighborsClassifier, KNeighborsMixinTrain):
    pass


class KNeighborsRegressorWithTrain(neighbors.KNeighborsRegressor, KNeighborsMixinTrain):
    pass


class WeightedNeighbors:
    """
    KNN can work great when the distance function makes sense.
    But when there are many features, it's not always easy to spot the features that are most relevant. Including unnecessary features will blurr the distance function, making it seem like KNN is not a relevant algo for the task.

    On fit(), this class searches for relevant features and their associated weights.
    """

    def __init__(self, clf, scale=True, max_weight=8, n_iter=100, n_jobs=-1):
        assert isinstance(clf, KNeighborsMixinTrain), "Must used a model with ability to predict on training data"

        self.clf = clf
        self.scale = scale
        self.max_weight = max_weight
        self.n_iter = n_iter
        self.n_jobs = n_jobs
        self.scaler = preprocessing.StandardScaler()
        self.feature_weights = None

    def clone(self):
        clf = WeightedNeighbors(self.clf, scale=self.scale, n_iter=self.n_iter)
        if self.scale:
            clf.scaler = self.scaler.copy()

        clf.feature_weights = self.feature_weights
        return clf

    def _apply_weights(self, X, feature_weights=None):
        feature_weights = feature_weights if feature_weights is not None else self.feature_weights

        idxs = feature_weights > 0
        X = X[:, idxs]

        feature_weights = feature_weights[idxs]
        for idx, w in enumerate(feature_weights):
            X[:, idx] *= w

        return X

    def transform(self, X):
        if self.scale:
            X = self.scaler.transform(X)

        X = self._apply_weights(X)
        return X

    def fit(self, X, y=None):
        import optuna

        if self.scale:
            X = self.scaler.fit_transform(X)

        def objective(trial):
            _X = X.copy()
            weights = []
            for idx in range(X.shape[1]):
                include_p = trial.suggest_int(f"include_{idx}", 0, 1)
                if include_p:
                    weight = trial.suggest_float(f"weight_{idx}", 1, self.max_weight)
                    weights.append(weight)
                else:
                    weights.append(0)

            weights = np.array(weights)
            # print(weights)
            if (weights > 0).sum() == 0:
                return -1*np.inf

            _X = self._apply_weights(_X, feature_weights=weights)

            _clf = clone(self.clf)
            _clf.fit(_X, y=y)

            score = _clf.score_train(_X, y)
            return score

        study = optuna.create_study(direction='maximize')
        study.optimize(objective, n_trials=self.n_iter, n_jobs=self.n_jobs)

        bp = study.best_params.copy()
        weights = []
        for idx in range(X.shape[1]):
            if bp[f'include_{idx}'] == 0:
                weights.append(0)
            else:
                weights.append(bp[f'weight_{idx}'])

        weights = np.array(weights)
        self.feature_weights = weights
        _X = self._apply_weights(X)
        self.clf.fit(_X, y)


if __name__ == "__main__":
    from sklearn.datasets import fetch_california_housing
    import pandas as pd

    housing_data = fetch_california_housing()

    descr = housing_data['DESCR']
    feature_names = housing_data['feature_names']
    data = housing_data['data']
    target = housing_data['target']
    df = pd.DataFrame(dict(zip(feature_names, data.T)))

    # clf = WeightedNeighbors(KNeighborsRegressorWithTrain(), n_iter=1000, n_jobs=-1)
    # clf.fit(df, target)
    # df2 = clf.transform(df)
    # clf2 = KNeighborsRegressorWithTrain()
    # clf2.fit(df2, target)
    # print(clf2.score_train(df2, target))

    df = df[['Latitude', 'Longitude']]
    clf = neighbors.KNeighborsRegressor()
    clf.fit(df, target)
    clf2 = KNeighborsRegressorWithTrain()
    clf2.fit_predict(df, target)
    print(clf2.score_train(df, target))
    # metrics.log_loss(target, clf.predict(df), eps=1e-15)


    print('hi')