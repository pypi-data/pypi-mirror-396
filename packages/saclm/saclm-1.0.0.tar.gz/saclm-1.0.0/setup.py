"""
SCLM: Stateful Coherent Language Models
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="saclm",
    version="1.0.0",
    author="Mike Amega",
    author_email="contact@amewebstudio.com",
    description="Stateful Coherent Language Models - Transformers with persistent memory",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Volgat/sclm",
    project_urls={
        "Bug Tracker": "https://github.com/Volgat/sclm/issues",
        "Documentation": "https://github.com/Volgat/sclm#readme",
        "Paper": "https://arxiv.org/abs/2512.XXXXX",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: Linguistic",
    ],
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "torch>=1.10.0",
        "numpy>=1.19.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=22.0",
            "isort>=5.0",
            "flake8>=4.0",
        ],
        "transformers": [
            "transformers>=4.20.0",
        ],
    },
    keywords=[
        "language model",
        "transformer",
        "stateful",
        "coherence",
        "memory",
        "nlp",
        "deep learning",
        "pytorch",
    ],
)
