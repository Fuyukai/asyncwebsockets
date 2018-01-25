import sys
from pathlib import Path

from setuptools import setup

if sys.version_info[0:2] < (3, 6):
    raise RuntimeError("This package requires Python 3.6+.")

setup(
    name="asyncwebsockets",
    use_scm_version={
        "version_scheme": "guess-next-dev",
        "local_scheme": "dirty-tag"
    },
    packages=[
        "asyncwebsockets"
    ],
    url="https://github.com/SunDwarf/asyncwebsockets",
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
        "wsproto>=0.11.0"
    ],
    extras_require={},
    python_requires=">=3.6",
)
