import sys
import os
import subprocess
import re
import platform

from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
__version__ = '0.1.0'


class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=''):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)


class CMakeBuild(build_ext):
    def run(self):
        try:
            out = subprocess.check_output(['cmake', '--version'])
        except OSError:
            raise RuntimeError("CMake must be installed to build the following extensions: " +
                               ", ".join(e.name for e in self.extensions))

        if platform.system() == "Windows":
            cmake_version = tuple(int(x) for x in re.search(r'version\s*([\d.]+)', out.decode()).group(1).split('.'))
            if cmake_version < (3, 1, 0):
                raise RuntimeError("CMake >= 3.1.0 is required on Windows")

        for ext in self.extensions:
            self.build_extension(ext)

    def build_extension(self, ext):
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
        cmake_args = ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=' + extdir,
                      '-DPYTHON_EXECUTABLE=' + sys.executable]

        cfg = os.environ.get('CMAKE_BUILD_TYPE', 'Debug' if self.debug else 'Release')
        build_args = ['--config', cfg]

        if platform.system() == "Windows":
            cmake_args += ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{}={}'.format(cfg.upper(), extdir)]
            if sys.maxsize > 2**32:
                cmake_args += ['-A', 'x64']
            build_args += ['--', '/m']
        else:
            cmake_args += ['-DCMAKE_BUILD_TYPE=' + cfg]
            cmake_args += ['-DSTATICLIBS=ON']
            # Allow configuring parallel build jobs via environment variable.
            # Defaults to 1 on ARM (to avoid OOM on devices like Raspberry Pi),
            # and 2 on other architectures.
            machine = platform.machine().lower()
            is_arm = machine.startswith('arm') or machine.startswith('aarch')
            default_jobs = '1' if is_arm else '2'
            build_jobs = os.environ.get('PYDNP3_BUILD_JOBS', default_jobs)
            build_args += ['--', '-j{}'.format(build_jobs)]

        env = os.environ.copy()
        env['CXXFLAGS'] = '{} -DVERSION_INFO=\\"{}\\"'.format(env.get('CXXFLAGS', ''),
                                                              self.distribution.get_version())
        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)

        setup_path = os.path.dirname(os.path.abspath(__file__))
        if not "<string>" in open(os.path.join(setup_path, 'deps', 'dnp3', 'cpp', 'libs', 'include', 'asiodnp3', 'IMasterOperations.h')).read():
            dnp3_path = os.path.join(setup_path, 'deps', 'dnp3')
            patch_path = os.path.join(setup_path, 'imasteroperations.patch')

            subprocess.check_call(['git', 'apply', patch_path], cwd=dnp3_path)

        subprocess.check_call(['cmake', ext.sourcedir] + cmake_args, cwd=self.build_temp, env=env)
        subprocess.check_call(['cmake', '--build', '.'] + build_args, cwd=self.build_temp)

setup(
    name='pydnp3',
    version=__version__,
    author='Anh Nguyen',
    author_email='anh@kisensum.com',
    url='http://github.com/Kisensum/pydnp3',
    description='pydnp3 -- python binding for opendnp3',
    long_description='',
    install_requires=['pybind11>=2.2'],
    ext_modules=[CMakeExtension('pydnp3')],
    cmdclass=dict(build_ext=CMakeBuild),
    zip_safe=False,
)
