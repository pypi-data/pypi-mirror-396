import numpy as np
from collections import Counter
from sklearn.base import BaseEstimator, ClassifierMixin, RegressorMixin


class TreeNode:
    """
    A simple tree node.
    """
    def __init__(self, feature=None, threshold=None, left=None, right=None,
                 value=None, impurity=None, n_samples=None):
        self.feature = feature          # Index of the feature used for splitting
        self.threshold = threshold      # Threshold value for the split
        self.left = left                # Left subtree
        self.right = right              # Right subtree
        self.value = value              # Prediction at leaf node
        self.impurity = impurity        # Impurity value for the node
        self.n_samples = n_samples      # Sum of sample weights (or number of samples)

    def is_leaf(self):
        return self.left is None and self.right is None


class BaseCustomDecisionTree(BaseEstimator):
    """
    Base class for a custom decision tree. Contains common functionality for both
    classification and regression trees.

    Parameters
    ----------
    criterion : string or callable, default=None
        The function to measure the quality of a split. For classification, a string
        like "gini" (default) or "entropy" is supported. For regression, "mse" is supported.
        Alternatively, a custom callable can be provided.

    max_depth : int, default=None
        The maximum depth of the tree. If None, then nodes are expanded until all leaves are pure.

    min_samples_split : int, default=2
        The minimum number of samples required to split an internal node. When using sample weights,
        the sum of weights is used.

    min_samples_leaf : int, default=1
        The minimum number of samples (or sum of weights) required to be at a leaf node.

    max_features : int, default=None
        The number of features to consider when looking for the best split. If None, then all
        features are used.

    random_state : int or None, default=None
        Controls the randomness of the feature selection at splits.

    min_impurity_decrease : float, default=0.0
        A node will be split if this split induces a decrease of the impurity greater than or equal
        to this value.
    """

    def __init__(self,
                 criterion=None,
                 max_depth=None,
                 min_samples_split=2,
                 min_samples_leaf=1,
                 max_features=None,
                 random_state=None,
                 min_impurity_decrease=0.0):
        self.criterion = criterion
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.min_samples_leaf = min_samples_leaf
        self.max_features = max_features
        self.random_state = random_state
        self.min_impurity_decrease = min_impurity_decrease

        self.tree_ = None
        self._rng = np.random.RandomState(random_state) if random_state is not None else np.random

    def fit(self, X, y, sample_weight=None):
        """
        Build the decision tree from the training set (X, y). If sample_weight is provided,
        the tree will use weighted impurity measures.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            The training input samples.

        y : array-like of shape (n_samples,)
            The target values.

        sample_weight : array-like of shape (n_samples,), default=None
            The weights for each sample. If None, then each sample is given equal weight.
        """
        X = np.array(X)
        y = np.array(y)
        if sample_weight is None:
            sample_weight = np.ones_like(y, dtype=float)
        else:
            sample_weight = np.array(sample_weight, dtype=float)
        self.n_features_ = X.shape[1]
        self.tree_ = self._build_tree(X, y, sample_weight, depth=0)
        return self

    def _build_tree(self, X, y, sample_weight, depth):
        """
        Recursively build the tree.
        """
        # Compute weighted impurity at the node.
        node_impurity = self._compute_impurity(y, sample_weight)
        total_weight = sample_weight.sum()

        # Check stopping criteria.
        if (self.max_depth is not None and depth >= self.max_depth) or \
           (total_weight < self.min_samples_split):
            return self._create_leaf(y, sample_weight)

        # Select features to consider (all or a random subset).
        features = np.arange(self.n_features_)
        if self.max_features is not None:
            features = self._rng.choice(features, size=min(self.max_features, self.n_features_), replace=False)

        best_feature, best_threshold, best_gain = None, None, -np.inf
        best_splits = None

        # Try every split for every feature in the subset.
        for feature in features:
            X_feature = X[:, feature]
            thresholds = np.unique(X_feature)
            # Skip if the feature is constant in this node.
            if len(thresholds) == 1:
                continue
            for threshold in thresholds:
                left_mask = X_feature <= threshold
                right_mask = X_feature > threshold
                left_weight = sample_weight[left_mask]
                right_weight = sample_weight[right_mask]
                if left_weight.sum() < self.min_samples_leaf or right_weight.sum() < self.min_samples_leaf:
                    continue
                y_left = y[left_mask]
                y_right = y[right_mask]
                impurity_left = self._compute_impurity(y_left, left_weight)
                impurity_right = self._compute_impurity(y_right, right_weight)
                weighted_impurity = (left_weight.sum() * impurity_left + right_weight.sum() * impurity_right) / total_weight
                gain = node_impurity - weighted_impurity
                if gain > best_gain and gain >= self.min_impurity_decrease:
                    best_gain = gain
                    best_feature = feature
                    best_threshold = threshold
                    best_splits = (X[left_mask], y_left, left_weight,
                                   X[right_mask], y_right, right_weight)

        # If no valid split was found, create a leaf node.
        if best_gain == -np.inf or best_feature is None:
            return self._create_leaf(y, sample_weight)

        # Build subtrees recursively.
        left_subtree = self._build_tree(best_splits[0], best_splits[1], best_splits[2], depth + 1)
        right_subtree = self._build_tree(best_splits[3], best_splits[4], best_splits[5], depth + 1)
        return TreeNode(feature=best_feature,
                        threshold=best_threshold,
                        left=left_subtree,
                        right=right_subtree,
                        impurity=node_impurity,
                        n_samples=total_weight)

    def _create_leaf(self, y, sample_weight):
        """
        Create a leaf node. This method must be implemented by subclasses.
        """
        raise NotImplementedError("_create_leaf must be implemented in subclass.")

    def _compute_impurity(self, y, sample_weight):
        """
        Compute the impurity for the given labels. Must be implemented by subclasses.
        """
        raise NotImplementedError("_compute_impurity must be implemented in subclass.")

    def _traverse_tree(self, x, node):
        """
        Recursively traverse the tree to get a prediction for one sample.
        """
        if node.is_leaf():
            return node.value
        if x[node.feature] <= node.threshold:
            return self._traverse_tree(x, node.left)
        else:
            return self._traverse_tree(x, node.right)

    def predict(self, X):
        """
        Predict target for X.
        """
        X = np.array(X)
        predictions = [self._traverse_tree(x, self.tree_) for x in X]
        return np.array(predictions)

    def _get_leaf_node(self, x, node):
        """
        Recursively traverse the tree and return the leaf node for a given sample.
        """
        if node.is_leaf():
            return node
        if x[node.feature] <= node.threshold:
            return self._get_leaf_node(x, node.left)
        else:
            return self._get_leaf_node(x, node.right)

    def get_leaf_subsets(self, X, y):
        """
        Given the input samples X and targets y, traverse the tree for each sample
        and return a list of tuples (X_subset, y_subset) where each tuple corresponds
        to the data reaching one leaf node.
        """
        X = np.array(X)
        y = np.array(y)
        # Use a dictionary to group indices by leaf node (using id of the node as key)
        leaf_dict = {}
        for idx, (x_sample, y_sample) in enumerate(zip(X, y)):
            leaf_node = self._get_leaf_node(x_sample, self.tree_)
            key = id(leaf_node)
            if key not in leaf_dict:
                leaf_dict[key] = []
            leaf_dict[key].append(idx)
        # Build the list of subsets
        subsets = []
        for indices in leaf_dict.values():
            subsets.append((X[indices], y[indices]))
        return subsets


class CustomDecisionTreeClassifier(BaseCustomDecisionTree, ClassifierMixin):
    """
    A custom decision tree classifier.

    Parameters
    ----------
    criterion : {"gini", "entropy"} or callable, default="gini"
        The function to measure the quality of a split. If a callable is provided, it should
        take the array of labels (and optionally sample weights) at a node and return a float.

    class_weight : dict, "balanced", or None, default=None
        Weights associated with classes. If not None, the sample weights passed to fit()
        will be adjusted by the corresponding class weight for each sample.
        If "balanced", weights will be automatically computed to be inversely proportional
        to class frequencies.
    """
    def __init__(self,
                 criterion="gini",
                 max_depth=None,
                 min_samples_split=2,
                 min_samples_leaf=1,
                 max_features=None,
                 random_state=None,
                 min_impurity_decrease=0.0,
                 class_weight=None):
        super().__init__(criterion=criterion,
                         max_depth=max_depth,
                         min_samples_split=min_samples_split,
                         min_samples_leaf=min_samples_leaf,
                         max_features=max_features,
                         random_state=random_state,
                         min_impurity_decrease=min_impurity_decrease)
        self.class_weight = class_weight

    def fit(self, X, y, sample_weight=None):
        """
        Fit the decision tree classifier. Adjust sample weights based on class_weight if provided.
        """
        X = np.array(X)
        y = np.array(y)
        # Create default sample_weight if not provided.
        if sample_weight is None:
            sample_weight = np.ones_like(y, dtype=float)
        else:
            sample_weight = np.array(sample_weight, dtype=float)

        # Adjust sample weights using class_weight if specified.
        if self.class_weight is not None:
            if self.class_weight == "balanced":
                # Compute weights inversely proportional to class frequencies.
                counts = Counter(y)
                n_samples = len(y)
                n_classes = len(counts)
                weight_dict = {cls: n_samples / (n_classes * count) for cls, count in counts.items()}
            elif isinstance(self.class_weight, dict):
                weight_dict = self.class_weight
            else:
                raise ValueError("class_weight must be 'balanced', a dict, or None")
            sample_weight = np.array([sw * weight_dict[cls] for sw, cls in zip(sample_weight, y)], dtype=float)

        return super().fit(X, y, sample_weight=sample_weight)

    def _compute_impurity(self, y, sample_weight):
        """
        Compute impurity for classification. If a custom callable was provided as criterion,
        use it. Otherwise, use "gini" or "entropy".
        """
        if callable(self.criterion):
            # Assume custom criterion can handle sample_weight.
            return self.criterion(y, sample_weight)
        # If no sample_weight provided, default to equal weights.
        if sample_weight is None:
            sample_weight = np.ones_like(y, dtype=float)
        classes = np.unique(y)
        # Compute weighted counts.
        weighted_counts = np.array([sample_weight[y == cls].sum() for cls in classes])
        proportions = weighted_counts / weighted_counts.sum()
        if self.criterion == "gini":
            impurity = 1 - np.sum(proportions ** 2)
        elif self.criterion == "entropy":
            eps = 1e-10  # small constant to avoid log(0)
            impurity = -np.sum(proportions * np.log(proportions + eps))
        else:
            raise ValueError(f"Unsupported criterion: {self.criterion}")
        return impurity

    def _create_leaf(self, y, sample_weight):
        """
        Create a leaf node for classification by storing the majority class.
        Also stores the class distribution for predict_proba.
        """
        if sample_weight is None:
            sample_weight = np.ones_like(y, dtype=float)
        classes = np.unique(y)
        weighted_counts = {cls: sample_weight[y == cls].sum() for cls in classes}
        # Majority class is the one with maximum weighted count.
        prediction = max(weighted_counts, key=weighted_counts.get)
        leaf = TreeNode(value=prediction, n_samples=sample_weight.sum(),
                        impurity=self._compute_impurity(y, sample_weight))
        leaf.class_counts = weighted_counts
        return leaf

    def predict_proba(self, X):
        """
        Estimate class probabilities for samples in X.
        """
        X = np.array(X)
        proba = []
        for x in X:
            node = self.tree_
            while not node.is_leaf():
                if x[node.feature] <= node.threshold:
                    node = node.left
                else:
                    node = node.right
            total = sum(node.class_counts.values())
            classes = sorted(node.class_counts.keys())
            probs = np.array([node.class_counts.get(cls, 0) / total for cls in classes])
            proba.append(probs)
        return np.array(proba)


class CustomDecisionTreeRegressor(BaseCustomDecisionTree, RegressorMixin):
    """
    A custom decision tree regressor.

    Parameters
    ----------
    criterion : {"mse"} or callable, default="mse"
        The function to measure the quality of a split. If a callable is provided, it should
        take the array of target values (and optionally sample weights) at a node and return a float.
    """
    def __init__(self,
                 criterion="mse",
                 max_depth=None,
                 min_samples_split=2,
                 min_samples_leaf=1,
                 max_features=None,
                 random_state=None,
                 min_impurity_decrease=0.0):
        super().__init__(criterion=criterion,
                         max_depth=max_depth,
                         min_samples_split=min_samples_split,
                         min_samples_leaf=min_samples_leaf,
                         max_features=max_features,
                         random_state=random_state,
                         min_impurity_decrease=min_impurity_decrease)

    def _compute_impurity(self, y, sample_weight):
        """
        Compute impurity for regression. If a custom callable was provided as criterion, use it.
        Otherwise, use the mean squared error (MSE).
        """
        if callable(self.criterion):
            return self.criterion(y, sample_weight)
        if self.criterion == "mse":
            if sample_weight is None:
                mean_y = np.mean(y)
                impurity = np.mean((y - mean_y) ** 2)
            else:
                mean_y = np.average(y, weights=sample_weight)
                impurity = np.average((y - mean_y) ** 2, weights=sample_weight)
        else:
            raise ValueError(f"Unsupported criterion: {self.criterion}")
        return impurity

    def _create_leaf(self, y, sample_weight):
        """
        Create a leaf node for regression by storing the mean target value.
        """
        if sample_weight is None:
            value = np.mean(y)
            weight_sum = len(y)
        else:
            value = np.average(y, weights=sample_weight)
            weight_sum = sample_weight.sum()
        return TreeNode(value=value, n_samples=weight_sum,
                        impurity=self._compute_impurity(y, sample_weight))


if __name__ == "__main__":
    from sklearn.datasets import load_iris, load_diabetes
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, mean_squared_error

    # --- Test the classifier ---
    data = load_iris()
    X, y = data.data, data.target

    # Split the data into training and testing sets.
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Create an instance of our custom decision tree classifier with class_weight.
    clf = CustomDecisionTreeClassifier(max_depth=3, min_samples_split=5, random_state=42,
                                         class_weight="balanced")

    # Fit the classifier on the training data with sample weights.
    sample_weight = np.random.rand(len(y_train))
    clf.fit(X_train, y_train, sample_weight=sample_weight)

    # Predict on the test set.
    y_pred = clf.predict(X_test)

    # Evaluate and print the accuracy.
    acc = accuracy_score(y_test, y_pred)
    print("Classifier Test Accuracy:", acc)

    for Xs, ys in clf.get_leaf_subsets(X_train, y_train):
        print(f'-- len(X)={len(Xs)}')

    # --- Test the regressor ---
    # Note: The regressor only accepts sample_weight in fit().
    # Here we use the Boston housing dataset.
    data_reg = load_diabetes()
    X_reg, y_reg = data_reg.data, data_reg.target

    X_train_reg, X_test_reg, y_train_reg, y_test_reg = train_test_split(X_reg, y_reg, test_size=0.2, random_state=42)

    reg = CustomDecisionTreeRegressor(max_depth=3, min_samples_split=5, random_state=42)
    sample_weight_reg = np.random.rand(len(y_train_reg))
    reg.fit(X_train_reg, y_train_reg, sample_weight=sample_weight_reg)
    y_pred_reg = reg.predict(X_test_reg)
    mse = mean_squared_error(y_test_reg, y_pred_reg)
    print("Regressor Test MSE:", mse)
