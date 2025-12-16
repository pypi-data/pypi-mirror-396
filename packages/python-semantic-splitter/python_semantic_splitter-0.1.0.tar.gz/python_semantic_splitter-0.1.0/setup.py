"""
Setup configuration for Python Semantic Splitter.
"""
from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Python Semantic Splitter - Intelligent code splitting for AI/RAG pipelines"

# Read version from __init__.py
def get_version():
    init_path = os.path.join(os.path.dirname(__file__), 'python_semantic_splitter', '__init__.py')
    with open(init_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"\'')
    return '0.1.0'

setup(
    name="python-semantic-splitter",
    version=get_version(),
    author="Sarabjot Singh",
    author_email="aufvaa@example.com",
    description="Semantic Python code splitter for AI/RAG pipelines",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/ricky-aufvaa/python-semantic-splitter",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        # No external dependencies for core functionality
    ],
    extras_require={
        "yaml": ["PyYAML>=6.0"],
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=22.0",
            "flake8>=5.0",
            "mypy>=1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "python-splitter=python_semantic_splitter.cli:main",
        ],
    },
    keywords=[
        "python", "code", "splitting", "semantic", "parsing", "ast", 
        "rag", "ai", "ml", "chunks", "nlp", "text-processing"
    ],
    project_urls={
        "Bug Reports": "https://github.com/ricky-aufvaa/python-semantic-splitter/issues",
        "Source": "https://github.com/ricky-aufvaa/python-semantic-splitter",
        "Documentation": "https://github.com/ricky-aufvaa/python-semantic-splitter#readme",
    },
)
