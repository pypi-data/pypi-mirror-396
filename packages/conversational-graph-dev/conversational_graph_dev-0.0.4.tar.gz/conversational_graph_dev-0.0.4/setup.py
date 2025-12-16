from setuptools import setup, Extension, find_packages
from setuptools.command.build_py import build_py
from Cython.Build import cythonize
import glob
import os

class CustomBuildPy(build_py):
    def run(self):
        super().run()
        internal_build_dir = os.path.join(self.build_lib, "conversational_graph", "_internal")
        
        if os.path.exists(internal_build_dir):
            for filename in os.listdir(internal_build_dir):
                if filename.endswith('.py') and filename != '__init__.py':
                     os.remove(os.path.join(internal_build_dir, filename))
            init_py = os.path.join(internal_build_dir, "__init__.py")
            if os.path.exists(init_py):
                 os.remove(init_py)

def get_extensions():
    internal_dir = os.path.join("conversational_graph", "_internal")
    sources = glob.glob(os.path.join(internal_dir, "*.py"))
    
    extensions = []
    for source in sources:
        module_name = source.replace(os.path.sep, ".")[:-3]
        
        extensions.append(
            Extension(
                module_name,
                [source]
            )
        )
    return extensions

setup(
    name="conversational-graph-dev",
    version="0.0.4",
    packages=find_packages(),
    cmdclass={'build_py': CustomBuildPy},
    ext_modules=cythonize(
        get_extensions(),
        compiler_directives={'language_level': "3"},
        build_dir="build"
    ),
    include_package_data=True,
    exclude_package_data={
        'conversational_graph': ['_internal/*.py']
    }
)
