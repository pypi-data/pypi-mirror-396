from contextlib import contextmanager
import numpy as np
from sklearn.ensemble import _bagging
from scipy import stats, linalg


def testing():
    w_before = [1, 1, 1, 1]
    print(f'before={w_before}, after={adjust_weights_for_weighted_bagging(w_before)}')

    w_before = [1, 1, 1, 3]
    print(f'before={w_before}, after={adjust_weights_for_weighted_bagging(w_before)}')

    with patch_for_weighted_bagging():
        print('hi')

    return


def x_inverse_category_weight(a_cats):
    """
    Given a bunch of sample categories, return the sample weights
    """
    unique, counts = np.unique(a_cats, return_counts=True)
    total_count = len(a_cats)
    weights_for_unique = total_count / counts
    weight_map = dict(zip(unique, weights_for_unique))
    sample_weights = np.vectorize(weight_map.get)(a_cats)
    sample_weights = sample_weights * (len(sample_weights)/sample_weights.sum())

    return sample_weights


def x_inverse_density_weight(a, kde_cov=0.25):
    """
    Given array of values, return the weights as inverse of density
    (higher weights to areas with less values)
    """

    if len(a) <= 2:
        return np.ones(len(a))

    try:
        density = stats.gaussian_kde(a)
    except np.linalg.LinAlgError as e:
        print(f"- WARNING: {repr(e)}")
        return np.ones(len(a))

    density.covariance_factor = lambda: kde_cov
    density._compute_covariance()
    a_density = density(a)
    weights = 1/a_density

    weights = weights * (len(weights) / weights.sum())
    return weights


def x_inverse_hist_weight(a, bins=100):
    """
    Given array of values, return the weights as inverse of histogram (quantile) density
    (higher weights to areas with less values)
    """
    percentiles = np.linspace(0, 100, bins + 1)
    bin_edges = np.percentile(a, percentiles)

    # Calculate the widths of each bin
    bin_widths = np.diff(bin_edges)
    bin_widths = np.maximum(bin_widths, 1e-9)

    bin_weights = bin_widths / bin_widths.sum()

    # Find the indices of the bins to which each element of a belongs
    bin_indices = np.digitize(a, bin_edges, right=True)

    # Ensure bin indices do not exceed the number of bins
    bin_indices[bin_indices > bins] = bins

    # Map bin weights back to the original array elements
    weights = bin_weights[bin_indices - 1]  # subtract 1 because bin_indices are 1-based

    weights = len(a)/weights.sum()*weights

    return weights


def x_adjust_weights_balanced(df, target_col, existing_weight_col=None):
    assert existing_weight_col, "just use 'balanced', no need for this function"

    sums = df[[target_col, existing_weight_col]].groupby(target_col).sum()
    total = sums.sum()

    def adj_weight(r):
        w_init = r[existing_weight_col]
        target = r[target_col]
        w_adj = w_init * (total - sums.loc[target])/total
        return w_adj

    w_adj = df.apply(adj_weight, axis=1)
    return w_adj


def adjust_weights_for_weighted_bagging(weights):
    """
    modifies weights so that after weighted bagging, the final weights have the same effect
    Note: assumes that prob gets activated twice (once in weighted bootstrap, another in model fit)
    p = w / sum(W)   // convert weight to prob
    p_after = p_before * p_before   // convert prob before adj to prob after adj
    """

    weights = np.array(weights)
    weight_sum = weights.sum()
    probs_before = weights / weight_sum
    probs_after = np.sqrt(probs_before)
    weights_after = weight_sum * probs_after
    weights_after = weights_after * (weight_sum/weights_after.sum())
    return weights_after


@contextmanager
def patch_for_weighted_bagging():
    """
    Allows for easy fitting of sklearn.ensemble.BaggingClassifier / sklearn.ensemble.BaggingRegressor
    with *weighted* bootstrapping on sample_weight.
    """

    WeightedBagging.monkey_patch()
    yield
    WeightedBagging.undo_monkey_patch()


class WeightedBagging:
    """
    Allows for easy fitting of sklearn.ensemble.BaggingClassifier / sklearn.ensemble.BaggingRegressor
    with *weighted* bootstrapping on sample_weight.
    """

    _orig__parallel_build_estimators = _bagging._parallel_build_estimators

    @staticmethod
    def monkey_patch():
        _bagging._parallel_build_estimators = WeightedBagging._parallel_build_estimators

    @staticmethod
    def undo_monkey_patch():
        _bagging._parallel_build_estimators = WeightedBagging._orig__parallel_build_estimators

    @staticmethod
    def _parallel_build_estimators(
            n_estimators, ensemble, X, y, sample_weight, seeds, total_n_estimators, verbose
    ):
        """Private function used to build a batch of estimators within a job."""
        # Retrieve settings
        n_samples, n_features = X.shape
        max_features = ensemble._max_features
        max_samples = ensemble._max_samples
        bootstrap = ensemble.bootstrap
        bootstrap_features = ensemble.bootstrap_features
        support_sample_weight = _bagging.has_fit_parameter(ensemble.base_estimator_, "sample_weight")
        if not support_sample_weight and sample_weight is not None:
            raise ValueError("The base estimator doesn't support sample weight")

        # Build estimators
        estimators = []
        estimators_features = []

        for i in range(n_estimators):
            if verbose > 1:
                print(
                    "Building estimator %d of %d for this parallel run (total %d)..."
                    % (i + 1, n_estimators, total_n_estimators)
                )

            random_state = seeds[i]
            estimator = ensemble._make_estimator(append=False, random_state=random_state)

            # Draw random feature, sample indices
            features, indices = WeightedBagging._generate_bagging_indices(
                random_state,
                bootstrap_features,
                bootstrap,
                n_features,
                n_samples,
                max_features,
                max_samples,
                sample_weight,
            )

            # Draw samples, using sample weights, and then fit
            if support_sample_weight:
                if sample_weight is None:
                    curr_sample_weight = np.ones((n_samples,))
                else:
                    curr_sample_weight = sample_weight.copy()

                if bootstrap:
                    sample_counts = np.bincount(indices, minlength=n_samples)
                    curr_sample_weight *= sample_counts
                else:
                    not_indices_mask = ~_bagging.indices_to_mask(indices, n_samples)
                    curr_sample_weight[not_indices_mask] = 0

                estimator.fit(X[:, features], y, sample_weight=curr_sample_weight)

            else:
                estimator.fit((X[indices])[:, features], y[indices])

            estimators.append(estimator)
            estimators_features.append(features)

        return estimators, estimators_features

    @staticmethod
    def _generate_bagging_indices(
            random_state,
            bootstrap_features,
            bootstrap_samples,
            n_features,
            n_samples,
            max_features,
            max_samples,
            sample_weight,
    ):
        """Randomly draw feature and sample indices."""
        # Get valid random state
        random_state = _bagging.check_random_state(random_state)

        # Draw indices
        feature_indices = WeightedBagging._generate_indices(
            random_state, bootstrap_features, n_features, max_features
        )
        sample_indices = WeightedBagging._generate_indices(
            random_state, bootstrap_samples, n_samples, max_samples, sample_weight=sample_weight
        )

        return feature_indices, sample_indices

    @staticmethod
    def _generate_indices(random_state, bootstrap, n_population, n_samples, sample_weight=None):
        """Draw randomly sampled indices."""
        # Draw sample indices
        a_population = np.arange(0, n_population)
        p = None if sample_weight is None else sample_weight/sample_weight.sum()
        indices = random_state.choice(a_population, size=n_samples, replace=bootstrap, p=p)
        return indices


if __name__ == "__main__":
    testing()