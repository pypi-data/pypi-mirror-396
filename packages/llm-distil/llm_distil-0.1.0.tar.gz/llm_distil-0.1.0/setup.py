from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
if readme_file.exists():
    with open(readme_file, "r", encoding="utf-8") as fh:
        long_description = fh.read()
else:
    long_description = "LLM Knowledge Distillation Library"

# Read version
version = {}
version_file = Path(__file__).parent / "src" / "llm_distil" / "__version__.py"
with open(version_file, "r") as f:
    exec(f.read(), version)

setup(
    name="llm-distil",
    version=version['__version__'],
    author="Parmanu, LCS2, IIT Delhi",
    author_email="",
    description="Knowledge Distillation for Large Language Models",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/parmanu-lcs2/llm_distil",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "torch>=1.12.0",
        "transformers>=4.30.0",
        "datasets>=2.10.0",
        "evaluate>=0.4.0",
        "rouge-score>=0.1.2",
        "tqdm>=4.65.0",
        "numpy>=1.23.0",
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
    keywords="llm knowledge-distillation transformer gpt distillation model-compression nlp deep-learning pytorch",
    project_urls={
        "Bug Reports": "https://github.com/parmanu-lcs2/llm_distil/issues",
        "Source": "https://github.com/parmanu-lcs2/llm_distil",
    },
)
