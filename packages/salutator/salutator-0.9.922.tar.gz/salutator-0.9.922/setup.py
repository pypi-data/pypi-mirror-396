# setup.py
from setuptools import setup

setup(
    use_scm_version=True,  # <-- tells setuptools to use setuptools_scm
    setup_requires=["setuptools_scm"],
)

