from celery import bootsteps

from . import receivers


class DjangoStructLogInitStep(bootsteps.Step):
    """``celery`` worker boot step to initialize ``django_structlog``.

    >>> from celery import Celery
    >>> from structlog_wrapper.django.celery.steps import DjangoStructLogInitStep
    >>>
    >>> app = Celery("demo_project")
    >>> app.steps['worker'].add(DjangoStructLogInitStep)

    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        import celery
        from celery.signals import (
            before_task_publish,
            after_task_publish,
            task_received,
            task_prerun,
            task_retry,
            task_success,
            task_failure,
            task_revoked,
        )

        before_task_publish.connect(receivers.receiver_before_task_publish)
        after_task_publish.connect(receivers.receiver_after_task_publish)
        task_received.connect(receivers.receiver_task_received)
        task_prerun.connect(receivers.receiver_task_pre_run)
        task_retry.connect(receivers.receiver_task_retry)
        task_success.connect(receivers.receiver_task_success)
        task_failure.connect(receivers.receiver_task_failure)
        task_revoked.connect(receivers.receiver_task_revoked)
        if celery.VERSION > (4,):

            from celery.signals import task_unknown, task_rejected

            task_unknown.connect(receivers.receiver_task_unknown)
            task_rejected.connect(receivers.receiver_task_rejected)
