import os

from setuptools import setup, find_namespace_packages


def get_version():
    basedir = os.path.dirname(__file__)
    try:
        with open(os.path.join(basedir, 'structlog_wrapper/version.py')) as f:
            locals = {}
            exec(f.read(), locals)
            return locals['VERSION']
    except FileNotFoundError:
        raise RuntimeError('No version info found.')


setup(
    name="structlog_wrapper",
    version=get_version(),
    description="Structured Logging for Django & Python",
    url="https://github.com/ankitkr/structlog-wrapper",
    packages=find_namespace_packages(
        include=["structlog_wrapper", "structlog_wrapper.*"]
    ),
    install_requires=["django>=1.11", "structlog~=21.5.0", "django-ipware>=4.0.2", "structlog_sentry~=1.4.0"],
    include_package_data=True,
    license="MIT",
    classifiers=[
        "Framework :: Django",
        "Framework :: Django :: 1.11",
        "Framework :: Django :: 2.0",
        "Framework :: Django :: 2.1",
        "Framework :: Django :: 2.2",
        "Framework :: Django :: 3.0",
        "Framework :: Django :: 3.1",
        "Framework :: Django :: 3.2",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: System :: Logging",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
