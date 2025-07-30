from setuptools import setup, Extension, find_packages
from setuptools.command.build_py import build_py
import os
import glob
import shutil


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
    sources=get_tree_sitter_sources(
    ) + ['grammars/tree-sitter-spthy/bindings/python/tree_sitter_spthy/binding.c'],
    include_dirs=[
        'grammars/tree-sitter-spthy/src',
        'grammars/tree-sitter-spthy/bindings/python/tree_sitter_spthy',
    ],
    define_macros=[('TREE_SITTER_HIDE_SYMBOLS', None)],
)

class CustomBuildPy(build_py):
    """Custom build_py command to ensure all package files are copied"""

    def run(self):
        # Run the standard build_py
        super().run()

        # Ensure tree_sitter_spthy Python files are copied
        src_dir = 'grammars/tree-sitter-spthy/bindings/python/tree_sitter_spthy'
        dest_dir = os.path.join(self.build_lib, 'tree_sitter_spthy')

        # Copy Python files that might be missing
        for filename in ['__init__.py', '__init__.pyi', 'py.typed']:
            src_path = os.path.join(src_dir, filename)
            dest_path = os.path.join(dest_dir, filename)
            if os.path.exists(src_path) and not os.path.exists(dest_path):
                os.makedirs(dest_dir, exist_ok=True)
                shutil.copy2(src_path, dest_path)

setup(
    packages=['py_tree_sitter_spthy', 'tree_sitter_spthy'],
    package_dir={
        'py_tree_sitter_spthy': 'py_tree_sitter_spthy',
        'tree_sitter_spthy': 'grammars/tree-sitter-spthy/bindings/python/tree_sitter_spthy'
    },
    ext_modules=[tree_sitter_ext],
    package_data={
        'py_tree_sitter_spthy': ['py.typed', '*.pyi'],
        'tree_sitter_spthy': ['*.c', 'py.typed', '*.pyi'],
    },
    include_package_data=True,
    zip_safe=False,
    cmdclass={
        'build_py': CustomBuildPy,
    },
)
