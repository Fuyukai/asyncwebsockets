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
    packages=[ "asyncwebsockets", ],
    url="https://github.com/Fuyukai/asyncwebsockets",
    license="MIT",
    author="Laura Dickinson",
    author_email="l@veriny.tf",
    description="A websocket library",
    long_description=Path(__file__).with_name("README.rst").read_text(encoding="utf-8"),
    setup_requires=[
        "setuptools_scm",
        "pytest-runner"
    ],
    install_requires=[
        "anyio>=1.0.0b2",
        "wsproto>=0.13.0",
        "async_generator",
        "yarl",
    ],
    extras_require={},
    python_requires=">=3.6",
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Framework :: AsyncIO',
        'Framework :: Trio',
        'Intended Audience :: Developers',
        'License :: OSI Approved',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
