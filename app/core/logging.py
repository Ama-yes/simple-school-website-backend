import json, logging

class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord):
        log = {
            "Timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
        }
        
        if record.exc_info:
            log["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(record)


def setup_logger():
    logger = logging.getLogger("SchoolApp")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
    
    return logger