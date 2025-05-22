from setuptools import setup, find_packages

setup(
    name="pf2e-auto-battler",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "pygame",
    ],
    entry_points={
        'console_scripts': [
            'pf2e-auto-battler=src.__main__:main',
        ],
    },
) 