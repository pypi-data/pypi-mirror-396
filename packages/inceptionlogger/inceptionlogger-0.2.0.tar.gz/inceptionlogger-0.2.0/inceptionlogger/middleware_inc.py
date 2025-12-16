import uuid
from datetime import datetime
from inceptionlogger.logging_inc import logger, get_dynamic_fields
from fastapi import Request, Response, BackgroundTasks
from starlette.middleware.base import BaseHTTPMiddleware
from inceptionlogger.settings_inc import get_logging_setting

logging_settings = get_logging_setting()


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next, background_tasks: BackgroundTasks):
        # Generate a unique correlation ID
        correlation_id = str(uuid.uuid4())
        request.state.correlation_id = correlation_id
        request.state.start_time = datetime.now().timestamp()

        # Log the incoming request
        client_info = await get_client_info(request)
        def log_request():
            logger.info(
                msg="request_received",
                extra={
                    **await get_dynamic_fields(),
                    "timestamp_iso": datetime.now().isoformat(),
                    "timestamp_epoch": int(datetime.now().timestamp()),
                    "event": "request_received",
                    "method": request.method,
                    "url": request.url,
                    "path": request.url.path,
                    "correlation_id": correlation_id,
                    **client_info,
                    "message_type": "request",
                    "traceback": "",
                    "function": "logging_middleware.dispatch",
                },
            )
        background_tasks.add_task(log_request)

        # Process the request and get the response
        response = await call_next(request)

        # Log the response
        def log_response():
            logger.info(
                msg="response_sent",
                extra={
                    **await get_dynamic_fields(),
                    "timestamp_iso": datetime.now().isoformat(),
                    "timestamp_epoch": int(datetime.now().timestamp()),
                    "event": "response_sent",
                    "status_code": response.status_code,
                    "correlation_id": correlation_id,
                    "response_time": datetime.now().timestamp() - request.state.start_time,
                    **client_info,
                    "message_type": "response",
                    "traceback": "",
                    "function": "logging_middleware.dispatch",
                },
            )
        background_tasks.add_task(log_response)

        # Add Server Information to the response headers
        response = await add_server_info_to_response(response, correlation_id)
        return response


async def get_client_info(request: Request):
    return {
        "user_agent": request.headers.get("user-agent"),
        "client_ip_address": request.client.host,
        "client_hostname": request.headers.get("x-hostname", "External"),
        "client_application_name": request.headers.get(
            "x-application-name", "External"
        ),
        "client_application_version": request.headers.get(
            "x-application-version", "External"
        ),
        "client_correlation_id": request.headers.get("x-correlation-id", "External"),
        "client_log_facility": request.headers.get("x-log-facility", "External"),
        "client_log_host": request.headers.get("x-log-host", "External"),
    }


async def get_response_info(response: Response):
    return {
        "response_server_correlation_id": response.headers.get(
            "x-response-server-correlation-id"
        ),
        "response_server_hostname": response.headers.get("x-response-server-hostname"),
        "response_server_ip_address": response.headers.get(
            "x-response-server-ip-address"
        ),
        "response_server_application_name": response.headers.get(
            "x-response-server-application-name"
        ),
        "response_server_application_version": response.headers.get(
            "x-response-server-application-version"
        ),
        "response_server_log_facility": response.headers.get(
            "x-response-server-log-facility"
        ),
        "response_server_log_host": response.headers.get("x-response-server-log-host"),
    }


async def add_server_info_to_response(response: Response, correlation_id: str):
    response.headers["x-response-server-correlation-id"] = correlation_id
    response.headers["x-response-server-hostname"] = logging_settings.hostname
    response.headers["x-response-server-ip-address"] = logging_settings.ip_address
    response.headers["x-response-server-application-name"] = (
        logging_settings.application_name
    )
    response.headers["x-response-server-application-version"] = (
        logging_settings.application_version
    )
    response.headers["x-response-server-log-facility"] = logging_settings.facility
    response.headers["x-response-server-log-host"] = logging_settings.graylog_host
    return response


async def add_logs(
    request: Request, function_name: str, event: str, log_level: str, message: dict
):
    """
    Add logs to the logger.

    Args:
        request (Request): The request object containing relevant request data.
        function_name (str): The name of the function that is being logged.
        event (str): The event name (e.g., `account_creation_started`, `account_creation_completed`,
            `redis_query_started`, `redis_query_completed`).
        log_level (str): The logging level (e.g., 'info', 'error', 'debug', 'warning').
        message (dict): The message to log, containing additional context and details.

    Example:
        message = {
            "type": "result" or "query" or "message" or "error",
            "content": "User created successfully"
                # or "User not found"
                # or "sqlalchemy.exc.IntegrityError"
                # or "SELECT * FROM users WHERE id = 1"
            "traceback": str # when error occurs
            # Add any other information you want to include in the log.

        }
    """

    client_info = await get_client_info(request)
    dynamic_fields = await get_dynamic_fields()
    dynamic_fields.update(client_info)
    dynamic_fields["event"] = event
    dynamic_fields["correlation_id"] = request.state.correlation_id
    dynamic_fields["timestamp_iso"] = datetime.now().isoformat()
    dynamic_fields["timestamp_epoch"] = int(datetime.now().timestamp())
    dynamic_fields["function"] = function_name
    dynamic_fields["traceback"] = message.get("traceback", "")
    dynamic_fields["message_type"] = message.get("type", "")

    log_level = log_level.lower().strip()

    if log_level == "info":
        logger.info(msg=message, extra=dynamic_fields)
    elif log_level == "error":
        if dynamic_fields["traceback"]:
            del message["traceback"]
            logger.error(msg=message, extra=dynamic_fields)
        else:
            raise ValueError("Traceback is required for error logs")
    elif log_level == "warning":
        logger.warning(msg=message, extra=dynamic_fields)
    elif log_level == "debug":
        logger.debug(msg=message, extra=dynamic_fields)
