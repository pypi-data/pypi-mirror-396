from typing import Any

from .._base import BaseRemoteLogSender, RemoteLogRecord


class BaseLogstashSender(BaseRemoteLogSender):
    def remote_log_record_to_ecs(self, log: RemoteLogRecord) -> dict[str, Any]:
        log_dict: dict[str, Any] = {
            "@timestamp": log.created_time.isoformat(),
            "message": log.message,
            "service.name": log.service_name,
            "log.level": log.log_level.name.lower(),
            "log.logger": log.log_logger,
        }

        if log.tags is not None:
            log_dict["tags"] = log.tags

        if log.extra is not None:
            log_dict["labels"] = log.extra

        error_type, error_message, error_stack_trace = log.error

        if error_type is not None:
            log_dict["error.type"] = error_type

        if error_message is not None:
            log_dict["error.message"] = error_message

        if error_stack_trace is not None:
            log_dict["error.stack_trace"] = error_stack_trace

        return log_dict
