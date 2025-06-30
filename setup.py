from setuptools import setup, find_packages
import os
import glob

def get_tree_sitter_sources():
    """Get generated C source files"""
    grammar_dir = "grammars/tree-sitter-spthy/src"
    sources = []
    if os.path.exists(grammar_dir):
        sources.extend(glob.glob(f"{grammar_dir}/*.c"))
    return sources

# C Extension for the compiled grammar
tree_sitter_ext = Extension(
    'tree_sitter_spthy._binding',
    sources=get_tree_sitter_sources() + ['grammars/tree-sitter-spthy/bindings/python/tree_sitter_spthy/binding.c'],
    include_dirs=[
        'grammars/tree-sitter-spthy/src',
        'grammars/tree-sitter-spthy/bindings/python/tree_sitter_spthy',
    ],
    define_macros=[('TREE_SITTER_HIDE_SYMBOLS', None)],
)

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="py-tree-sitter-spthy",
    version="1.0.1",
    author="Luca Mandrelli",
    author_email="luca.mandrelli@icloud.com",
    description="Tree-sitter parser for Spthy language",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lmandrelli/py-tree-sitter-spthy",
    packages=['tree_sitter_spthy'],
    package_dir={'tree_sitter_spthy': 'grammars/tree-sitter-spthy/bindings/python/tree_sitter_spthy'},
    ext_modules=[tree_sitter_ext],
    package_data={
        'tree_sitter_spthy': ['*.c', 'py.typed', '*.pyi'],
    },
    include_package_data=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.8",
    install_requires=[
        "tree-sitter>=0.20.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black",
            "flake8",
        ],
    },
)
