"""
Factors Analysis
"""
import numpy as np
from sklearn import model_selection, ensemble
from tqdm import tqdm


class BinaryFactorsAnalysis:
    def __init__(self, clf):
        self.clf = clf

    def fit(self, X):
        self.clf.fit(X)

    def get_W_H(self, X):
        W = self.clf.transform(X)  # rows
        H = self.clf.components_  # cols
        return W, H

    def predict_proba(self, X):
        W, H = self.get_W_H(X)
        X_hat = np.dot(W, H)
        return X_hat

    def predict(self, X, idx_groups=None):
        X_hat = self.predict_proba(X)
        X_pred = np.zeros(shape=X_hat.shape)
        for idx_start, idx_end in idx_groups:
            idx_end += 1

            argmax = X_hat[:, idx_start:idx_end].argmax(axis=1)
            X_pred[:, idx_start:idx_end][np.arange(X_pred.shape[0]), argmax] = 1

        return X_pred


def factors_cv(X, create_clf, n_splits=12, how='predict', idx_groups=None):
    kfold = model_selection.KFold(n_splits=n_splits)
    X_test_hat = np.zeros(shape=X.shape)

    for train_index, test_index in tqdm(kfold.split(X), total=n_splits):
        X_train = X[train_index]
        X_test = X[test_index]

        clf2 = create_clf()
        clf2.fit(X_train)

        f = getattr(clf2, how)
        if idx_groups:
            X_hat = f(X_test, idx_groups=idx_groups)
        else:
            X_hat = f(X_test)

        X_test_hat[test_index] = X_hat

    return X_test_hat
