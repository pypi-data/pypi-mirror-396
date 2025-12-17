from setuptools import setup, find_packages

setup(
    name='tardis_spac',
    version='0.6.2',
    author='pkuTrasond',
    author_email='barry_2001@stu.pku.edu.cn',
    description='TArget pRioritization toolkit for perturbation Data In Spatial-omics',
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
    install_requires=[
        'numpy',
        'pandas',
        'scipy',
        'scikit-learn',
        'scikit-bio',
        'matplotlib',
        'seaborn',
        'scanpy',
        'statsmodels',
        'tqdm',
    ]
)