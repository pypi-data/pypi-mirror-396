"""Alertiqo client for Python error tracking."""

import sys
import os
import platform
import traceback
import threading
import linecache
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple
import requests


class Breadcrumb:
    """Represents a breadcrumb for tracking user actions."""
    
    def __init__(
        self,
        message: str,
        category: str = "default",
        level: str = "info",
        data: Optional[Dict[str, Any]] = None
    ):
        self.timestamp = int(datetime.now().timestamp() * 1000)
        self.message = message
        self.category = category
        self.level = level
        self.data = data or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "message": self.message,
            "category": self.category,
            "level": self.level,
            "data": self.data,
        }


class Alertiqo:
    """Alertiqo client for error tracking."""

    def __init__(
        self,
        api_key: str,
        endpoint: str,
        environment: Optional[str] = None,
        release: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        before_send: Optional[Callable[[Dict], Optional[Dict]]] = None,
        capture_unhandled: bool = True,
    ):
        self.api_key = api_key
        self.endpoint = endpoint.rstrip("/")
        self.environment = environment or os.getenv("PYTHON_ENV", "production")
        self.release = release
        self.tags = tags or {}
        self.before_send = before_send
        self.capture_unhandled = capture_unhandled
        self.breadcrumbs: List[Breadcrumb] = []
        self.user: Optional[Dict[str, str]] = None
        self._initialized = False
        self._original_excepthook = None

    def init(self) -> None:
        """Initialize the error handlers."""
        if self._initialized:
            return

        if self.capture_unhandled:
            self._original_excepthook = sys.excepthook
            sys.excepthook = self._handle_exception

        self._initialized = True

    def _handle_exception(self, exc_type, exc_value, exc_traceback) -> None:
        """Handle uncaught exceptions."""
        self.capture_exception(exc_value)
        
        if self._original_excepthook:
            self._original_excepthook(exc_type, exc_value, exc_traceback)

    def capture_exception(
        self,
        error: Exception,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Capture an exception and send it to Alertiqo."""
        additional_data = additional_data or {}
        
        tb = traceback.format_exception(type(error), error, error.__traceback__)
        stack_trace = "".join(tb)
        
        # Extract file and line from traceback
        file_path, line_number = self._parse_traceback(error)
        code_context = self._get_code_context(file_path, line_number)

        report = {
            "message": str(error),
            "stack": stack_trace,
            "file": file_path,
            "line": line_number,
            "level": "error",
            "timestamp": int(datetime.now().timestamp() * 1000),
            "environment": self.environment,
            "release": self.release,
            "tags": {**self.tags, **additional_data.get("tags", {})},
            "context": self._get_context(),
            "breadcrumbs": [b.to_dict() for b in self.breadcrumbs],
            "code_context": code_context,
        }

        if self.user:
            report["tags"]["userId"] = self.user.get("id", "")
            report["tags"]["userEmail"] = self.user.get("email", "")

        self._send_report(report)

    def capture_message(
        self,
        message: str,
        level: str = "info"
    ) -> None:
        """Capture a message and send it to Alertiqo."""
        report = {
            "message": message,
            "level": level,
            "timestamp": int(datetime.now().timestamp() * 1000),
            "environment": self.environment,
            "release": self.release,
            "tags": self.tags.copy(),
            "context": self._get_context(),
            "breadcrumbs": [b.to_dict() for b in self.breadcrumbs],
        }

        if self.user:
            report["tags"]["userId"] = self.user.get("id", "")
            report["tags"]["userEmail"] = self.user.get("email", "")

        self._send_report(report)

    def add_breadcrumb(
        self,
        message: str,
        category: str = "default",
        level: str = "info",
        data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add a breadcrumb for tracking user actions."""
        self.breadcrumbs.append(Breadcrumb(message, category, level, data))
        
        if len(self.breadcrumbs) > 100:
            self.breadcrumbs.pop(0)

    def set_user(
        self,
        user_id: Optional[str] = None,
        email: Optional[str] = None,
        username: Optional[str] = None
    ) -> None:
        """Set user context."""
        self.user = {
            "id": user_id or "",
            "email": email or "",
            "username": username or "",
        }

    def set_tag(self, key: str, value: str) -> None:
        """Set a single tag."""
        self.tags[key] = value

    def set_tags(self, tags: Dict[str, str]) -> None:
        """Set multiple tags."""
        self.tags.update(tags)

    def _get_context(self) -> Dict[str, Any]:
        """Get system context information."""
        return {
            "runtime": "python",
            "pythonVersion": platform.python_version(),
            "platform": platform.system(),
            "arch": platform.machine(),
            "hostname": platform.node(),
        }

    def _parse_traceback(self, error: Exception) -> Tuple[Optional[str], Optional[int]]:
        """Extract file and line number from exception traceback."""
        if not error.__traceback__:
            return None, None
        
        # Get the last frame (where the error occurred)
        tb = error.__traceback__
        while tb.tb_next:
            tb = tb.tb_next
        
        frame = tb.tb_frame
        file_path = frame.f_code.co_filename
        line_number = tb.tb_lineno
        
        # Skip site-packages and internal files
        if "site-packages" in file_path or file_path.startswith("<"):
            return None, None
        
        return file_path, line_number

    def _get_code_context(
        self,
        file_path: Optional[str],
        line_number: Optional[int],
        context_lines: int = 5
    ) -> Optional[Dict[str, Any]]:
        """Get source code context around the error line."""
        if not file_path or not line_number:
            return None
        
        try:
            # Clear linecache to ensure fresh reads
            linecache.checkcache(file_path)
            
            start_line = max(1, line_number - context_lines)
            end_line = line_number + context_lines
            
            pre_lines = []
            post_lines = []
            error_line = ""
            
            for i in range(start_line, end_line + 1):
                line = linecache.getline(file_path, i)
                if not line:
                    continue
                line = line.rstrip('\n')
                
                if i < line_number:
                    pre_lines.append(line)
                elif i == line_number:
                    error_line = line
                else:
                    post_lines.append(line)
            
            return {
                "pre_lines": pre_lines,
                "error_line": error_line,
                "post_lines": post_lines,
                "start_line": start_line,
            }
        except Exception:
            return None

    def _send_report(self, report: Dict[str, Any]) -> None:
        """Send error report to Alertiqo."""
        if self.before_send:
            report = self.before_send(report)
            if report is None:
                return

        def send():
            try:
                response = requests.post(
                    f"{self.endpoint}/api/errors",
                    json=report,
                    headers={
                        "Content-Type": "application/json",
                        "X-API-Key": self.api_key,
                    },
                    timeout=10,
                )
                if response.status_code >= 400:
                    print(f"[Alertiqo] Failed to send error report: {response.status_code}")
            except Exception as e:
                print(f"[Alertiqo] Failed to send error report: {e}")

        thread = threading.Thread(target=send)
        thread.daemon = True
        thread.start()
