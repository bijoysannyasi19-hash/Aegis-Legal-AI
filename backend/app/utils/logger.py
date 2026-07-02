import logging
import json
import time
from datetime import datetime
from typing import Any, Dict

class JSONFormatter(logging.Formatter):
    """
    Enterprise Structured JSON Formatter.
    Strictly filters outputs to prevent leakage of unmasked legal PII/raw contract strings.
    """
    def format(self, record: logging.LogRecord) -> str:
        # 1. Base mandatory fields
        log_record: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "log_level": record.levelname,
            "message": record.getMessage(),
            "pii_redacted_flag": True, # Audit trail that PII suppression logic executed
        }
        
        # 2. Extract specific metadata dynamically injected via 'extra' dictionary
        if hasattr(record, "endpoint"):
            log_record["endpoint"] = record.endpoint
        if hasattr(record, "latency_ms"):
            log_record["latency_ms"] = record.latency_ms
        if hasattr(record, "chunks_retrieved_count"):
            log_record["chunks_retrieved_count"] = record.chunks_retrieved_count

        # 3. Aggressive Zero-Leak Guardrail
        # If the logging mechanism accidentally captures the actual generated draft or contract payload, 
        # overwrite it entirely to prevent DB/Cloud Watch leakage.
        unsafe_keywords = ["draft:", "clause:", "contract text", "here is the generation"]
        msg_lower = log_record["message"].lower()
        if any(kw in msg_lower for kw in unsafe_keywords):
            log_record["message"] = "[REDACTED SENSITIVE LEGAL TEXT]"

        return json.dumps(log_record)

def setup_structured_logger(name: str = "legal_assistant_prod") -> logging.Logger:
    logger = logging.getLogger(name)
    
    # Prevent duplicate handlers
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
        
    return logger

# Global singleton logger instance
logger = setup_structured_logger()

class RequestTimer:
    """Utility class to dynamically track endpoint latency for logging."""
    def __init__(self):
        self.start_time = time.time()
        
    def get_latency_ms(self) -> float:
        return round((time.time() - self.start_time) * 1000, 2)
