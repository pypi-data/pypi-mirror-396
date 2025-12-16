# https://graypy.readthedocs.io/en/latest/readme.html
# https://pypi.org/project/inceptionlogger/
# InceptionLogger
import os
import logging
import socket
import psutil
from datetime import datetime
from graypy import GELFUDPHandler
from inceptionlogger.settings_inc import get_logging_setting

logging_settings = get_logging_setting()
psutil.PROCFS_PATH = os.environ.get("PROCFS_PATH", "/proc")

# Configure logger
# print(logging_settings.model_dump())
logger = logging.getLogger(logging_settings.facility)
logger.setLevel(logging.INFO)
logger.propagate = True

# Add GELF handler for Graylog
log_handler = GELFUDPHandler(
    host=logging_settings.graylog_host, port=logging_settings.graylog_port
)
logger.addHandler(log_handler)


async def get_dynamic_fields():
    """Dynamically fetch system metrics for logging."""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count(logical=False)
        disk = psutil.disk_usage("/")
        uptime = datetime.now().timestamp() - psutil.boot_time()
        net_io = psutil.net_io_counters()
        memory = psutil.virtual_memory()
        hostname = socket.gethostname()

        return {
            "facility": logging_settings.facility,
            "application_name": logging_settings.application_name,
            "application_version": logging_settings.application_version,
            "hostname": hostname,
            "host_ip_address": socket.gethostbyname(hostname),
            "host_uptime_seconds": uptime,
            "host_uptime_days": uptime / 86400,
            "memory_total_gigabytes": bytes_to_gigabytes(memory.total),
            "memory_used_gigabytes": bytes_to_gigabytes(memory.used),
            "memory_free_gigabytes": bytes_to_gigabytes(memory.free),
            "memory_total_bytes": memory.total,
            "memory_used_bytes": memory.used,
            "memory_free_bytes": memory.free,
            "memory_usage_percent": memory.percent,
            "cpu_count": cpu_count,
            "cpu_usage_percent": cpu_percent,
            "disk_total_gigabytes": bytes_to_gigabytes(disk.total),
            "disk_used_gigabytes": bytes_to_gigabytes(disk.used),
            "disk_free_gigabytes": bytes_to_gigabytes(disk.free),
            "disk_total_bytes": disk.total,
            "disk_used_bytes": disk.used,
            "disk_free_bytes": disk.free,
            "disk_usage_percent": disk.percent,
            "network_bytes_received": net_io.bytes_recv,
            "network_bytes_sent": net_io.bytes_sent,
            "network_packets_received": net_io.packets_recv,
            "network_packets_sent": net_io.packets_sent,
            "network_errors_received": net_io.errin,
            "network_errors_sent": net_io.errout,
            "network_dropped_received": net_io.dropin,
            "network_dropped_sent": net_io.dropout,
        }
    except Exception as e:
        logging.error(f"Error collecting system metrics: {e}")
        return {}


# Convert bytes to gigabytes
def bytes_to_gigabytes(bytes_value):
    return bytes_value / (1024**3)


def bytes_to_megabytes(bytes_value):
    return bytes_value / (1024**2)
