from sklearn import pipeline
from sklearn.utils.validation import has_fit_parameter


def x_pipeline_fit(pipeline, X, y, sample_weight=None):
    fit_params = {}
    if sample_weight is not None:
        for name, step in pipeline.named_steps.items():
            if has_fit_parameter(step, 'sample_weight'):
                fit_params[f'{name}__sample_weight'] = sample_weight

    pipeline._orig__fit(X, y, **fit_params)
    return pipeline


def monkey_patch():
    pipeline.Pipeline._orig__fit = pipeline.Pipeline.fit
    pipeline.Pipeline.fit = x_pipeline_fit