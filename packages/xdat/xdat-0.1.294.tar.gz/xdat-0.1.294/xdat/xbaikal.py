from typing import Optional, Dict, Any
import makefun
import inspect
from sklearn.model_selection import cross_val_predict
from baikal import Input, Model, Step
from baikal import make_step as _make_step_orig
from baikal.steps import Lambda, Split, Stack, ColumnStack, Concatenate
from baikal.plot import plot_model

"""
See: https://baikal.readthedocs.io/en/stable/index.html
"""


def make_step_wrapper(base_class: type, attr_dict: Dict[str, Any] = None, class_name: Optional[str] = None) -> type:
    if class_name is None and hasattr(base_class, '__name__'):
        class_name = base_class.__name__

    step_orig = _make_step_orig(base_class, attr_dict=attr_dict, class_name=class_name)
    sig = inspect.signature(base_class)
    step_fixed = makefun.with_signature(sig)(step_orig)
    return step_fixed


assert inspect.signature(_make_step_orig) == inspect.signature(make_step_wrapper)


def make_step(base_class: type, attr_dict: Dict[str, Any] = None, class_name: Optional[str] = None, add_fit_predict=False, cv_pred=None) -> type:
    if add_fit_predict:
        attr_dict = attr_dict if attr_dict else dict()
        if cv_pred is None:
            cv_pred = lambda self, X, y: cross_val_predict(self, X, y, method="predict_proba")

        def fit_predict(self, X, y):
            self.fit(X, y)
            return cv_pred(self, X, y)

        attr_dict['fit_predict'] = fit_predict

    return make_step_wrapper(base_class, attr_dict=attr_dict, class_name=class_name)


if __name__ == "__main__":
    from sklearn import svm

    SVC = make_step(svm.SVC, add_fit_predict=True)
    clf = SVC(C=0.1)
    print('bye')
