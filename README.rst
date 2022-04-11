structlog-wrapper
=================

structlog-wrapper is a structured logging integration for `Python <https://www.python.org/>`_ and `Django <https://www.djangoproject.com/>`_ projects using `structlog <https://www.structlog.org/>`_ and `django-structlog <https://django-structlog.readthedocs.io/>`_

Logging will then produce additional cohesive metadata on each logs that makes it easier to track events or incidents.


Getting Started
===============

These steps will show how to integrate structlog logging to your python & django applications.

Installation
^^^^^^^^^^^^

Install the library

.. code-block:: bash

   pip install structlog-wrapper@git+https://github.com/vy-labs/structlog-wrapper.git@v1.0.0


Python Logging
^^^^^^^^^^^^^^
Add structlog configure block to appropriate place (preferably at package initialization)

.. code-block:: python

    from structlog_wrapper.python import configure_struct_logging

    configure_struct_logging({appName}, {appType}, {appEnvironment}, log_level='INFO')

Start logging with ``structlog`` instead of ``logging``.

.. code-block:: python

   import structlog
   logger = structlog.get_logger(__name__)


Django Logging
^^^^^^^^^^^^^^

Add middleware

.. code-block:: python

   MIDDLEWARE = [
       # ...
       'structlog_wrapper.django.middlewares.RequestMiddleware',
   ]

Add structlog configuration to your ``settings.py``

.. code-block:: python

    from structlog_wrapper.django import configure_struct_logging

    configure_struct_logging({appName}, {appType}, {appEnvironment}, log_level='INFO')

Start logging with ``structlog`` instead of ``logging``.

.. code-block:: python

   import structlog
   logger = structlog.get_logger(__name__)


Celery Logging
^^^^^^^^^^^^^^

In order to be able to support celery you need to configure both your webapp and your workers

Add CeleryMiddleWare in your web app. In your settings.py

.. code-block:: python

    MIDDLEWARE = [
        # ...
        'structlog_wrapper.django.middlewares.RequestMiddleware',
        'structlog_wrapper.django.celery.middlewares.CeleryMiddleware',
    ]

Initialize Celery Worker with DjangoStructLogInitStep.
In your celery AppConfig’s module.

.. code-block:: python

    import os

    from celery import Celery, signals
    from django.conf import settings

    from structlog_wrapper.django import configure_struct_logging
    from structlog_wrapper.django.celery.steps import DjangoStructLogInitStep

    if not settings.configured:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{appName}.settings')

    app = Celery({appName})
    app.config_from_object('django.conf:settings', namespace='CELERY')
    app.steps['worker'].add(DjangoStructLogInitStep)
    app.autodiscover_tasks()


    @signals.setup_logging.connect
    def receiver_setup_logging(loglevel, logfile, format, colorize, **kwargs):
        configure_struct_logging({appName}, {appType}, {appEnvironment}, log_level=loglevel)


Additional Notes
^^^^^^^^^^^^^^^
The function configure_struct_logging, can take the following extra parameters:

1) enable_log_file (boolean -> default false)
    This param enables logs to be written inside logs directory in the deployed apps directory.

2) formatter (string)
    Accepted Values:
      a) None -> default
      b) console
    The value console allows the logs to be printed in key value pairs with coloured formatting, to be used for development purposes.

3) appType (string)
    This param can take one of the following values.
      a) web
      b) data-manager
      c) RqWorker
      d) RqWorkerScheduler
      e) RqWorkerDashboard
      f) CeleryWorker
      g) CeleryWorkerScheduler
      h) CeleryWorkerDashboard

4) appEnvironment (string)
    This can take one of the values listed below.
      a) development
      b) testing
      c) staging
      d) production
