from setuptools import setup, find_packages
import os

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read version
version = {}
with open("src/transject/__version__.py", "r") as f:
    exec(f.read(), version)

setup(
    name="transject",
    version=version['__version__'],
    author="Parmanu, LCS2, IIT Delhi",
    author_email="",
    description="Manifold-Preserving Transformer Framework for NLP Tasks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/parmanu-lcs2/TransJect",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Mathematics",
    ],
    python_requires=">=3.8",
    install_requires=[
        "torch>=1.12.0",
        "transformers>=4.30.0",
        "datasets>=2.10.0",
        "evaluate>=0.4.0",
        "pytorch-lightning>=2.0.0",
        "tqdm>=4.65.0",
        "numpy>=1.23.0",
        "scikit-learn>=1.0.0",
        "pandas>=1.3.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "jupyter>=1.0.0",
        ],
        "logging": [
            "wandb>=0.15.0",
            "tensorboard>=2.11.0",
        ],
        "all": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "jupyter>=1.0.0",
            "wandb>=0.15.0",
            "tensorboard>=2.11.0",
        ],
    },
    include_package_data=True,
    keywords="transformer knowledge-distillation manifold-learning nlp deep-learning pytorch",
    project_urls={
        "Bug Reports": "https://github.com/parmanu-lcs2/TransJect/issues",
        "Source": "https://github.com/parmanu-lcs2/TransJect",
    },
)
