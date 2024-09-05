import logging
import signal

NGINX = "NGINX"
HTTPD = "HTTPD"
PROXY = "PROXY"

PORT = {
    NGINX: "8009",
    HTTPD: "8008",
    PROXY: "80"
}

# Logger configuration
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Get a specific logger for the package
logger = logging.getLogger('MASS')

def configure_logging(level=logging.INFO):
    logger.setLevel(level)
    for handler in logger.handlers:
        handler.setLevel(level)

_shutdown = False

def get_shutdown():
    return _shutdown


def signal_handler(sig, frame):
    global _shutdown
    if not _shutdown:
        logger.info(f"Shutting down...")
        _shutdown = True

signal.signal(signal.SIGINT, signal_handler)
