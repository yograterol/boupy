import sys
import os
import subprocess

from setuptools import setup

PUBLISH_CMD = "python setup.py register sdist upload"
TEST_PUBLISH_CMD = 'python setup.py register -r test sdist upload -r test'
TEST_CMD = 'nosetests'

if 'publish' in sys.argv:
    status = subprocess.call(PUBLISH_CMD, shell=True)
    sys.exit(status)

if 'publish_test' in sys.argv:
    status = subprocess.call(TEST_PUBLISH_CMD, shell=True)
    sys.exit()

if 'run_tests' in sys.argv:
    try:
        __import__('nose')
    except ImportError:
        print('nose required. Run `pip install nose`.')
        sys.exit(1)
    status = subprocess.call(TEST_CMD, shell=True)
    sys.exit(status)

def read(fname):
    with open(fname) as fp:
        content = fp.read()
    return content

setup(
    name='boupy',
    version="0.1.2",
    description='Boupy help your life with file system backup to the cloud!',
    long_description=read("README.rst"),
    author='Yohan Graterol',
    author_email='y@mejorando.la | yograterol@fedoraproject.org',
    url='https://github.com/yograterol/boupy',
    install_requires=['docopt', 'zoort'],
    license=read("LICENSE"),
    zip_safe=False,
    keywords='boupy',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
    py_modules=["boupy"],
    entry_points={
        'console_scripts': [
            "boupy = boupy:main"
        ]
    },
    tests_require=['nose'],
    include_package_data=True,
    data_files=[('/etc/boupy', ['etc/config.json', ])]
)
