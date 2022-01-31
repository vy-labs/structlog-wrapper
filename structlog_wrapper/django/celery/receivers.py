import structlog
import time

from . import signals

logger = structlog.getLogger(__name__)


def receiver_before_task_publish(sender=None, headers=None, body=None, **kwargs):
    immutable_logger = structlog.threadlocal.as_immutable(logger)
    # noinspection PyProtectedMember
    context = dict(immutable_logger._context)
    context.pop("retry_count", None)
    context.pop("start_time", None)
    if "task_id" in context:
        context["parent_task_id"] = context.pop("task_id")
    if "task_name" in context:
        context["parent_task_name"] = context.pop("task_name")

    signals.modify_context_before_task_publish.send(
        sender=receiver_before_task_publish, context=context
    )

    import celery

    if celery.VERSION > (4,):
        headers["parent_name"] = context.get("parent_task_name")
        headers["__django_structlog__"] = context
    else:
        body["parent_name"] = context.get("parent_task_name")
        body["__django_structlog__"] = context


def receiver_after_task_publish(sender=None, headers=None, body=None, **kwargs):
    logger.info(
        "task_enqueued",
        task_id=headers.get("id") if headers else body.get("id"),
        task_name=headers.get("task") if headers else body.get("task"),
        parent_task_id=headers.get("parent_id") if headers else body.get("parent_id"),
        parent_task_name=headers.get("parent_name")
        if headers
        else body.get("parent_name"),
    )


def receiver_task_received(request, *args, **kwargs):
    logger.info(
        "task_received",
        task_id=request.task_id,
        task_name=request.task_name,
        task_status=request.task.AsyncResult(request.id).state,
        parent_task_id=request.parent_id,
    )


def receiver_task_pre_run(task_id, task, *args, **kwargs):
    logger.new()
    logger.bind(task_id=task_id)
    logger.bind(task_name=task.name)
    metadata = getattr(task.request, "__django_structlog__", {})
    logger.bind(**metadata)
    structlog.threadlocal.bind_threadlocal(retry_count=task.request.retries)
    structlog.threadlocal.bind_threadlocal(start_time=time.monotonic())
    signals.bind_extra_task_metadata.send(
        sender=receiver_task_pre_run, task=task, logger=logger
    )


def receiver_task_retry(request=None, reason=None, einfo=None, **kwargs):
    logger.warning("task_retrying", reason=reason)


def receiver_task_success(result=None, **kwargs):
    threadlocal_context = structlog.threadlocal.get_threadlocal()
    task_start_time = threadlocal_context.pop("start_time", None)
    if task_start_time is not None:
        task_duration = time.monotonic() - task_start_time
        threadlocal_context["task_duration"] = str(task_duration) + "s"

    task = kwargs['sender']
    threadlocal_context["task_status"] = task.AsyncResult(task.request.id).state
    with structlog.threadlocal.tmp_bind(logger):
        signals.pre_task_succeeded.send(
            sender=receiver_task_success, logger=logger, result=result
        )
        logger.bind(**threadlocal_context)
        logger.info("task_succeeded")


def receiver_task_failure(
    task_id=None,
    exception=None,
    traceback=None,
    einfo=None,
    sender=None,
    *args,
    **kwargs
):
    throws = getattr(sender, "throws", ())
    if isinstance(exception, throws):
        logger.info(
            "task_failed",
            error=str(exception),
        )
    else:
        logger.exception(
            "task_failed",
            error=str(exception),
            exception=exception,
        )


def receiver_task_revoked(
    request=None, terminated=None, signum=None, expired=None, **kwargs
):
    logger.warning(
        "task_revoked", terminated=terminated, signum=signum, expired=expired
    )


def receiver_task_unknown(message=None, exc=None, name=None, id=None, **kwargs):
    logger.error("task_not_found", message=message, task_name=name, task_id=id)


def receiver_task_rejected(message=None, exc=None, **kwargs):
    logger.error("task_rejected", message=message)
