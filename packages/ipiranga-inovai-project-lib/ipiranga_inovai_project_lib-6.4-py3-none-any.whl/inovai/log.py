import logging
import logging.config
from contextvars import ContextVar
from typing import Optional, List
import asgi_correlation_id


integration_batch_id: ContextVar[Optional[str]] = ContextVar('integration_batch_id', default=None)
document_correlation_id: ContextVar[Optional[str]] = ContextVar('document_correlation_id', default=None)
origin: ContextVar[Optional[str]] = ContextVar('origin', default=None)
document_type: ContextVar[Optional[str]] = ContextVar('document_type', default=None)
document_error_ids: ContextVar[Optional[List[any]]] = ContextVar('document_error_ids', default=[])
document_success_ids: ContextVar[Optional[List[any]]] = ContextVar('document_success_ids', default=[])
branch_code: ContextVar[Optional[str]] = ContextVar('branch_code', default=None)
movement_type: ContextVar[Optional[str]] = ContextVar('movement_type', default=None)
origin_id: ContextVar[Optional[str]] = ContextVar("origin_id", default=None)
internal_batch_id: ContextVar[Optional[str]] = ContextVar('internal_batch_id', default=None)
integration_employer_number: ContextVar[Optional[str]] = ContextVar(
    "integration_employer_number", default=None
)
content_type: ContextVar[Optional[str]] = ContextVar("content_type", default=None)
processing_codes: ContextVar[Optional[list[str]]] = ContextVar('processing_codes', default=None)
kit_id: ContextVar[Optional[str]] = ContextVar("kit_id", default=None)


class ChunkedStreamHandler(logging.StreamHandler):
    def emit(self, record):
        # Format the record into a log message
        msg = self.format(record)
        msg_size = len(msg.encode('utf-8'))  # Get size of the message in bytes

        max_bytes = 50 * 1024  # 50kb in bytes

        # If the message is larger than max_bytes, split it into chunks
        if msg_size > max_bytes:
            message = record.msg
            for i in range(0, len(message), max_bytes):
                chunk = message[i:i + max_bytes]
                original_msg = record.msg  # Backup original message
                try:
                    record.msg = chunk  # Alter only the message part
                    record.args = None  # Reset args to avoid formatting issues
                    super().emit(record)  # Emit the chunked message
                finally:
                    record.msg = original_msg  # Restore original message after chunk is emitted
        else:
            # If the message fits, emit it as usual
            super().emit(record)


class CustomLogger(logging.Logger):

    def _add_extra_args(self, kwargs):
        # Define os `extra_args` a serem adicionados
        extra_args = {
            "integration_batch_id": str(integration_batch_id.get()),
            "correlation_id": str(asgi_correlation_id.correlation_id.get()),
            "document_correlation_id": str(document_correlation_id.get())
            if document_correlation_id.get() is not None else str(asgi_correlation_id.correlation_id.get()).lower(),
            "origin": str(origin.get()),
            "document_type": str(document_type.get()),
            "document_error_ids": str(document_error_ids.get()),
            "document_success_ids": str(document_success_ids.get()),
            "branch_code": str(branch_code.get()),
            "movement_type": str(movement_type.get()),
            "origin_id": str(origin_id.get()),
            "internal_batch_id": str(internal_batch_id.get()),
            "integration_employer_number": str(integration_employer_number.get()),
            "content_type": str(content_type.get()),
            "processing_codes": str(processing_codes.get()),
            "kit_id": str(kit_id.get())
        }

        # Atualiza o kwargs do log com `extra_args`
        if "extra" in kwargs:
            kwargs["extra"].update(extra_args)
        else:
            kwargs["extra"] = extra_args

        return kwargs

    def info(self, msg, *args, **kwargs):
        # Adicionar os extras para logs do nível INFO
        kwargs = self._add_extra_args(kwargs)
        super().info(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        # Adicionar os extras para logs do nível ERROR
        kwargs = self._add_extra_args(kwargs)
        super().error(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        # Adicionar os extras para logs do nível WARNING
        kwargs = self._add_extra_args(kwargs)
        super().warning(msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        # Adicionar os extras para logs do nível DEBUG
        kwargs = self._add_extra_args(kwargs)
        super().debug(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        # Adicionar os extras para logs do nível CRITICAL
        kwargs = self._add_extra_args(kwargs)
        super().critical(msg, *args, **kwargs)


def get_logger(name):
    logging.setLoggerClass(CustomLogger)

    custom_handler = ChunkedStreamHandler()
    custom_handler.setLevel(logging.INFO)

    log_formatter = logging.Formatter('%(asctime)s.%(msecs)03d %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    custom_handler.setFormatter(log_formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(custom_handler)

    return logger
