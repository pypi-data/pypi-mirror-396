import networkx as nx
import numpy.linalg
import pandas as pd
import numpy as np
from sklearn import decomposition, manifold, pipeline, ensemble, linear_model, preprocessing, discriminant_analysis, svm
umap = None
from tqdm import tqdm
from . import xpptx, xplots, xsettings, xmunge, xproblem, xstats
from . xcache import x_cached
import matplotlib.pyplot as plt


def x_reduce_dim_2d(df, subset=None, method='umap', merge_orig=False, **kwargs):
    """
    Various ways of reducing to 2D
    Note: can pass df.T to get feature similarity
    """

    if not isinstance(df, pd.DataFrame):
        df = pd.DataFrame(df)

    df_orig = df.copy()

    if subset:
        df = df[subset]

    if method == 'spring':
        G = nx.Graph(df.T.corr())
        pos = nx.spring_layout(G)
        df_2d = pd.DataFrame(pos).T

    elif method == 'umap':
        global umap
        if umap is None:
            import umap

        pos = umap.UMAP(**kwargs).fit_transform(df)
        df_2d = pd.DataFrame(pos)

    elif method == 'tsne':
        pos = manifold.TSNE(**kwargs).fit_transform(df)
        df_2d = pd.DataFrame(pos)

    elif method == 'pca':
        pos = decomposition.PCA(n_components=2, **kwargs).fit_transform(df)
        df_2d = pd.DataFrame(pos)

    else:
        raise ValueError(method)

    df_2d.columns = ['x', 'y']
    if merge_orig:
        df_orig = df_orig.reset_index(drop=True)
        df_merged = pd.concat([df_orig, df_2d], axis=1)
        return df_merged

    return df_2d


def x_inspect_cols(df):
    """
    Go over columns, get general idea of what they contain
    """

    for col_name in df.columns:
        sa_orig = df[col_name]
        sa = sa_orig.dropna()
        num_unique = len(sa.unique())
        topk = (sa.value_counts() / len(sa)).iloc[:5]
        topk_text = ", ".join([ f"{k}={100*v:.2f}%" for k,v in topk.items()])
        prec_na = 1 - len(sa)/len(sa_orig)
        print(f"{col_name}: dtype={sa.dtype} na={100*prec_na:.1f}% #unique={num_unique} top5={topk_text}")


def x_corr_with_target(df, target):
    """
    Go over columns, see how well they correlate with target
    """

    df, new_target = x_prep_col(df, target, on_na='drop')
    assert len(new_target) == 1, new_target
    if target != new_target:
        print(f'New Target: {target} ==> {new_target}')

    target = new_target[0]

    rows = []
    for col_name in df.columns:
        if col_name == target:
            continue

        df_sub = df[[col_name, target]].dropna()
        df_sub, new_cols = x_prep_col(df_sub, col_name)
        if len(new_cols) == 0:
            print(f"{col_name}: SKIPPED")
            continue

        elif len(new_cols) == 1:
            new_col = new_cols[0]
            corr = np.corrcoef(df_sub[new_col], df_sub[target])[0, 1]
            print(f"{new_col}: {corr}")
            rows.append({'orig_col': col_name, 'new_col': new_col, 'corr': corr, 'abs_corr': abs(corr)})

        else:
            print(f"{col_name}:")
            for new_col in new_cols:
                corr = np.corrcoef(df_sub[new_col], df_sub[target])[0, 1]
                print(f"   {new_col}: {corr}")
                rows.append({'orig_col': col_name, 'new_col': new_col, 'corr': corr, 'abs_corr': abs(corr)})

    df_corr = pd.DataFrame(rows)
    df_corr = df_corr.sort_values('abs_corr', ascending=False).reset_index(drop=True)
    return df_corr


def x_prep_df(df, target=None, on_na='auto'):
    """
    Go over columns, prepare for modeling (fill NA, dummy vars, etc.)
    NOTE: drops NA for target col, does "auto" for others
    """
    df = df.copy()

    new_target = None
    if target:
        df, new_target = x_prep_col(df, target, on_na='drop', inplace=True)
        assert len(new_target) == 1
        new_target = new_target[0]

    for col_name in df.columns:
        if col_name == new_target:
            continue

        df, _ = x_prep_col(df, col_name, on_na=on_na)

    if target is None:
        return df

    return df, new_target


def x_prep_col(df, col_name, on_na='auto', inplace=False):
    """
    prepare a column for modeling (fill NA, dummy vars, etc)
    """

    df = df.copy()
    new_cols = [col_name]

    if on_na == 'auto':
        if pd.api.types.is_float_dtype(df[col_name]):
            on_na = 'mean'
        elif pd.api.types.is_numeric_dtype(df[col_name]):
            on_na = 'median'
        else:
            on_na = 'na_value'

    if on_na == 'drop':
        df = df.dropna(subset=[col_name])

    elif on_na == 'mode':
        mode = df[col_name].value_counts().index.values[0]
        df[col_name] = np.where(df[col_name].isna(), mode, df[col_name])

    elif on_na == 'mean':
        mean = df[col_name].mean()
        df[col_name] = np.where(df[col_name].isna(), mean, df[col_name])

    elif on_na == 'median':
        median = df[col_name].median()
        df[col_name] = np.where(df[col_name].isna(), median, df[col_name])

    elif on_na == 'na_value':
        df[col_name] = np.where(df[col_name].isna(), 'NA', df[col_name])

    else:
        raise ValueError(on_na)

    if not pd.api.types.is_string_dtype(df[col_name]):
        return df, new_cols

    sa_col = df[col_name]
    unique_vals = np.unique(sa_col)
    num_unique = len(unique_vals)
    if num_unique == 1:
        del df[col_name]
        new_cols = []

    elif num_unique == 2:
        val_sel = sa_col.value_counts().index.values[0]
        new_val = (sa_col == val_sel).astype(int)
        if inplace:
            df[col_name] = new_val

        else:
            new_col_name = f"{col_name}_{val_sel}"
            new_cols = [new_col_name]
            df[new_col_name] = new_val
            del df[col_name]

    else:
        assert inplace is False, f"{col_name}: can't do inplace with multiple categorical values ({num_unique} unique)"

        new_cols = []
        for val_sel in unique_vals:
            new_val = (sa_col == val_sel).astype(int)
            new_col_name = f"{col_name}_{val_sel}"
            new_cols.append(new_col_name)
            df[new_col_name] = new_val

        del df[col_name]

    return df, new_cols


def x_explore_df_cols(df, interesting_cols=None, title='', prs=None):
    should_save = prs is None
    if prs is None:
        prs = xpptx.Presentation(title=title)

    if interesting_cols is None:
        interesting_cols = []

    if interesting_cols:
        interesting_cols_str = "".join([f"- {c}\n" for c in interesting_cols])
        xplots.plot_corr_heatmap(df[interesting_cols], show=False)
        prs.add_slide_content(title='Interesting Columns', desc=interesting_cols_str, main_content=prs.capture_image())

    df_corr = df.copy()
    for col in df_corr.columns:
        try:
            df_corr[col] = df_corr[col].astype(float)
        except ValueError:
            del df_corr[col]
        except TypeError:
            del df_corr[col]

    df_corr = df_corr.corr()
    cols_seen = set()
    for col_name in tqdm(interesting_cols + list(df.columns)):
        if col_name in cols_seen:
            continue

        cols_seen.add(col_name)

        sa = df[col_name]
        xsettings.x_reset_colors()
        print(col_name)

        col_dtype, sa = xmunge.AutoColumnType.type_and_transform(sa)

        if col_dtype is None or col_dtype is np.ndarray:
            continue

        dist_plot = None
        if col_dtype is float or (col_dtype is int and len(sa.unique()) > 15):
            try:
                xplots.plot_multi(sa.to_frame(), kind='kde', y=col_name, show=False)
                dist_plot = prs.capture_image()
            except numpy.linalg.LinAlgError:
                pass

        elif len(sa.unique()) < 200:
            xplots.plot_pie(vals=sa, show=False, sort_by_index=col_dtype is int)
            dist_plot = prs.capture_image()

        perc_na = sa.isna().sum() / len(sa)
        desc = f'Data Type: {col_dtype.__name__}\nNA: {perc_na*100:.1f}%\n'

        df_cc2 = None
        if col_name in df_corr.columns:
            df_cc = df_corr[col_name].to_frame()
            df_cc['abs_corr'] = df_cc[col_name].abs()
            df_cc = df_cc.sort_values('abs_corr', ascending=False)
            df_cc = df_cc.round(2)
            good_cols = list(set(interesting_cols + df_cc.index.values[:5].tolist()))
            if col_name in good_cols:
                good_cols.remove(col_name)

            df_cc2 = df_cc.loc[good_cols]
            df_cc2 = df_cc2.sort_values('abs_corr', ascending=False)
            del df_cc2['abs_corr']
            df_cc2 = df_cc2.reset_index()

        prs.add_slide_content(title=col_name, main_content=df_cc2, desc=desc, sub_content=dist_plot)

    if should_save:
        prs.save()


@x_cached(hash_name="@target_col", ignore_params=['prs'])
def x_explore_predictive(df, target_col, feature_cols=None, pipes=None, pipes_limit=None, treat_int_as_float=True, prs=None, min_auc=0.5, min_r2=0, topk_features=3, subtitle=''):
    print(f"- {target_col}")
    if feature_cols is not None:
        feature_cols = feature_cols[:]
        if target_col in feature_cols:
            print(f"WARNING: {target_col} in feature_cols, removing")
            feature_cols.remove(target_col)
        for col in feature_cols:
            if col not in df.columns:
                print(f"WARNING: feature {col} not in df, removing")
                feature_cols.remove(col)

    df_orig = df
    if feature_cols is not None:
        df_orig = df_orig[list(set(feature_cols+[target_col]))]
        
    df = df_orig.copy()
    should_save = prs is None
    if not subtitle:
        if prs is None:
            prs = xpptx.Presentation(title=f'Predictive EDA for {target_col}')
        else:
            prs.add_slide_h1(title=f'Predicting {target_col}')

    try:
        target_dtype, y = xmunge.AutoColumnType.type_and_transform(df[target_col])
    except ValueError:
        raise
    if target_dtype is int and treat_int_as_float:
        target_dtype = float
        print(f"WARNING: {target_col} is int, treating as float")

    df[target_col] = y
    df, target_col = x_prep_df(df, target=target_col)

    if target_col != 'target':
        assert 'target' not in df.columns
        df.rename(columns={target_col: 'target'}, inplace=True)

    if pipes is None:
        if target_dtype is bool:
            pipes = [
                ('Random Forest', ensemble.RandomForestClassifier(class_weight='balanced', max_depth=6, min_samples_split=.05, min_samples_leaf=0.05)),
                ('Logistic Regression', pipeline.Pipeline([
                    ('scale', preprocessing.StandardScaler()),
                    ('lr', linear_model.LogisticRegressionCV(class_weight='balanced', max_iter=5000))
                ])),
                # ('Linear Discriminant Analysis', pipeline.Pipeline([
                #     ('scale', preprocessing.StandardScaler()),
                #     ('ldr', discriminant_analysis.LinearDiscriminantAnalysis())
                # ])),
                # ('Support Vector Machines', pipeline.Pipeline([
                #     ('scale', preprocessing.StandardScaler()),
                #     ('svm', svm.SVC(probability=True))
                # ])),
            ]
        elif target_dtype is float:
            pipes = [
                ('Random Forest', ensemble.RandomForestRegressor(max_depth=6, min_samples_split=.05, min_samples_leaf=0.05)),
                ('Linear Regression', pipeline.Pipeline([
                    ('scale', preprocessing.StandardScaler()),
                    ('lr', linear_model.LinearRegression())
                ])),
                ('Elastic Net', pipeline.Pipeline([
                    ('scale', preprocessing.StandardScaler()),
                    ('elastic', linear_model.ElasticNetCV())
                ])),
                ('Support Vector Machines', pipeline.Pipeline([
                    ('scale', preprocessing.StandardScaler()),
                    ('svm', svm.SVR())
                ])),
            ]
        else:
            raise TypeError(f"{target_dtype} ({target_col})")

    rows = []
    for pipe_name, pipe in pipes:
        if pipes_limit and pipe_name not in pipes_limit:
            continue

        print(pipe_name)

        stratify_on = 'target' if target_dtype is bool else None
        df_test, all_folds = xproblem.train_cv(df, 'target', pipe, feature_cols=feature_cols, n_splits='max:20', stratify_on=stratify_on)
        st = xstats.x_model_pred_stats(df_test['target'], df_test['pred'])
        if target_dtype is bool:
            metric_list = ['AUC', 'BAL_ACC', 'F1']
        elif target_dtype is float:
            metric_list = ['R2', 'MAPE']
        else:
            raise TypeError(target_dtype)

        df_eval = xproblem.eval_test(df_test, eval_per='none', metric_list=metric_list)
        sa_metrics = df_eval[metric_list].mean().round(4)
        sa_metrics['P_VALUE'] = round(st.p_value, 4)
        df_metrics = sa_metrics.to_frame('CV Mean').reset_index(names='metric')
        sa_row = pd.pivot_table(df_metrics, columns='metric', values='CV Mean').iloc[0]

        fis = xplots.plot_feature_importances(all_folds, show=False)
        top_fis = fis[fis > fis.median()][:topk_features].index.values.tolist()
        if sa_row.get('AUC', min_auc) > min_auc or sa_row.get('R2', min_r2) > min_r2:
            title = pipe_name
            if subtitle:
                title = f'{title}: {subtitle}'

            print(f"- INCLUDING {target_col} - {pipe_name}: AUC={sa_row.get('AUC')} R2: {sa_row.get('R2')}")
            desc = f"- {df_orig.shape[1]-1} features before prep\n- {df.shape[1]-1} features after prep\n- Cross validated, {len(df_test.fold_num.unique())} folds"

            plt_fi = prs.capture_image()

            if target_dtype is bool:
                xplots.plot_confusion_matrix(df_test['target'], df_test['pred'], y_score=df_test.prob_1, show=False)
                plt_cm = prs.capture_image()
                prs.add_slide_content_2cols(title=title, desc=df_metrics, left=plt_cm, right=plt_fi, sub_content=desc)

            elif target_dtype is float:
                prs.add_slide_content(title=title, desc=df_metrics, main_content=plt_fi, sub_content=desc)
        else:
            print(f"- EXCLUDING {target_col} - {pipe_name}: AUC={sa_row.get('AUC')} R2: {sa_row.get('R2')}")
            plt.clf()

        sa_row['target'] = target_col
        sa_row['pipe_name'] = pipe_name
        sa_row['target_dtype'] = target_dtype.__name__
        sa_row['top_features'] = top_fis
        rows.append(sa_row)

    if should_save:
        prs.save()

    df_rows = pd.DataFrame(rows)
    return df_rows
