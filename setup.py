from setuptools import find_packages, setup

setup(
    name='preserve',
    version='0.1',
    description='Command-line preservation utilities.',
    author='Joshua A. Westgard',
    author_email="westgard@umd.edu",
    platforms=["any"],
    license="BSD",
    url="http://github.com/jwestgard/preserve",
    packages=find_packages(),
    py_modules=['preserve'],
    install_requires=[i.strip() for i in open("requirements.txt").readlines()]
)
