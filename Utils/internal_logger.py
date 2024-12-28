import logging


class ColoredFormatter(logging.Formatter):
    # Define color codes for log levels
    COLOR_CODES = {
        'DEBUG': '\033[92m',    # Green
        'INFO': '\033[97m',     # White
        'WARNING': '\033[93m',  # Yellow
        'ERROR': '\033[91m',    # Red
        'CRITICAL': '\033[91m', # Red
    }
    RESET = '\033[0m'  # Reset color

    def format(self, record):
        log_color = self.COLOR_CODES.get(record.levelname, self.RESET)
        record.msg = f"{log_color}{record.msg}{self.RESET}"  # Apply color to the message
        return super().format(record)


class InternalLogger:
    def __init__(self):
        # Create a logger
        self._logger = logging.getLogger("Logger")
        self._logger.setLevel(logging.DEBUG)  # Set the desired logging level

        # Create a console handler (output to console)
        console_handler = logging.StreamHandler()

        # Create a custom format with colors
        custom_format = "%(asctime)s - %(levelname)s - [file- %(module)s |func- %(funcName)s |line- %(lineno)d] - %(message)s"
        formatter = ColoredFormatter(custom_format)

        # Attach the custom format to the handler
        console_handler.setFormatter(formatter)

        # Add the handler to the logger
        self._logger.addHandler(console_handler)

    def __getattr__(self, attr):
        """
        Delegate attribute access to the internal logger.
        This allows calls like logger.info(message).
        """
        return getattr(self._logger, attr)
