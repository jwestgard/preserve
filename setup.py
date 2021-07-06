from setuptools import find_packages, setup

setup(
    name='preserve',
    version='2.0.0',
    description='Command-line digital preservation utilities.',
    author='Joshua A. Westgard',
    author_email="westgard@umd.edu",
    platforms=["any"],
    license="BSD",
    url="https://github.com/umd-lib/preserve",
    packages=find_packages(),
    entry_points = {
        'console_scripts': ['preserve=preserve.__main__:main',
                            'preserve.batch=preserve.batch.__main__:main',
                            'partition=partition.__main__:main',
                            'bag=bag.__main__:main']
        },
    install_requires=[i.strip() for i in open("requirements.txt").readlines()],
    python_requires='>=3.7',
    extras_require={  # Optional
       'dev': [],
       'test': [],
    }
)
