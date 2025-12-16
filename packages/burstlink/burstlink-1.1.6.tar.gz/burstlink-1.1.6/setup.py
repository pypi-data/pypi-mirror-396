from setuptools import setup, find_packages
from pathlib import Path

long_description = Path("README.md").read_text(encoding="utf-8")

setup(
    name="burstlink",                  
    version="1.1.6",   
    description="A user-friendly package for analyzing gene interactions and transcriptional bursting.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="LiyingZhou",
    author_email="zhouly68@mail2.sysu.edu.cn",
    url="https://github.com/LiyingZhou12/burstlink",
    license="MIT",
    classifiers=["Programming Language :: Python :: 3",
                 "License :: OSI Approved :: MIT License",
                 "Operating System :: OS Independent",
                 "Intended Audience :: Science/Research",
                 "Topic :: Scientific/Engineering :: Bio-Informatics",],
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
    "numpy>=1.21",
    "scipy>=1.7",
    "pandas>=1.3",
    "matplotlib>=3.4",
    "seaborn>=0.11",
    "statsmodels>=0.12",
    "scikit-learn>=1.0",
    "umap-learn>=0.5",
    "pyarrow>=6.0",
    "joblib>=1.0",
    "tqdm>=4.60",
    "gseapy>=0.10.8",
]
)
