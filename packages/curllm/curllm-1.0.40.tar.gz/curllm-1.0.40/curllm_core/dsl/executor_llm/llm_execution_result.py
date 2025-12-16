import json
import logging
import time
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from urllib.parse import urlparse


@dataclass
class LLMExecutionResult:
    """Result of LLM-driven DSL execution."""
    success: bool
    data: Any
    task_type: str
    algorithm_used: str
    execution_time_ms: int
    fields_detected: List[str]
    filter_expr: Optional[str]

