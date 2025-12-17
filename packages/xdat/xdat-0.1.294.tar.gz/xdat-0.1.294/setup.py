from setuptools import setup
import pathlib

"""
Can install dependencies directly by running from within this folder:
> pip install .

If you want to use py-glm, must install is separately: 
> pip install git+https://github.com/madrury/py-glm.git
"""

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / 'README.md').read_text(encoding='utf-8')
version = (here / 'xdat' / 'VERSION').read_text(encoding='utf-8').strip()

setup(
    name='xdat',
    version=version,
    description='eXtended Data Analysis Toolkit',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://bitbucket.org/hermetric/xdat/',
    author='Ido Carmi',
    author_email='ido@hermetric.com',
    license='MIT',
    packages=['xdat', 'xdat/tests', 'xdat/utilities'],
    package_data={'xdat': ['media/*', "VERSION", "LICENSE"]},
    install_requires=['pandas',
                      'numpy',
                      'scipy<1.13.0',   # 1.13.0 breaks arviz
                      'scikit-learn',
                      'quantile-forest',
                      'scriptinep3',
                      # 'pystan<3',
                      'tqdm',
                      'joblib',
                      'cloudpickle',
                      'pyarrow',    # to be able to work with parquet files
                      'mapply',     # parallel pd.apply, need to call mapply.init() first, then sa.mapply()
                      'matplotlib',
                      'pandas-sets',
                      'python-slugify',
                      # 'accupy',  # requires > sudo apt -q -y install libeigen3-dev
                      # 'tensorflow>=2',
                      'seaborn',
                      'missingno',
                      'data-science-utils',
                      'munch',
                      'optuna',             # hyper-param tuning
                      'arviz',              # vs inference-tools
                      'python-pptx',
                      'feature_engine',
                      'case-converter',
                      'datashader',         # huge plots
                      'mlxtend',            # plot_decision_regions
                      'umap-learn',
                      'networkx',
                      'lightgbm',
                      'pydot',
                      'baikal',             # complex ML pipeline
                      'combo',              # support for model stacking, sequential comb, classifier selection, etc
                      'DESlib',             # ensemble selection
                      'makefun',            # a better way to create dynamic functions / decorators
                      'natsort',            # natural sorting of strings
                      'sklearn-model',
                      'SciencePlots',       # styles various plots
                      'venn',               # Venn diagrams
                      'stegaplots',         # stores any data in PNG
                      'lets-plot',          # additional plots, taken from R (ggplot2)
                      'adjustText',         # moves annotation texts to make easier to read
                      'connectorx',         # fast way to load data from DB to pandas
                      'openpyxl',
                      'pip-review',         # easier package updates: pip-review --local --auto
                      # 'git+https://github.com/madrury/py-glm.git',    # easy package for confidence intervals for GLMs
                      'chardet',            # detect file encoding
                      'python-bidi',        # handle mixed RTL & LTR texts
                      'mpld3',
                      'dunder_xml_reader',  # simple xml reader
                      'opencv-python',
                      'imgaug',
                      'portalocker',        # portable file locks
                      'colour-science',
                      'shap',
                      ],

    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
    ],
)
