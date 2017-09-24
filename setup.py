import sys
from pathlib import Path

from setuptools import setup

if sys.version_info[0:2] < (3, 5):
    raise RuntimeError("This package requires Python 3.5+.")

setup(
    name="asyncws",
    use_scm_version={
        "version_scheme": "guess-next-dev",
        "local_scheme": "dirty-tag"
    },
    packages=[
        "asyncws"
    ],
    url="https://github.com/SunDwarf/asyncws",
    license="MIT",
    author="Laura Dickinson",
    author_email="l@veriny.tf",
    description="A websocket library for curio + trio",
    long_description=Path(__file__).with_name("README.rst").read_text(encoding="utf-8"),
    setup_requires=[
        "setuptools_scm",
        "pytest-runner"
    ],
    install_requires=[
        "multio",
        "wsproto>=0.10.0"
    ],
    extras_require={},
    python_requires=">=3.5.2",
)
