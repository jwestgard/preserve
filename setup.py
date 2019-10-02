from setuptools import find_packages, setup

setup(
    name='preserve',
    version='0.5',
    description='Command-line digital preservation utilities.',
    author='Joshua A. Westgard',
    author_email="westgard@umd.edu",
    platforms=["any"],
    license="BSD",
    url="http://github.com/jwestgard/preserve",
    packages=find_packages(),
    entry_points = {
        'console_scripts': ['preserve=preserve.__main__:main',
                            'preserve.batch=preserve.batch.__main__:main']
        },
    install_requires=[i.strip() for i in open("requirements.txt").readlines()]
)
