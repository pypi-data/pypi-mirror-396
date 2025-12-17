from contextlib import contextmanager
import datetime as dt
import pandas as pd
import seaborn as sns
import numpy as np
import arviz as az
import math

from sklearn import linear_model
from sklearn import metrics
from scipy import stats
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
from matplotlib.pyplot import subplots
import matplotlib
from matplotlib.colors import to_rgba
from matplotlib.colors import to_rgb
from matplotlib.lines import Line2D
try:
    import cv2
except ImportError:
    pass

from ds_utils.metrics import plot_confusion_matrix as _plot_confusion_matrix, visualize_accuracy_grouped_by_probability
from sklearn.tree import plot_tree
from venn import venn
from mlxtend import plotting as mlxtend_plotting
from pandas.plotting import parallel_coordinates
import mpld3
import mpld3.plugins as mpld3_plugins
from scriptine import path
from bidi.algorithm import get_display as fix_rtl_bidi
import matplotlib.font_manager
from munch import Munch as MunchDict

from . import xproblem, xpd, xsettings, xcalc, xstats, xpptx, xutils, xweights


FORMATTER_TIME = mdates.DateFormatter('%H:%M')
FORMATTER_PERC = mticker.PercentFormatter(xmax=1.0)
FORMATTER_INT = int


def update_font():
    avail_fonts = set(f.name for f in matplotlib.font_manager.fontManager.ttflist)
    for font in xsettings.PREFERRED_FONTS:
        if font in avail_fonts:
            plt.rcParams.update({
                "font.family": font
            })
            break
update_font()


def WEB_IMAGE(col, srv='localhost', port=8000, width='auto'):
    return col, lambda url: f'<div style="width: {width}; display: inline-block;"><img src="//{srv}:{port}/{url}" style="width: 100%; height: auto;"></img> </div>'
    # return col, lambda url: f'<img src="{srv}{url}" style="width: {int(100*scale)}%; height: auto;"></img>'


_TOOLTIP_CSS = """
table
{
  border-collapse: collapse;
}
th
{
  color: #ffffff;
  background-color: #000000;
}
td
{
  background-color: #cccccc;
}
table, th, td
{
  font-family:Arial, Helvetica, sans-serif;
  border: 1px solid black;
  text-align: right;
}
"""


def merge_titles(title1, title2):
    title1 = title1 or ''
    title2 = title2 or ''

    if not title1:
        return title2

    if not title2:
        return title1

    if title1.endswith('\n'):
        return f"{title1}{title2}"

    if title1.endswith(': '):
        return f"{title1}{title2}"

    if title1.endswith(':'):
        return f"{title1} {title2}"

    return f"{title1}: {title2}"


def merge_title_desc(title, desc, as_xpptx):
    if as_xpptx and not as_xpptx.fake:
        return title, desc

    if not desc:
        if '(' in title:
            idx = title.find('(')
            title, desc = title[:idx], title[idx-1:]

    title = merge_titles(title, desc)
    return title, ''


def plot_decision_regions(clf, df, feature_cols, target, class_names=None, title='Decision Regions', desc='', as_xpptx=None):
    """
    Note: target needs to be integer to work, but can specify class_names for better legend.

    If target is str, can make integer by:
    - le = preprocessing.LabelEncoder()
    - df[target_enc] = le.fit_transform(df[target])
    - class_names = le.classes_
    """

    assert len(feature_cols) == 2, feature_cols


    X = np.array(df[feature_cols].to_numpy())
    y = np.array(df[target].to_numpy())

    if class_names is not None:
        class_names = list(class_names)
    else:
        class_names = list(range(len(np.unique(y))))

    slide_note = """
    This plots shows how a model's predictions behave, dependent on the 2 features.
    Each background color is a region in which the model makes one or another prediction.
    
    The specific points are the data used in training.
    """

    with plot_wrapper(title=title, xlabel=feature_cols[0], ylabel=feature_cols[1], legend=False, desc=desc, slide_note=slide_note, as_xpptx=as_xpptx) as (fix, ax):
        mlxtend_plotting.plot_decision_regions(X=X, y=y, clf=clf, legend=0)
        handles, _ = ax.get_legend_handles_labels()

        ax.legend(
            handles,
            class_names,
            framealpha=0.3,
            scatterpoints=1,
            loc='best'
        )

def plot_gini(a, num_bins=101, xlabel='samples', ylabel='values', title='', figsize=(8,8)):
    """
    Credit: https://stackoverflow.com/questions/39512260/calculating-gini-coefficient-in-python-numpy
    """
    a = pd.Series(a)
    a = a.dropna()
    np.sort(a)
    gini_val = xcalc.x_calc_gini(a, presorted=True)

    def G(v):
        bins = np.linspace(0., 100., num_bins)
        total = float(np.sum(v))
        yvals = []
        for b in bins:
            bin_vals = v[v <= np.percentile(v, b)]
            bin_fraction = (np.sum(bin_vals) / total) * 100.0
            yvals.append(bin_fraction)

        return bins, yvals

    bins, result = G(a)
    plt.figure(figsize=figsize)
    # plt.subplot(2, 1, 1)
    plt.plot(bins, result, label="observed")
    plt.plot(bins, bins, '--', label="perfect eq.")
    plt.xlabel(f"fraction of {xlabel}")
    plt.ylabel(f"fraction of {ylabel}")
    title2 = merge_titles(title, f"GINI={gini_val:.4f}")
    plt.title(title2)
    plt.legend()
    # plt.subplot(2, 1, 2)
    # plt.hist(a, bins=20)
    plt.tight_layout()
    plt.show()


def plot_beta_prob_dists(df, n_col=None, success_col=None, fail_col=None, label_on=None, title='', xlabel='probability of success'):
    pre_plot()
    for _, row in df.iterrows():
        success = None
        fail = None
        if success_col:
            success = row[success_col]
        if fail_col:
            fail = row[fail_col]
        if n_col:
            n = row[n_col]
            if success is not None:
                fail = n - success
            elif fail is not None:
                success = n - fail

        assert success is not None
        assert fail is not None
        n = success + fail

        label = ''
        if label_on:
            label = row[label_on]
        label = f"{label} ({success:.0f}/{n:.0f})"

        rv = stats.beta(success+1, fail+1)
        x = np.linspace(0.001, 0.999, 1000)
        plt.plot(x, rv.pdf(x), lw=1, label=label)

    post_plot(title=title, ylabel=False, xlabel=xlabel)


def plot_feature_importances(folds, use_shap=False, title='', top_k=None, show=True, as_xpptx=None, also_text=False):
    df = xproblem.calc_feature_importances(folds, use_shap=use_shap, flat=True)
    if df is None:
        return

    fis = df.groupby('feature_name')['feature_importance'].mean()
    fis = fis.sort_values(ascending=False)
    if top_k:
        fis = fis[:top_k]
        df = df[df.feature_name.isin(fis.index.values)]

    df = xpd.x_sort_on_lookup(df, 'feature_name', fis, ascending=True)

    means = df.groupby('feature_name')['feature_importance'].mean().reset_index()

    g = sns.catplot(data=df, y='feature_name', x='feature_importance', height=6, aspect=1.5, color='xkcd:steel blue')
    g.set(title=title)

    sns.scatterplot(data=means, x='feature_importance', y='feature_name', color='xkcd:dark pink', marker='o', s=100, ax=g.ax)

    post_plot(xlim=[0, None], show=show, as_xpptx=as_xpptx)

    if also_text:
        print(fis.to_string())

    return fis


def plot_roc_curve(y_true, y_score, title='', show=True, as_xpptx=None):
    auc = metrics.roc_auc_score(y_true, y_score)
    fper, tper, thresholds = metrics.roc_curve(y_true, y_score)
    plt.plot(fper, tper, color='orange', label=f'ROC (AUC={auc:.3f})')
    plt.fill_between(fper, tper, color='orange', alpha=0.1)
    plt.plot([0, 1], [0, 1], color='darkblue', linestyle='--')

    xlabel = 'False Positive Rate'
    ylabel = 'True Positive Rate'
    desc = f'ROC Curve (AUC={auc:.3f})'

    if as_xpptx is None or as_xpptx.fake:
        if title:
            title = f"{title}\n{desc}"
        else:
            title = desc

        desc = ''

    slide_note = """
A binary classification model's actual output is a probability: a number between 0 & 1.  
- 0.0 means that the model is certain sure that it's negative
- 1.0 means the model is certain that it's positive
- 0.5 means
- 0.8 means the model is fairly sure that it's positive, but not as sure as 1.0
- 0.2 means the model is fairly sure that it's negative, but not as sure as 0.0

When we want to use the model to actually predict something as "Postive" or "Negative", it means we need to [arbitrarily] select a threshold for deciding from which point we want to predict "Positive". 
- A typical (default) threshold is 0.5: if the model's predicted probability is >= 0.5, then we say "Positive", otherwise we say "Negative"
- But we don't have to use 0.5 as the threshold.  Different thresholds will give us different true-positive-rates & false-positive-rates.

But there is a tradeoff:
- A higher threshold will give us a higher TPR, but also a higher FPR
  (we say that "Positive" only when very sure, thus we'll tend to be more correct when we say "Positive", but we'll also be saying "Negative" more often, thus there will be more Positives that we'll say "Negative" for.)
- A lower threshold will give as a lower FPR, but also a lower TPR.

The ROC curve is a way to see all the possible thresholds, how the tradeoff that it generates between TPR & FPR.

The “right” threshold depends on your goal. For example, in fraud detection, you may prefer more false alarms if it means catching almost all fraud cases. In medical tests, you might prefer fewer false positives to avoid unnecessary treatments.
    """.strip()

    post_plot(title=title, desc=desc, xlim=[0, None], xlabel=xlabel, ylabel=ylabel, show=show, as_xpptx=as_xpptx, slide_note=slide_note)

    return auc


def plot_confusion_matrix(y_true, y_pred, y_score=None, labels=None, classes=None, title='', show=True, as_xpptx=None):
    """
    :param labels: How to display the results (in order of classes or sorted order)
    :param classes: List of target classes in case want to control order / some are missing
    """

    auc = metrics.roc_auc_score(y_true, y_score) if y_score is not None else None

    y_true = pd.Series(y_true)
    classes = classes or sorted(y_true.unique())

    if labels:
        replace_dict = {k:v for k,v in zip(classes, labels)}
        y_true = xpd.x_replace(y_true, valid_vals='all', replace_vals=replace_dict)
        y_pred = xpd.x_replace(y_pred, valid_vals='all', replace_vals=replace_dict)

        classes = [replace_dict[k] for k in classes]

    counts = sorted([(l, c) for l, c in y_true.value_counts().items()])
    counts_str = ", ".join([f"{l}={c}" for l, c in counts])

    _plot_confusion_matrix(y_true, y_pred, labels=classes, cbar=False)

    b_acc = metrics.balanced_accuracy_score(y_true, y_pred)
    desc = f"{counts_str}\nBalanced Accuracy: {100*b_acc:.1f}%\n"
    if auc is not None:
        desc = f"{desc}AUC={auc:.3f}\n"

    title, desc = merge_title_desc(title, desc, as_xpptx)

    slide_note = """
    The confusion matrix takes the model prediction scores (anything between 0 & 1), and generates a True / False prediction using:
    - if the score >= 0.5, then "True"
    - if the score < 0.5, then "False"
    
    It also calculates different values based on them:
    - **Recall**: of all the _actually_ True values, what percent were _predicted_ True?  (Same for False)
    - **Precision**: of all the _predicted_ True values, what percent were _actually_ True?
    """

    post_plot(title=title, legend=False, show=show, as_xpptx=as_xpptx, desc=desc, slide_note=slide_note)


def plot_model_reg_pred(df, target='target', pred='pred', title='', df_train=None, as_xpptx=None, show=True, desc='', figsize=(7,7), flip=False):
    with plot_wrapper(title=title, legend_loc='lower right', as_xpptx=as_xpptx, show=show, desc=desc, square=True, figsize=figsize):
        if flip:
            target, pred = pred, target
        plot_multi(df, kind='reg', x=target, y=pred, show=False, figsize=figsize)

        if 'pred_conf' in df.columns:
            df = df.sort_values(target)
            plt.fill_between(df[target], df['pred_conf'].apply(min), df['pred_conf'].apply(max), alpha=0.3, color='xkcd:sky blue', label='predicted')

        if 'pred_low' in df.columns and 'pred_high' in df.columns:
            df = df.sort_values(target)
            plt.fill_between(df[target], df['pred_low'], df['pred_high'], alpha=0.3, color='xkcd:sky blue', label='predicted')

        plt.plot([df[target].min(), df[target].max()], [df[target].min(), df[target].max()], color='xkcd:red', ls='--', label='actual')

        if df_train is not None:
            xmin = max(df_train[target].min(), df[target].min())
            xmax = min(df_train[target].max(), df[target].max())
            plt.axvspan(xmin=xmin, xmax=xmax, color='gray', alpha=0.1, label='training zone')


def plot_model_scores(y_true, y_score, bins=25, title='', show=True, as_xpptx=None):
    """
    Useful of comparing model scores for the different targets
    """

    df = pd.DataFrame({'Target': y_true, 'Model Score': y_score})
    sns.histplot(data=df, x='Model Score', hue='Target', element="step", common_norm=False, stat='percent', bins=bins)

    title2 = 'Histogram of model scores'
    if title:
        title2 = f"{title}: {title2}"

    slide_note = """
    Here we can see how well separated the two predicted classes are.
    - The x-axis is the model's predicted scores.
    - The y-axis is the amount of predictions with such a score
    - The color is the different classes
    
    We want the clases to be as separated from each other as possible.
    """

    post_plot(title=title2, legend=False, show=show, as_xpptx=as_xpptx, slide_note=slide_note)


def plot_model_accuracy_binned(df, num_bins=10, with_count=True, balanced=True, target_col='target', pred_col='pred', prob_1_col='prob_1', title='', show=True, as_xpptx=None):
    df = df[[target_col, pred_col, prob_1_col]].copy()
    df['correct'] = df[pred_col] == df[target_col]
    bin_size = 1.0/num_bins
    df['bin'] = np.floor(df[prob_1_col] / bin_size) * bin_size
    df['weight'] = xweights.x_inverse_category_weight(df[target_col])

    g = df.groupby('bin')

    if balanced:
        def calc_bal_acc(dfg):
            return (dfg['correct'] * dfg['weight']).sum() / dfg['weight'].sum()

        df_bins = g.apply(calc_bal_acc).reset_index(name='correct')
    else:
        df_bins = g.mean()['correct'].reset_index()

    df_bins['count'] = g.size().values

    accuracy_txt = "accuracy"
    if balanced:
        accuracy_txt = "accuracy (balanced)"

    title = merge_titles(title, f'Model {accuracy_txt} by score (binned)')
    slide_note = """
    Here, the x-axis represents the model's output score:
    - Lower values (left): model is more certain in its "False" prediction
    - Higher values (right): model is more certain in its "True" prediction
    - Middle values: model is not surr about its predictions
    
    The y-axis: the percent of the predictions that were predicted correctly.
    
    We expect to see a "U" shape histogram: better predictions in the edges, where the model is more certain of itself.
    """

    with plot_wrapper(title=title, slide_note=slide_note, ylim=[0, 1.2], xlim=[0, 1], y_axis_fmt=FORMATTER_PERC, ylabel=accuracy_txt, xlabel='Predicted Score', show=show, as_xpptx=as_xpptx):
        width = 0.08 * 10 / num_bins
        bars = plt.bar(df_bins['bin'], df_bins['correct'], align='edge', width=width)

        # Add accuracy percentages on top of bars
        for bar, acc, count in zip(bars, df_bins['correct'], df_bins['count']):
            text = f"{acc:.1%}"
            if with_count:
                text = f"{text} ({count})"
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02, text, ha='center', va='bottom', fontsize=10, color='black')

        plt.axhline(y=0.5, color='red', ls=":", label="Random Model")



def plot_score_comparison(scores: dict, key_label='Dataset', score_label='Model Score', bins=25, title='', show=True):
    """
    Useful for comparing the scores of various datasets:
    > plot_score_comparison({'train': train_scores, 'test': test_scores, 'blind': blind_scores)
    """

    rows = []
    for k, scores in scores.items():
        for score in scores:
            rows.append({key_label: k, score_label: score})

    df = pd.DataFrame(rows)
    sns.histplot(data=df, x=score_label, hue=key_label, element="step", common_norm=False, stat='percent', bins=bins)

    title2 = f'Histogram of model scores per {key_label}'
    if title:
        title2 = f"{title}: {title2}"

    plt.title(title2)
    plt.tight_layout()
    if show:
        plt.show()


def plot_model_scores_ratios(y_true, y_score, bins=25, ratio_of=1, title='', class_1='class 1'):
    df = pd.DataFrame({'target': y_true, 'score': y_score})
    s_min = y_score.min()
    s_max = y_score.max()
    s_range = s_max - s_min
    borders = np.linspace(s_min, s_max+s_range*.0001, bins+1)

    rows = []
    for s_start, s_end in zip(borders[:-1], borders[1:]):
        s_mid = (s_start + s_end) / 2
        df_g = df[(df.score >= s_start) & (df.score < s_end)]
        if len(df_g) == 0:
            continue

        r = (df_g.target == ratio_of).sum() / len(df_g)
        rows.append({'s_start': df_g.score.min(), 's_end': df_g.score.max(), 'ratio': r})

    df_rows = pd.DataFrame(rows)

    for row in df_rows.itertuples():
        plt.plot([row.s_start, row.s_end], [row.ratio, row.ratio], color='black')

    title = merge_titles('Histogram of model scores', title)
    post_plot(title=title, y_axis_fmt=FORMATTER_PERC, ylabel=f'% {class_1}', xlabel='model score')


def plot_corr_heatmap(df, title='Correlation Heatmap', desc=None, fontsize=12, pad=12, cmap='BrBG', figsize=(15,15), show=True, as_xpptx=None, half=True, num_round=2):
    """
    Credits: https://medium.com/@szabo.bibor/how-to-create-a-seaborn-correlation-heatmap-in-python-834c0686b88e
    """

    df = df.copy()
    for col in df.columns:
        if not pd.api.types.is_numeric_dtype(df[col].dtype):
            del df[col]

    df_corr = df.corr()
    df_corr = np.round(df_corr, num_round)
    plt.subplots(figsize=figsize)
    mask = None
    if half:
        mask = np.triu(np.ones_like(df_corr, dtype=bool))

    hm = sns.heatmap(df_corr, vmin=-1, vmax=1, annot=True, cmap=cmap, mask=mask)
    hm.set_title(title, fontdict={'fontsize': fontsize}, pad=pad)
    plt.tight_layout()
    if as_xpptx and not as_xpptx.fake:
        as_xpptx.add_slide_content(title=title, desc=desc, main_content=as_xpptx.capture_image())
    elif show:
        plt.show()

    return df_corr


def plot_dispersion_summary(df, cols=None, kind='cv', title=''):
    if cols is None:
        cols = df.columns

    rows = []
    for col in cols:
        if not pd.api.types.is_numeric_dtype(df[col].dtype):
            continue
        try:
            if kind == 'cv':
                cv = np.std(df[col])/np.mean(df[col])
            elif kind == 'std':
                cv = np.std(df[col])
            elif kind == 'kurtosis':
                cv = stats.kurtosis(df[col], fisher=True)
            elif kind == 'gini':
                cv = xcalc.x_calc_gini(df[col].to_numpy())
            elif kind == 'mad':
                cv = stats.median_abs_deviation(df[col])
            else:
                raise KeyError(kind)
        except:
            continue

        rows.append({'col': col, 'coef_var': cv})

    df_cv = pd.DataFrame(rows)
    df_cv = df_cv.sort_values('coef_var').reset_index(drop=True)

    plt.figure(figsize=(10, 6))
    bars = plt.barh(df_cv.col, df_cv.coef_var)
    for bar in bars:
        width = bar.get_width()
        if kind == 'cv':
            text = f'{100*width:.2f}%'
        elif kind in ['std', 'gini', 'mad']:
            text = f'{width:.3f}'
        elif kind == 'kurtosis':
            text = f'{width:.2f}'
        plt.text(width, bar.get_y() + bar.get_height() / 2, text, va='center')

    if kind == 'cv':
        plt.xlabel('Coefficient of Variance')
    elif kind == 'std':
        plt.xlabel('Standard Deviation')
    elif kind == 'kurtosis':
        plt.xlabel('Kurtosis')
    elif kind == 'gini':
        plt.xlabel('Gini')
    elif kind == 'mad':
        plt.xlabel('Median Absolute Deviation')

    if title:
        plt.title(title)

    plt.tight_layout()
    plt.show()


def plot_counts_2d(df, x, y, title='Counts', fontsize=12, pad=12, cmap='BrBG', figsize=(6,6), show=True, as_xpptx=None):
    df = df.copy()
    df = df[[x, y]]

    df_p = df.pivot_table(index=x, columns=y, aggfunc='size', fill_value=0)

    plt.subplots(figsize=figsize)

    hm = sns.heatmap(df_p, annot=True, cmap=cmap, fmt='d', cbar=False)
    hm.set_title(title, fontdict={'fontsize': fontsize}, pad=pad)
    plt.tight_layout()

    if as_xpptx and not as_xpptx.fake:
        as_xpptx.add_slide_content(title='Counts', desc=title, main_content=as_xpptx.capture_image())
    elif show:
        plt.show()


def plot_funnel(vals, labels, figsize=(8,5), title='', pct_kind='abs'):
    # credits: https://www.dontusethiscode.com/blog/2023-03-29_matplotlib-funnel-chart.html
    s = pd.Series(
        data=vals,
        index=labels
    )

    fig, ax = subplots(figsize=figsize)

    sorted_s = s.sort_values()

    bc = ax.barh(
        sorted_s.index,
        sorted_s,
        left=(sorted_s.max() - sorted_s) / 2 - sorted_s.max() / 2, lw=0
    )

    bc_rev = list(reversed(bc))
    for prev, cur in zip(bc_rev[:-1], bc_rev[1:]):
        prev_x0, prev_y0, prev_x1, prev_y1 = prev.get_corners()[::2, :].flat
        cur_x0, cur_y0, cur_x1, cur_y1 = cur.get_corners()[::2, :].flat

        ax.fill_betweenx(
            [prev_y0, cur_y1],
            x1=[prev_x0, cur_x0],
            x2=[prev_x1, cur_x1],
            color=prev.get_facecolor(),
            alpha=.4,
            ec='face'
        )

    for rect, (name, value) in zip(bc, sorted_s.items()):
        ax.text(
            s=f'{name.title()}\n{value:,}',
            x=rect.get_x() + (rect.get_width() / 2),
            y=rect.get_y() + (rect.get_height() / 2),
            ha='center',
            va='center',
            color='xkcd:white',
            backgroundcolor='xkcd:dark blue'
        )

    def formatter():
        def _formatter(x, pos):
            label = f'{locs[pos]}\n'
            if pct_kind == 'abs':
                label = f'{label}{pcts.loc[locs[pos]] * 100:.0f}%'
            elif pct_kind == 'diff' and not np.isnan(pct_diffs.loc[locs[pos]]):
                label = f'{label}{pct_diffs.loc[locs[pos]] * 100:.0f}%'
            return label

        locs = [t.get_text() for t in ax.get_yticklabels()]
        pcts = s / s.max()
        pct_diffs = s / s.shift()
        return _formatter

    ax.yaxis.set_major_formatter(formatter())
    ax.margins(x=0, y=0)
    ax.spines[:].set_visible(False)
    ax.yaxis.set_tick_params(labelright=True, labelleft=False, left=False)
    ax.xaxis.set_tick_params(bottom=False, labelbottom=False)
    if title:
        ax.set_title(title, y=1.05)
    plt.tight_layout()
    plt.show()


def is_dark(color):
    r, g, b = mcolors.to_rgb(color)
    brightness = 0.299 * r + 0.587 * g + 0.114 * b  # luminance formula
    return brightness < 0.5


def plot_pie(vals=None, counts=None, title='', sort_by_index=False, figsize=(6, 5), colors=None, with_numbers=True, specific_order=None, cmap=None, legend_loc=None, show=True, as_xpptx=None, desc='', slide_note=''):
    if sort_by_index and cmap is None:
        cmap = 'cool'

    on_name = ''
    name = ''
    if vals is not None:
        vals = pd.Series(vals)
        counts = vals.value_counts()
        if hasattr(vals, 'name') and vals.name is not None:
            on_name = f"{vals.name}"
            name = f"{vals.name}, "

    assert counts is not None, "either vals or counts must be provided"
    if sort_by_index:
        counts = counts.sort_index()
    else:
        counts = counts.sort_values(ascending=False)

    if specific_order is not None:
        so = [i for i in specific_order if i in counts]
        counts = counts[so]
        if colors:
            colors = [c for idx, c in enumerate(colors) if specific_order[idx] in counts]

    numbers = counts.values
    labels = counts.index.values
    actual_labels = [f"{str(l)}" for l in labels]
    if with_numbers:
        actual_labels = [f"{str(l)} ({counts[l]})" for l in labels]

    if colors:
        actual_colors = []
        if isinstance(colors, dict):
            for label in labels:
                actual_colors.append(mcolors.to_rgb(colors[label]))
        elif isinstance(colors, list):
            for color in colors:
                actual_colors.append(mcolors.to_rgb(color))
        else:
            raise TypeError(type(colors))

    else:
        if cmap:
            color_idxs = np.linspace(0, 255, len(labels)).astype(int)
            mpl_cmap = matplotlib.colormaps[cmap]
            actual_colors = [mpl_cmap(idx) for idx in color_idxs]
        else:
            actual_colors = [xsettings.x_get_color(l if not on_name else f"{on_name}={l}") for l in labels]

    plt.figure(figsize=figsize)
    wedges, texts, autotexts = plt.pie(numbers, labels=actual_labels, autopct='%1.1f%%', shadow=False, startangle=0, colors=actual_colors)

    for autotext, color in zip(autotexts, actual_colors):
        autotext.set_color('white' if is_dark(color) else 'black')

    title2 = merge_titles(title, f"{name}total count={counts.sum()}")

    post_plot(title=title2, legend_loc=legend_loc, show=show, as_xpptx=as_xpptx, desc=desc, slide_note=slide_note)
    df_res = pd.DataFrame({'label': labels, 'counts': numbers})
    df_res['perc'] = df_res['counts'] / df_res['counts'].sum()
    return df_res


def plot_counts(df, on, sort_by_counts=True, title=''):
    counts = df[on].value_counts()
    counts = counts.sort_values(ascending=False)
    plt.clf()
    title2 = merge_titles(title, f"Counts on {on}")
    plt.title(title2)
    x = np.arange(len(counts)) if sort_by_counts else counts.index.values
    plt.scatter(x, counts.values, s=2)
    plt.ylabel('counts')
    if sort_by_counts:
        plt.xlabel(f"{on} sorted by counts ({len(counts)} cases)")
        plt.tick_params(
            axis='x',  # changes apply to the x-axis
            which='both',  # both major and minor ticks are affected
            bottom=False,  # ticks along the bottom edge are off
            top=False,  # ticks along the top edge are off
            labelbottom=False)  # labels along the bottom edge are off

    else:
        plt.xlabel(f"{on}")

    plt.tight_layout()
    plt.show()
    return


def plot_bar_do(df, x_col, y_cols, total_width=0.6, y_colors=None, x_colors=None, bar_label=None):
    if isinstance(y_cols, str):
        y_cols = [y_cols]

    ax = plt.gca()
    x = np.arange(len(df))
    n = len(y_cols)
    width = total_width / n
    for idx, y in enumerate(y_cols):
        start = total_width / 2 - width/2
        offset = idx * width

        actual_color = None
        if isinstance(y_colors, dict):
            actual_color = y_colors[y]
        elif isinstance(y_colors, list):
            actual_color = y_colors[idx]

        if isinstance(x_colors, list):
            actual_color = x_colors

        bars = ax.bar(x - start + offset, df[y], width, label=xsettings.x_get_desc(y), color=actual_color)

        if bar_label is not None:
            fmt = None
            if isinstance(bar_label, str) or callable(bar_label):
                fmt = bar_label

            ax.bar_label(bars, fmt=fmt)

    ax.set_xticks(x, df[x_col])
    return bars


def plot_category_density(df, col_cat, col_dens, alt_col_dens=None, title=''):
    """
    Credit: https://seaborn.pydata.org/examples/kde_ridgeplot.html
    """

    df = xpd.x_sort_on_lookup(df, col_cat, df.groupby(col_cat)[col_dens].mean())
    sns.set_theme(style="white", rc={"axes.facecolor": (0, 0, 0, 0)})

    # Initialize the FacetGrid object
    pal = sns.cubehelix_palette(len(df.date_str.unique()), rot=-.25, light=.7)
    g = sns.FacetGrid(df, row=col_cat, hue=col_cat, aspect=8, height=1.0, palette=pal)

    # draw alt densities in background:
    if alt_col_dens:
        g.map(sns.kdeplot, alt_col_dens,
              bw_adjust=.5, clip_on=False,
              fill=True, alpha=0.8, linewidth=1, color='xkcd:light grey green')
        g.map(sns.kdeplot, alt_col_dens, clip_on=False, color="w", lw=2, bw_adjust=.5)

    # Draw the densities:
    g.map(sns.kdeplot, col_dens,
          bw_adjust=.5, clip_on=False,
          fill=True, alpha=0.8, linewidth=1.5, color='xkcd:ocean blue')
    g.map(sns.kdeplot, col_dens, clip_on=False, color="w", lw=2, bw_adjust=.5)

    # passing color=None to refline() uses the hue mapping
    g.refline(y=0, linewidth=2, linestyle="-", color=None, clip_on=False)

    # Define and use a simple function to label the plot in axes coordinates
    def label(x, color, label):
        ax = plt.gca()
        ax.text(0, .2, label, fontweight="bold", color=color,
                ha="left", va="center", transform=ax.transAxes)

    g.map(label, col_dens)

    # Set the subplots to overlap
    g.figure.subplots_adjust(hspace=-.25)

    # Remove axes details that don't play well with overlap
    g.set_titles("")
    g.set(yticks=[], ylabel="")
    g.despine(bottom=True, left=True)

    if title:
        g.fig.suptitle(title)
    #
    # plt.tight_layout()
    plt.show()


def big_scatter(df, x, y, colors='fire', title='', show=True, show_axis=True, figsize=(12, 12), plot_dim=(1000, 1000)):
    import datashader as ds
    import colorcet as cc

    fig, axes = plt.subplots(figsize=figsize)
    # a = ds.Canvas().points(df, 'x', 'y')
    # tf.shade(a)
    # plt.plot([-15, 15], [-15, 15], color='blue')
    # plt.show()

    cvs = ds.Canvas(plot_width=plot_dim[0], plot_height=plot_dim[1])
    agg = cvs.points(df, x, y)

    if colors == 'fire':
        img = ds.tf.set_background(ds.tf.shade(agg, cmap=cc.fire), "black")
    elif colors == 'bw':
        img = ds.tf.set_background(ds.tf.shade(agg, cmap=cc.b_cyclic_grey_15_85_c0_s25), "black")
    else:
        raise ValueError(colors)

    img2 = img.to_pil()
    plt.imshow(img2, extent=(img[x].min(), img[x].max(), img[y].min(), img[y].max()))

    if not show_axis:
        plt.axis('off')

    plt.tight_layout()

    if title:
        plt.title(title)

    if show:
        plt.show()


def add_rectangle_and_label(image, xyxy, title, color='red', font_size=1):
    """
    Adds a rectangle and a label to an image.

    Parameters:
    - image: RGB image as a numpy array.
    - xyxy: Tuple of (x1, y1, x2, y2) coordinates for the rectangle.
    - title: The text for the label.
    - color: String with the name of the color for the rectangle and label background,
             compatible with Matplotlib color names.

    Returns:
    - Modified image as a numpy array with the rectangle and label on it.
    """
    # Convert color name to RGB tuple with scaling to 0-255
    rgb_color = tuple([int(255 * c) for c in to_rgb(color)])

    # Draw the rectangle
    image_with_rect = cv2.rectangle(image.copy(), (xyxy[0], xyxy[1]), (xyxy[2], xyxy[3]), rgb_color, 2)

    # Calculate width & height of the label
    (w, h), _ = cv2.getTextSize(title, cv2.FONT_HERSHEY_SIMPLEX, font_size, 1)

    # Make sure the label always fits within the image bounds
    label_x1 = max(xyxy[0], 0)
    label_y1 = max(xyxy[1] - h - 3, 0)
    label_x2 = min(xyxy[0] + w + 2, image.shape[1])
    label_y2 = xyxy[1]

    text_color = (0, 0, 0) if (rgb_color[0] * 0.299 + rgb_color[1] * 0.587 + rgb_color[2] * 0.114) > 186 else (255, 255, 255)

    # Draw the label rectangle
    image_with_label = cv2.rectangle(image_with_rect, (label_x1, label_y1), (label_x2, label_y2), rgb_color, -1)

    # Put the label text
    image_with_label_text = cv2.putText(image_with_label, title, (label_x1, label_y2 - 3), cv2.FONT_HERSHEY_SIMPLEX, font_size, text_color, int(font_size*2)) #min(3,int(math.ceil(font_size*.3))))

    return image_with_label_text


def plot_images(images, figsize=(5, 5), title='', show=True, as_xpptx=None):
    """
    :param images: can be a single image, a list of images, or a list of tuples (img, desc)
    """

    if not isinstance(images, list) and not isinstance(images, tuple):
        images = [images]

    num_imgs = len(images)
    assert num_imgs > 0

    images2 = []
    for img in images:
        desc = ''
        if isinstance(img, tuple) or isinstance(img, list):
            img, desc = img

        if not isinstance(img, np.ndarray):
            img = np.asarray(img)

        images2.append((img, desc))

    images = images2
    cmap = None
    if len(images[0][0].shape) == 2:
        cmap = 'gray'

    fig, axarr = plt.subplots(1, num_imgs, figsize=(figsize[0]*num_imgs, figsize[1]), squeeze=False)

    for idx, (img, desc) in enumerate(images):
        axarr[0][idx].imshow(img, cmap=cmap)
        axarr[0][idx].axis('off')
        axarr[0][idx].set_title(desc)

    if title:
        fig.suptitle(title)

    plt.tight_layout()

    if as_xpptx and not as_xpptx.fake:
        as_xpptx.add_slide_caption(title=title, content=as_xpptx.capture_image())

    elif show:
        plt.show()


@contextmanager
def plot_wrapper(title='', legend=True, legend_loc='best', xlim=None, ylim=None, xlabel=None, ylabel=None, x_rotation=None, tight_layout=True, show=True, y_auc=False, x_axis_fmt=None, y_axis_fmt=None, add_date=False, desc='', slide_note='', as_xpptx=None, figsize=(7, 5), square=False):
    fig, ax = pre_plot(figsize=figsize)
    yield fig, ax
    post_plot(title=title, legend=legend, legend_loc=legend_loc, xlim=xlim, ylim=ylim, xlabel=xlabel, ylabel=ylabel, x_rotation=x_rotation, tight_layout=tight_layout, show=show, y_auc=y_auc, x_axis_fmt=x_axis_fmt, y_axis_fmt=y_axis_fmt, add_date=add_date, desc=desc, slide_note=slide_note, as_xpptx=as_xpptx, square=square, ax=ax, fig=fig)


def pre_plot(figsize=(6, 5)):
    return plt.subplots(figsize=figsize)


def post_plot(title='', legend=True, legend_loc='best', axis_color='xkcd:dark grey', legend_title=None, xlim=None, ylim=None, xlabel=None, ylabel=None, x_rotation=None, tight_layout=True, show=True, y_auc=False, x_axis_fmt=None, y_axis_fmt=None, add_date=False, desc='', slide_note='', as_xpptx=None, square=False, ax=None, fig=None):
    """
    Helper function to set various plot attributes...
    """
    if as_xpptx and as_xpptx.fake:
        as_xpptx = None

    if ax is None:
        ax = plt.gca()

    if square:
        ax.set_aspect('equal', adjustable='box')

    if y_auc:
        ylim = [0, 1]

    if title is not None and title:
        plt.title(title)

    if '\n' in title and not desc:
        title, desc = title.split('\n', maxsplit=1)

    if xlim:
        plt.xlim(xlim)

    if ylim:
        plt.ylim(ylim)

    if xlabel:
        plt.xlabel(xlabel)

    if ylabel:
        plt.ylabel(ylabel)

    if ylabel is False:
        ax.get_yaxis().set_visible(False)

    if xlabel is False:
        ax.get_xaxis().set_visible(False)

    if x_rotation:
        plt.xticks(rotation=x_rotation)

    if x_axis_fmt:
        if x_axis_fmt == int:
            plt.gca().xaxis.set_major_locator(mticker.MultipleLocator(1))

        else:
            ax.xaxis.set_major_formatter(x_axis_fmt)

    # elif isinstance(ax.xaxis.get_major_formatter(), mdates.DateFormatter) or isinstance(ax.xaxis.get_major_formatter(), mdates.AutoDateFormatter):
    #     # locator = mdates.AutoDateLocator()
    #     # formatter = mdates.ConciseDateFormatter(locator)
    #     #
    #     # ax.xaxis.set_major_locator(locator)
    #     # ax.xaxis.set_major_formatter(formatter)
    #     if fig:
    #         fig.autofmt_xdate()

    if y_axis_fmt:
        if y_axis_fmt == int:
            plt.gca().yaxis.set_major_locator(mticker.MultipleLocator(1))
        else:
            ax.yaxis.set_major_formatter(y_axis_fmt)

    if y_auc:
        plt.axhline(y=0.5, ls=':', color='red', alpha=0.75)
        plt.axhline(y=0.65, ls=':', color='xkcd:dark yellow', alpha=0.75)
        plt.axhline(y=0.8, ls=':', color='xkcd:green', alpha=0.75)

        if y_auc == 'model':
            plt.axhline(y=0.35, ls=':', color='xkcd:dark grey', alpha=0.75)
            plt.axhline(y=0.2, ls=':', color='xkcd:dark grey', alpha=0.75)

        else:
            plt.axhline(y=0.35, ls=':', color='xkcd:dark yellow', alpha=0.75)
            plt.axhline(y=0.2, ls=':', color='xkcd:green', alpha=0.75)

    if add_date:
        date_str = dt.date.today().isoformat()
        down_shift = -0.08
        if isinstance(add_date, int) or isinstance(add_date, float):
            down_shift *= add_date
        plt.annotate(date_str, xy=(0.9, down_shift), xycoords='axes fraction')

    if tight_layout:
        plt.tight_layout()

    if legend and legend_loc != 'off':
        handles, labels = ax.get_legend_handles_labels()
        valid_labels = [label for label in labels if not label.startswith('_')]
        if valid_labels:
            ax.legend(title=legend_title, loc=legend_loc)

    if axis_color:
        for spine in ax.spines.values():
            spine.set_color(axis_color)
        ax.tick_params(colors=axis_color)
        ax.xaxis.label.set_color(axis_color)
        ax.yaxis.label.set_color(axis_color)
        ax.title.set_color(axis_color)

    if as_xpptx:
        as_xpptx.add_slide('left_column', title=title, text=desc, text_2=as_xpptx.capture_image(), slide_note=slide_note)

    elif show:
        plt.show()


def _gaussian_kernel(u):
    return np.exp(-0.5 * u * u)

def _weighted_percentile(values, weights, p):
    if len(values) == 0:
        return np.nan
    order = np.argsort(values)
    v = values[order]
    w = np.maximum(0.0, weights[order])
    cw = np.cumsum(w)
    if cw[-1] == 0:
        return np.nan
    return np.interp((p/100.0) * cw[-1], cw, v)

def _as_numeric_seconds(arr, base=None):
    """
    Convert datetime-like to float seconds relative to base.
    If numeric, return float array and base=None.
    """
    arr = np.asarray(arr)
    if np.issubdtype(arr.dtype, np.datetime64):
        if base is None:
            base = arr.min()
        # ns -> seconds
        sec = (arr.astype('datetime64[ns]').astype('int64')
               - np.asarray(base).astype('datetime64[ns]').astype('int64')) / 1e9
        return sec.astype(float), base
    if arr.dtype == object and isinstance(arr[0], pd.Timestamp):
        if base is None:
            base = min(arr)
        sec = (pd.to_datetime(arr) - base).total_seconds()
        return np.asarray(sec, float), base
    # already numeric
    return np.asarray(arr, float), None

def _bandwidth_numeric(x_kde, t_obs_num):
    """
    Interpret x_kde on a numeric axis.
    - True: auto heuristic
    - float/int: use as-is
    - Timedelta/np.timedelta64: convert to seconds
    """
    if x_kde is True:
        span = float(np.max(t_obs_num) - np.min(t_obs_num))
        return 0.5 * span / max(np.sqrt(len(t_obs_num)), 1.0)
    if isinstance(x_kde, (int, float)):
        return float(x_kde)
    if isinstance(x_kde, (pd.Timedelta, np.timedelta64)):
        return (x_kde / np.timedelta64(1, 's')) if isinstance(x_kde, np.timedelta64) else x_kde.total_seconds()
    raise ValueError("x_kde must be True, a number, or a Timedelta.")

def _kernel_percentiles_over_x(t_eval, t_obs, y_obs, percentiles, x_kde):
    """
    Core helper: handles datetimes, bandwidth choice, and returns
    an array of shape (len(percentiles), len(t_eval)).
    """
    t_obs = np.asarray(t_obs)
    y_obs = np.asarray(y_obs)

    # convert to numeric if needed (keeps original t_eval for plotting)
    t_obs_num, base = _as_numeric_seconds(t_obs)
    t_eval_num, _ = _as_numeric_seconds(t_eval, base=base)

    h = _bandwidth_numeric(x_kde, t_obs_num)
    inv_h = 1.0 / h

    out = np.empty((len(percentiles), len(t_eval_num)), dtype=float)
    for j, p in enumerate(percentiles):
        for i, tt in enumerate(t_eval_num):
            w = _gaussian_kernel((tt - t_obs_num) * inv_h)
            out[j, i] = _weighted_percentile(y_obs, w, p)
    return out


def plot_multi(df, kind=None, plot_func=None, x=None, y=None, var_name='variable', value_name='value', plot_on=None, group_on=None, color_on=None, annotate_on=None, cmap=None, label_on=None, style_on=None, size_on=None, figsize=(10,6), alpha=1.0, hdi_probs=(0.1, 0.25, 0.5, 0.8, 0.999), kde_cov=0.25, x_kde=False, kde_percentile=None, hist_calc='perc', hist_type='step', hist_bins=10, hist_range=None, title='', x_axis_type=None, y_axis_type=None, x_axis_fmt=None, y_axis_fmt=None, invert_yaxis=False, legend_loc='best', xlim=None, ylim=None, save_to=None, clear_folder=False, add_date=True, add_counts=True, plot_decorate_func=None, drop_na=True, as_xpptx=None, desc='', slide_note='', reset_colors=False, show=True, web=False, tooltip_on=None, **kwargs):
    """
    :param df: input dataframe
    :param kind: type of plot ('scatter', 'reg', 'line', 'hdi', '%', 'kde', 'hist')
    :param plot_func: alternative to *kind*, can provide a custom function that takes a subset of data & plots. f(plt, df, **kwargs)
    :param x: name of column for x-axis
    :param y: name of column for y-axis (can be iterable)
    :param var_name: in case y is a list
    :param value_name: in case y is a list
    :param plot_on: column name that generates different plot for each unique value
    :param group_on: column name for different subgroup of data (usually not neaded if provide color_on, etc)
    :param color_on: column name for different colors
    :param cmap: (optional) name of colormap to use, eg 'plasma' or 'cool'
    :param label_on: column name for different labels
    :param style_on: column name for different styles
    :param figsize:
    :param alpha: transparency
    :param hdi_probs: used for kind == 'hdi'
    :param kde_cov: used for kind == 'kdi'
    :param x_kde: for use with kind = '%', does kde smoothing on x-axis. Can be True or a value.
    :param hist_calc: 'perc', 'count'
    :param hist_bins: either number of bins, or a fraction of possible unique vals
    :param hist_range: optional, default <min, max> for plot
    :param hist_type: 'step', 'stepfilled', 'bar', 'barfilled'
    :param color_dict:
    :param title:
    :param x_axis_type: can set to int
    :param y_axis_type: can be set to int
    :param legend_loc:
    :param xlim:
    :param ylim:
    :param save_to: instead of displaying, can save fig to file
    :param clear_folder:
    :param add_date: adds a date to fig
    :param plot_decorate_func: called once per entire plot with (plt, dfp)
    :param drop_na: removes NA before plotting (prevents strange errors)
    :param as_xpptx: add the results to a xpptx slides presentation
    :param desc: a description (used in slides)
    :param slide_note: a slide note (used in slides)
    :param show: whether to call plt.show() when finished
    :param web: if True, display results in interactive web browser
    :param tooltip_on: which columns to show in the tooltip (requires web=True)
    :param kwargs: additional params that get passed to plot_func
    :return:
    """

    if reset_colors:
        xsettings.x_reset_colors()

    if as_xpptx and as_xpptx.fake:
        as_xpptx = None

    if kind is None and plot_func is None:
        kind = 'scatter'

    multi_y = False
    if isinstance(y, list) or isinstance(y, tuple):
        multi_y = True

        id_vars = list(set(df.columns) - set(y))
        df = pd.melt(df, id_vars=id_vars, value_vars=y, var_name=var_name, value_name=value_name)
        y = value_name
        if color_on is None:
            color_on = var_name
        elif style_on is None:
            style_on = var_name
        else:
            raise ValueError("if y is a list, then either color_on or style_on must be None")

    if kind in ['percentiles', 'percentile', 'percent', 'perc']:
        kind = '%'

    if x is None and y is None:
        raise TypeError('Missing required keyword argument: x or y')

    if save_to:
        save_to = path(save_to)
        save_to.ensure_dir()

        if clear_folder:
            save_to.rmtree()
            save_to.ensure_dir()

    if as_xpptx and plot_on:
        assert isinstance(as_xpptx, xpptx.Presentation), as_xpptx
        if title:
            as_xpptx.add_slide('section_header', title=title, subtitle=desc)

    def to_list(i):
        if not i:
            i = []

        if isinstance(i, str):
            i = [i]

        return i

    color_on = to_list(color_on)
    style_on = to_list(style_on)
    label_on = to_list(label_on)
    group_on = to_list(group_on)
    tooltip_on = to_list(tooltip_on)

    if not label_on:
        label_on = color_on + style_on

    if not color_on:
        color_on = label_on

    if label_on:
        label_on = xutils.x_remove_list_duplicates(label_on)
        df = df.sort_values(label_on)

    group_on = xutils.x_remove_list_duplicates(group_on + color_on + style_on + label_on)
    tooltip_on = xutils.x_remove_list_duplicates(to_list(plot_on) + [x, y] + group_on + tooltip_on)

    tooltip_funcs = dict()
    tooltip_cols = []
    for col in tooltip_on:
        if isinstance(col, tuple) or isinstance(col, list):
            col, func = col
            tooltip_funcs[col] = func
        tooltip_cols.append(col)

    color_id = 0
    style_id = 0
    color_lookup = None
    style_lookup = dict()
    x_label_override = None
    y_label_override = None

    legend_handles = []
    color_list = xsettings.COLOR_LIST
    if cmap and color_on:
        assert len(color_on) == 1, color_on
        color_vals = np.unique(df[color_on].to_numpy())
        color_vals = np.sort(color_vals)
        color_vals = [f"{color_on[0]}={v}" for v in color_vals]
        color_idxs = np.linspace(0, 255, len(color_vals)).astype(int)
        mpl_cmap = matplotlib.colormaps[cmap]
        color_rgbs = [mpl_cmap(idx) for idx in color_idxs]
        color_lookup = dict(zip(color_vals, color_rgbs))

        legend_idxs = np.linspace(0, len(color_idxs)-1, 3).astype(int)
        for idx in legend_idxs:
            legend_handles.append(Line2D([0], [0], marker='o', color=color_rgbs[idx], markerfacecolor=color_rgbs[idx], markersize=10, label=color_vals[idx]))

    line_styles = [
     ('solid', 'solid'),      # Same as (0, ()) or '-'
     ('dotted', 'dotted'),    # Same as (0, (1, 1)) or ':'
     ('dashed', 'dashed'),    # Same as '--'
     ('dashdot', 'dashdot'),  # Same as '-.'
     ('loosely dashed',        (0, (5, 10))),
     ('densely dashed',        (0, (5, 1))),
     ('loosely dashdotted',    (0, (3, 10, 1, 10))),
     ('dashdotted',            (0, (3, 5, 1, 5))),
     ('densely dashdotted',    (0, (3, 1, 1, 1))),
     ('dashdotdotted',         (0, (3, 5, 1, 5, 1, 5))),
     ('loosely dashdotdotted', (0, (3, 10, 1, 10, 1, 10)))]
    line_styles = [ls[1] for ls in line_styles]
    scatter_markers = list(".vsPp*+xd|_,o^<>1234shHXD")
    style_param = "ls" if kind in ['line', 'kde'] else 'marker'
    style_list = line_styles if style_param == 'ls' else scatter_markers

    for df_p, keys, plot_title in xpd.x_iter_groups(df, plot_on):
        labels = set()
        plt.close()
        did_plot = False

        label_counts = None
        if label_on:
            if kind in ['scatter', 'kde', 'hist']:
                label_counts = df_p.value_counts(label_on).reset_index(name='_count')
            elif kind in ['line'] and group_on:
                if multi_y:
                    label_counts = df_p.value_counts(label_on).reset_index(name='_count')
                else:
                    label_counts = df_p.drop_duplicates(group_on).value_counts(label_on).reset_index(name='_count')

        fig, ax = plt.subplots(figsize=figsize)

        hist_range_p = hist_bins_p = None
        if kind == 'hist':
            hist_range_p = hist_range
            if hist_range_p is None:
                hist_range_p = [df_p[y].min(), df_p[y].max()]
                if np.issubdtype(df_p[y].iloc[0], np.integer):
                    hist_range_p[0] -= 1

            if hist_range_p[0] is None:
                hist_range_p[0] = df_p[y].min()

            if hist_range_p[1] is None:
                hist_range_p[1] = df_p[y].max()

            hist_bins_p = hist_bins
            if isinstance(hist_bins_p, float):
                assert np.issubdtype(df_p[y].iloc[0], np.integer), df_p[y].dtype
                hist_bins_p = int((hist_range_p[1] - hist_range_p[0] + 1)*hist_bins_p)

        for df_g, _, group_title in xpd.x_iter_groups(df_p, group_on):
            color = None
            label = None
            style = None

            if drop_na:
                df_g = df_g.dropna(subset=[y]).copy()

            if not len(df_g):
                continue

            did_plot = True

            if label_on:
                sa_label = df_g.iloc[0][label_on]
                label = ", ".join([f"{k}={v}" for k,v in sa_label.items()])
                if add_counts and label_counts is not None:
                    count = xpd.x_filter_by_keys(label_counts, sa_label)['_count'].iloc[0]
                    label = f"{label} ({count})"

                label = fix_rtl_bidi(label)

            if label in labels:
                label = None

            labels.add(label)

            if color_on:
                sa_color_val = df_g.iloc[0][color_on]
                color_val = ", ".join([f"{k}={v}" for k, v in sa_color_val.items()])
                if color_lookup:
                    color = color_lookup[color_val]
                else:
                    color = xsettings.x_get_color(color_val)

            if style_on:
                sa_style_val = df_g.iloc[0][style_on]
                style_val = ", ".join([f"{k}={v}" for k, v in sa_style_val.items()])
                if style_val not in style_lookup:
                    style_lookup[style_val] = style_list[style_id]
                    style_id += 1

                style = style_lookup[style_val]

            params = dict()
            if color is not None:
                params['color'] = color

            if style is not None:
                params[style_param] = style

            if label is not None:
                params['label'] = label

            if alpha is not None:
                params['alpha'] = alpha

            params.update(kwargs)

            if plot_func:
                params2 = params.copy()
                if kind is not None:
                    if 'label' in params2:
                        del params2['label']

                for k in kwargs:
                    del params2[k]

                plot_func(plt, df_g, **params2)

            def add_tooltip(points):
                if not web:
                    return

                tlabels = []
                for i in range(len(df_g)):
                    l = df_g[tooltip_cols].iloc[[i], :]
                    for col, func in tooltip_funcs.items():
                        l[col] = func(l[col].iloc[0])
                    l = l.T
                    l.columns = ['']
                    tlabels.append(str(l.to_html(escape=False)))

                tooltip = mpld3_plugins.PointHTMLTooltip(points, tlabels, voffset=10, hoffset=10, css=_TOOLTIP_CSS)
                mpld3_plugins.connect(fig, tooltip)

            if kind in ['scatter', 'reg', 'corr']:
                _x = df_g[x]
                _y = df_g[y]
                params['s'] = params.get('s', 2)

                if kind in ['reg', 'corr']:
                    X = _x.to_numpy().reshape(-1, 1)
                    reg = linear_model.LinearRegression()
                    reg.fit(X, _y)
                    _y_pred = reg.predict(X)
                    st = xstats.x_model_pred_stats(_x, _y, is_classification=False)
                    if kind == 'reg':
                        text = f"R2={st.r2:.3f} Corr={st.corr:.3f} MSE={st.mse:.3f} MAE={st.mae:.3f}"
                        if st.mape is not None:
                            text = f"{text} MAPE={100*st.mape:.1f}%"
                    else:
                        text = f"Corr={st.corr:.3f}"

                    x_min = _x.iloc[_x.argmin()]
                    x_max = _x.iloc[_x.argmax()]
                    y_min = _y_pred[_x.argmin()]
                    y_max = _y_pred[_x.argmax()]

                    if 'label' in params:
                        params['label'] = f"{params['label']} ({text})"
                    else:
                        plt.text(.01, .99, text, ha='left', va='top', transform=ax.transAxes)

                    if color:
                        fact = 0.5
                        reg_color = to_rgba(color)
                        reg_color = (reg_color[0]*fact, reg_color[1]*fact, reg_color[2]*fact, reg_color[3])
                    else:
                        reg_color = 'black'

                    plt.plot([x_min, x_max], [y_min, y_max], ls=':', color=reg_color)

                if size_on:
                    min_s = params.get('s', 2)
                    sizes = df_g[size_on]
                    min_size = sizes.min()
                    max_size = sizes.max()
                    size_diff = max_size - min_size
                    size_ratio = 1
                    if size_diff > 0:
                        size_ratio = 10 / size_diff

                    sizes = (sizes - min_size) * size_ratio + min_s
                    params['s'] = sizes

                points = plt.scatter(x=_x, y=_y, **params)
                add_tooltip(points)

                if annotate_on:
                    _txt = [str(i) for i in df_g[annotate_on]]
                    for __txt, __x, __y in zip(_txt, _x, _y):
                        ax.annotate(__txt, (__x, __y))

            elif kind == 'line':
                if len(df_g) == 1:
                    params['marker'] = 'x'

                df_g = df_g.sort_values([x, y])
                points = plt.plot(df_g[x], df_g[y], **params)
                add_tooltip(points[0])

            elif kind == 'hdi':
                hdi_probs = sorted(hdi_probs)
                alpha_step = alpha / len(hdi_probs)
                g_hdi = df_g.groupby(x)
                for hdi_prob in hdi_probs:
                    try:
                        df_hdi = g_hdi.apply(lambda dfx: pd.Series(az.hdi(dfx[y].to_numpy(), hdi_prob=hdi_prob), index=['low', 'high']))
                    except ValueError:
                        raise
                    df_hdi = df_hdi.reset_index()
                    params['label'] = label
                    params['alpha'] = alpha_step
                    if 'color' not in params:
                        params['color'] = 'blue'

                    plt.fill_between(df_hdi[x], df_hdi['low'], df_hdi['high'], linewidth=0, **params)
                    label = None

                df_mode = g_hdi.apply(lambda dfx: pd.Series(az.hdi(dfx[y].to_numpy(), hdi_prob=0.05), index=['low', 'high'])).mean(axis=1)
                plt.plot(df_mode.index.values, df_mode.to_numpy(), ls='--', color=color)
                # df_means = g_hdi[y].median().reset_index(name='_mean_val')
                # plt.plot(df_means[x], df_mode.to_numpy(), ls='--', color=color)

            elif kind == '%':
                hdi_probs = sorted(hdi_probs)
                alpha_step = alpha / len(hdi_probs)

                params['label'] = label
                params['alpha'] = alpha_step
                if 'color' not in params:
                    params['color'] = 'blue'

                if not x_kde:
                    g_hdi = df_g.groupby(x)

                    for hdi_prob in hdi_probs:
                        perc_low = 0.5 - hdi_prob / 2
                        perc_high = 0.5 + hdi_prob / 2

                        sa_low = g_hdi.apply(lambda dfx: np.percentile(dfx[y].to_numpy(), 100 * perc_low))
                        sa_high = g_hdi.apply(lambda dfx: np.percentile(dfx[y].to_numpy(), 100 * perc_high))

                        plt.fill_between(sa_low.index.values, sa_low, sa_high, linewidth=0, **params)
                        params['label'] = None

                    df_means = g_hdi[y].median().reset_index(name='_mean_val')
                    plt.plot(df_means[x], df_means['_mean_val'], ls='--', alpha=0.7, color=color)
                else:
                    _t_obs = df_g[x].to_numpy()
                    _y_obs = df_g[y].to_numpy()
                    n_grid = max(400, 2 * len(_t_obs))
                    if np.issubdtype(np.asarray(_t_obs).dtype, np.datetime64):
                        t_min = pd.to_datetime(_t_obs.min())
                        t_max = pd.to_datetime(_t_obs.max())
                        t_grid = np.array(pd.date_range(t_min, t_max, periods=n_grid))
                    else:
                        t_grid = np.linspace(np.min(_t_obs), np.max(_t_obs), n_grid)

                    for hdi_prob in hdi_probs:
                        perc_low = 0.5 - hdi_prob / 2
                        perc_high = 0.5 + hdi_prob / 2

                        sa_low_vals, sa_high_vals = _kernel_percentiles_over_x(
                            t_grid, _t_obs, _y_obs, [100 * perc_low, 100 * perc_high], x_kde
                        )

                        valid = ~np.isnan(sa_low_vals) & ~np.isnan(
                            sa_high_vals)

                        plt.fill_between(t_grid, sa_low_vals, sa_high_vals, where=valid, linewidth=0, **params)
                        params['label'] = None

                    median_vals = _kernel_percentiles_over_x(t_grid, _t_obs, _y_obs, [50.0], x_kde)[0]
                    plt.plot(t_grid, median_vals, ls='--', alpha=0.7, color=color)

            elif kind == 'kde':
                # credit: https://stackoverflow.com/questions/4150171/how-to-create-a-density-plot-in-matplotlib
                if not slide_note:
                    slide_note = "A KDE plot is similar to a histogram, but smoother (without bins).\nIn the x-axis are the different values, and the y-axis is how much (about) there is of those values.  The higher, the more that we have of these values.\n\nNOTE: the area below the KDE always adds up to 1. This means that the y-axis is not the absolute count of how many instances we have, but a relative share."

                _y = np.array(df_g[y].astype(float))
                if kde_percentile:
                    _y_min = np.percentile(_y, 100 * (0.5 - kde_percentile / 2))
                    _y_max = np.percentile(_y, 100 * (0.5 + kde_percentile / 2))
                    _y = _y[(_y_min <= _y) & (_y <= _y_max)]

                if len(np.unique(_y)) == 1:
                    plt.axvline(x=_y[0], **params)
                else:
                    density = stats.gaussian_kde(_y)
                    xs = np.linspace(_y.min(), _y.max(), 200)
                    density.covariance_factor = lambda: kde_cov
                    density._compute_covariance()
                    plt.plot(xs, density(xs), **params)
                    y_label_override = 'density'
                    x_label_override = xsettings.x_get_desc(y)
                    if ylim is None:
                        ylim = [0, None]

            elif kind == 'hist':
                _y = df_g[y].astype(float)
                counts, bins = np.histogram(_y, bins=hist_bins_p, range=hist_range_p)
                if hist_calc == 'perc':
                    counts = counts / counts.sum()
                    y_label_override = 'Percent'
                    y_axis_fmt = FORMATTER_PERC
                else:
                    y_label_override = 'Count'

                plt.hist(bins[:-1], bins, weights=counts, histtype=hist_type, **params)

                x_label_override = xsettings.x_get_desc(y)

            elif not plot_func:
                raise ValueError(kind)

        if title and plot_title:
            if title.endswith('\n'):
                plot_title = f"{title}{plot_title}"
            else:
                plot_title = f"{title}: {plot_title}"

        elif title:
            plot_title = title

        if not did_plot:
            continue

        if plot_decorate_func is not None:
            plot_decorate_func(plt, df_p)

        if plot_title:
            plt.title(plot_title)

        if legend_handles:
            plt.legend(handles=legend_handles)

        elif labels and legend_loc != 'off':
            handles, labels = ax.get_legend_handles_labels()
            valid_labels = [label for label in labels if not label.startswith('_')]
            if valid_labels:
                plt.legend(loc=legend_loc)

        if x_axis_type == int:
            plt.gca().xaxis.set_major_locator(mticker.MultipleLocator(1))

        if y_axis_type == int:
            plt.gca().yaxis.set_major_locator(mticker.MultipleLocator(1))

        if x_axis_fmt:
            if x_axis_fmt == int:
                plt.gca().xaxis.set_major_locator(mticker.MultipleLocator(1))

            else:
                ax.xaxis.set_major_formatter(x_axis_fmt)

        if y_axis_fmt:
            if y_axis_fmt == int:
                plt.gca().yaxis.set_major_locator(mticker.MultipleLocator(1))
            else:
                ax.yaxis.set_major_formatter(y_axis_fmt)

        if invert_yaxis:
            plt.gca().invert_yaxis()

        if xlim:
            plt.xlim(xlim)

        if ylim:
            plt.ylim(ylim)

        if x_label_override:
            plt.xlabel(x_label_override)
        elif x:
            plt.xlabel(xsettings.x_get_desc(x))

        if y_label_override:
            plt.ylabel(y_label_override)
        elif y:
            plt.ylabel(xsettings.x_get_desc(y))

        if add_date:
            date_str = dt.date.today().isoformat()
            ax.annotate(date_str, xy=(0.9, -0.08), xycoords='axes fraction')

        plt.tight_layout()

        if save_to:
            plot_title = plot_title or "all"
            plt.savefig(save_to.joinpath(f"{plot_title}.png"), pad_inches=0)

        elif web:
            if isinstance(web, str):
                out_path = path(web)
                if not out_path.isabs():
                    out_path = xsettings.OUTPUT_PATH.joinpath(out_path)

                mpld3.save_html(fig, out_path)
            else:
                mpld3.show()
            plt.clf()

        elif as_xpptx:
            x_vs_y = f"{y}"
            if x:
                x_vs_y = f"{x} vs {y}"
            if plot_on:
                text = "\n".join([f"{k}={v}" for k,v in keys.items()])
                slide_title = ''
            else:
                slide_title = title or x_vs_y
                text = desc

            as_xpptx.add_slide('left_column', title=slide_title, text=text, text_2=as_xpptx.capture_image(), slide_note=slide_note)

        elif show:
            plt.show()
