from collections import namedtuple
import numpy as np
from scipy import stats, linalg
from sklearn import metrics, base

ModelPredStats = namedtuple("ModelPredStats", ["r2", "r2_adj", "p_value", "corr", "mse", "mae", "mape", "rmse", "p_value_err_normal", "kappa", "matthew", "auc"])


def x_model_pred_stats(y_true, y_pred, y_alt='mean', k=None, y_score=None, is_classification=None):
    """
    Calculates various statistics on model predictions, including:
        p_value: the p_value of the test that the absolute errors of the pred are less than the absolute errors of the alt
        p_value_err_normal: the p_value of the test that the errors are normally distributed
        r2_adj: adjusted r-squared (requires the k parameter to be set)
        y_score: score array for binary (or matrix for multiclass)
        is_classification: True for classification, False for regression

    Args:
        y_true: true values
        y_pred: predicted values
        y_alt: alternative (null) model, typically mean of train data
        k: number of variables in the model (for calculating r2_adj)

    Returns: ModelPredStats
    """
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)

    if is_classification is None:
        unique_vals = np.unique(y_true)
        if len(unique_vals) <= 2 and len(set(unique_vals) - {0, 1, 2, -1}) == 0:
            is_classification = True
        else:
            is_classification = False

    if y_alt == 'mean':
        y_alt = y_true.mean()

    err_pred = np.abs(y_true - y_pred)
    err_alt = np.abs(y_true - y_alt)

    res = stats.ttest_rel(err_pred, err_alt, alternative='less')
    p_value = res.pvalue
    if p_value is np.nan:
        p_value = None

    errors = y_true - y_pred
    p_value_err_normal = None
    try:
        p_value_err_normal = stats.normaltest(errors).pvalue
    except ValueError:
        pass

    if p_value_err_normal is np.nan:
        p_value_err_normal = None

    if not is_classification:
        r2 = metrics.r2_score(y_true, y_pred)
        n = len(y_true)
        r2_adj = None
        if k is not None and n - k - 1 > 0:
            r2_adj = 1 - ((1-r2)*(n-1))/(n-k-1)

        corr = np.corrcoef(y_true, y_pred)[0, 1]
        mse = metrics.mean_squared_error(y_true, y_pred)
    else:
        r2 = r2_adj = corr = mse = None

    kappa = None        # good for multiclass as well
    matthew = None      # good for multiclass as well
    auc = None          # good for multiclass as well  (OvR)
    if is_classification:
        kappa = metrics.cohen_kappa_score(y_true, y_pred)
        matthew = metrics.matthews_corrcoef(y_true, y_pred)
        if y_score is not None:
            if len(y_score.shape) == 2 and y_score.shape[1] == 2:
                y_score = y_score[:, 1]

            if len(y_score.shape) == 1:
                auc = metrics.roc_auc_score(y_true, y_score)
            else:
                auc = metrics.roc_auc_score(y_true, y_score, multi_class='ovr', average='weighted')

    mape = None
    mae = None
    rmse = None

    if not is_classification:
        mae = np.mean(err_pred)
        rmse = metrics.root_mean_squared_error(y_true, y_pred)

        if (y_true > 0).sum() == len(y_true) and (y_pred > 0).sum() == len(y_pred):
            mape = np.mean(err_pred / y_true)

    res = ModelPredStats(r2=r2, r2_adj=r2_adj, p_value=p_value, corr=corr, mse=mse, mae=mae, mape=mape, rmse=rmse, p_value_err_normal=p_value_err_normal, kappa=kappa, matthew=matthew, auc=auc)
    return res


def x_auc_values(a_lower, a_higher):
    assert len(a_lower) > 0
    assert len(a_higher) > 0
    a_true = np.array([0]*len(a_lower) + [1]*len(a_higher))
    a_actual = np.array(a_lower.tolist() + a_higher.tolist())
    auc = metrics.roc_auc_score(a_true, a_actual)
    return auc


class MahalanobisDistance(base.BaseEstimator):
    """
    Credits: https://www.machinelearningplus.com/statistics/mahalanobis-distance/
    """
    def __init__(self):
        super().__init__()
        self.mean = None
        self.cov = None
        self.inv_covmat = None

        # self.post_scaler = preprocessing.StandardScaler()

    def fit(self, X, y=None):
        self.mean = np.mean(X)
        self.cov = np.cov(X.values.T)
        self.inv_covmat = linalg.inv(self.cov)

    def transform(self, X, y=None):
        x_minus_mu = X - self.mean
        left_term = np.dot(x_minus_mu, self.inv_covmat)
        mahal = np.dot(left_term, x_minus_mu.T)
        diag = mahal.diagonal()
        return diag.reshape(-1, 1)

    def fit_transform(self, X, y=None):
        self.fit(X)
        return self.transform(X)


def x_kde(a, kde_cov=0.25, ls=200, a_min_max=None):
    if a_min_max is None:
        a_min, a_max = a.min(), a.max()
    else:
        a_min, a_max = a_min_max

    density = stats.gaussian_kde(a)
    x = np.linspace(a.min(), a.max(), ls)
    density.covariance_factor = lambda: kde_cov
    density._compute_covariance()
    a_density = density(x)
    return x, a_density


def x_kde_mode(a, kde_cov=0.25, ls=200):
    x, a_density = x_kde(a, kde_cov=kde_cov, ls=ls)
    density_mode = a_density.max()
    mode = x[np.argmax(a_density)]
    return mode, density_mode


def x_randomization_test_approx(samples_big, samples_small, n_permutations=10000):
    """
    Perform a one-sided randomization test (approximation) for two independent samples.
    (checks if their means are different)

    Args:
    samples_big (array-like): The first sample (expected larger values).
    samples_small (array-like): The second sample (expected smaller values).
    n_permutations (int): The number of permutations to perform.

    Returns:
    p_value (float): The p-value from the randomization test.  (closer to 0 means more certain that mean of samples_big are not by chance)
    """

    combined_samples = np.concatenate([samples_big, samples_small])
    observed_diff = np.mean(samples_big) - np.mean(samples_small)

    # Count how many times the permuted difference is at least as extreme as the observed difference
    count_extreme_values = 0
    for _ in range(n_permutations):
        np.random.shuffle(combined_samples)

        # Split the permuted dataset into two new samples
        new_samples_big = combined_samples[:len(samples_big)]
        new_samples_small = combined_samples[len(samples_big):]

        # Calculate the difference in means for the new samples
        new_diff = np.mean(new_samples_big) - np.mean(new_samples_small)

        # Check if the permuted difference is as extreme as the observed difference
        if new_diff >= observed_diff:
            count_extreme_values += 1

    # Calculate the p-value
    p_value = count_extreme_values / n_permutations

    return p_value


def x_calc_auc_separation_score(y_true, y_score, directional=False):
    """
    AUC-based separation score.
    - if not directional: 0 --> 1
    - if directional: -1 --> 1
    """

    auc = metrics.roc_auc_score(y_true, y_score)
    sep = 2*(auc - 0.5)
    if not directional:
        sep = abs(sep)

    return sep


def x_robust_z_score(a):
    z = (a - np.median(a)) / stats.median_abs_deviation(a, scale='normal')
    return z


def stouffer_method(pvals, weights=None):
    """
    Combine p-values using Stouffer’s Z-method.
    """
    pvals = np.array(pvals)
    pvals = np.clip(pvals, 0.001, 0.999)

    if weights is None:
        weights = np.ones_like(pvals)
    else:
        weights = np.array(weights)
        if len(weights) != len(pvals):
            raise ValueError("Weights and pvals must have the same length.")

    # Convert each p-value to its corresponding Z-score (for a right-tailed test):
    zscores = stats.norm.ppf(1 - pvals)

    # Compute the weighted sum of Z-scores
    numerator = np.sum(weights * zscores)
    denominator = np.sqrt(np.sum(weights ** 2))

    z_combined = numerator / denominator

    # Convert back to a (right-tailed) p-value
    combined_p = 1 - stats.norm.cdf(z_combined)
    return combined_p


def x_rstd(a):
        return np.std(a) / np.mean(a)


if __name__ == "__main__":
    from sklearn import datasets, ensemble, model_selection
    # from xdat import xproblem
    for loader in [datasets.load_breast_cancer, datasets.load_wine]:
        print(loader.__name__)
        X, y = loader(return_X_y=True)
        X_train, X_test, y_train, y_test = model_selection.train_test_split(X, y, train_size=0.5)
        clf = ensemble.RandomForestClassifier(n_estimators=1, max_depth=3)
        clf.fit(X_train, y_train)
        y_pred = clf.predict(X_test)
        y_score = clf.predict_proba(X_test)
        print(x_model_pred_stats(y_test, y_pred, y_score=y_score))
    print('hi')