"""List all extra dependencies to be installed for Konfuzio SDK's AIs and dev mode."""

# Keep track with AI type needs which package in order to make bento builds as small as possible.
CATEGORIZATION_EXTRAS = [
    'torch>=2.7.0',
    'torchvision>=0.22.0',
    'transformers>=4.51.3',
    'timm>=1.0.15',
]

FILE_SPLITTING_EXTRAS = [
    'accelerate>=1.7.0',
    'datasets==3.6.0; python_version>="3.13"',  # Pin for Python 3.13
    'datasets>=3.6.0; python_version<"3.13"',
    'mlflow>=2.22.0',
    # Pin specific versions for Python 3.13 to avoid dependency backtracking
    'tensorflow==2.20.0; python_version>="3.13"',
    'keras==3.10.0; python_version>="3.13"',
    'h5py==3.15.0; python_version>="3.13"',
    'ml-dtypes==0.5.1; python_version>="3.13"',
    'tensorflow>=2.16.0,<2.20.0; python_version<"3.13"',  # 2.16+ includes Keras 3
    'tf-keras>=2.16.0',  # Backwards compat for transformers with Keras 3 (all Python versions)
    'torch>=2.7.0',  # Covered above but kept for clarity
    'transformers>=4.51.3',
]

EXTRAS = {
    'dev': [
        'autodoc_pydantic>=2.2.0',
        'coverage>=7.8.0',
        'jupytext>=1.17.1',
        'pytest>=8.3.5',
        'pre-commit>=4.2.0',
        'parameterized>=0.9.0',
        'Sphinx>=7.0.0',
        'sphinx-toolbox>=4.0.0',
        'sphinx-reload>=0.2.0',
        'sphinx-notfound-page>=1.1.0',
        'm2r2>=0.3.4',
        'nbval>=0.11.0',
        'sphinx-sitemap>=2.6.0',
        'sphinx-rtd-theme>=3.0.2',
        'sphinxcontrib-jquery>=4.1',
        'sphinxcontrib-mermaid>=1.0.0',
        'sphinx-copybutton>=0.5.2',
        'myst_nb>=1.2.0',
        'ruff>=0.11.10',
        'pytest-rerunfailures>=15.1',
    ],
    'ai': list(
        set(
            [
                'chardet>=5.2.0',
                'evaluate==0.4.3; python_version>="3.13"',  # Pin for Python 3.13
                'evaluate>=0.4.3; python_version<"3.13"',
            ]
            + CATEGORIZATION_EXTRAS
            + FILE_SPLITTING_EXTRAS
        )
    ),
}
