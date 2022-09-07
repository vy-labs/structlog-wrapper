from setuptools import setup, find_namespace_packages

import structlog_wrapper

setup(
    name="structlog_wrapper",
    version=structlog_wrapper.__version__,
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
