"""
Local code execution using embedded kernel.

This module provides local code execution capabilities using an embedded kernel.
It's designed for development environments and scenarios where full isolation is not required.

WARNING: Local execution has limited security controls compared to sandbox mode.
Use sandbox mode for production or multi-tenant environments.
"""
import asyncio
import io
import json
import logging
from typing import Any

from jupyter_client.asynchronous.client import AsyncKernelClient
from jupyter_client.manager import AsyncKernelManager
from pydantic import BaseModel
from tenacity import retry, retry_if_exception_cause_type, stop_after_attempt, wait_fixed

logger = logging.getLogger(__name__)


class RuntimeOutput(BaseModel):
    """Output from code execution."""
    type: str
    content: str


class RuntimeOutputTraceback(BaseModel):
    """Output with traceback information."""
    type: str
    content: str
    traceback: str | None = None


UNINITIALIZED_CLIENT_ERROR = RuntimeOutput(
    type="error", content="attempted to use an uninitialized client"
)

_TEXT_PLAIN_MIME = "text/plain"
_IMAGE_PNG_MIME = "image/png"


class LocalKernelExecutor:
    """
    Local kernel executor for running Python code in an embedded kernel.

    This executor provides lightweight code execution without full isolation.
    It's suitable for development and testing but should not be used in
    production or multi-tenant environments.
    """

    def __init__(self, cache_dir: str, is_tcp: bool = True) -> None:
        """
        Initialize the local kernel executor.

        Args:
            cache_dir: Directory for kernel connection files
            is_tcp: Use TCP connection (True) or IPC (False)
        """
        if is_tcp:
            self.connection_config = {
                "shell_port": 0,
                "iopub_port": 0,
                "stdin_port": 0,
                "control_port": 0,
                "ip": "0.0.0.0",
                "transport": "tcp",
                "kernel_name": "python3",
                "hb": "tcp://0.0.0.0:0",
            }
        else:
            self.connection_config = {
                "shell_port": 0,
                "iopub_port": 0,
                "stdin_port": 0,
                "control_port": 0,
                "ip": "localhost",
                "transport": "ipc",
                "kernel_name": "python3",
                "shell": f"ipc://{cache_dir}/shell",
                "iopub": f"ipc://{cache_dir}/iopub",
                "stdin": f"ipc://{cache_dir}/stdin",
                "control": f"ipc://{cache_dir}/control",
                "hb": f"ipc://{cache_dir}/hb",
            }

        self.connection_file = f"{cache_dir}/kernel-connection.json"

        with open(self.connection_file, "w") as f:
            json.dump(self.connection_config, f)

        self.km: AsyncKernelManager | None = None
        self.kc: AsyncKernelClient | None = None

    def _is_relevant_message(self, msg: dict, msg_id: str) -> bool:
        """Check if message is relevant to the current execution."""
        parent_id = msg.get("parent_header", {}).get("msg_id")
        return parent_id == msg_id

    def _handle_stream(self, msg: dict, result_buffer: io.StringIO) -> RuntimeOutput | None:
        """Handle stream messages."""
        text = msg.get("content", {}).get("text", "").strip()
        if text and "Requirement already satisfied:" not in text:
            result_buffer.write(text + "\n")
        return None

    def _handle_execute_result(self, msg: dict, result_buffer: io.StringIO) -> RuntimeOutput | None:
        """Handle execute result messages."""
        data = msg.get("content", {}).get("data", {})
        text = data.get(_TEXT_PLAIN_MIME, "").strip()
        if text:
            result_buffer.write(text + "\n")
        return None

    def _handle_status(self, msg: dict, result_buffer: io.StringIO) -> RuntimeOutput | None:
        """Handle status messages."""
        if msg.get("content", {}).get("execution_state") == "idle":
            # Limit result buffer size
            current_result = result_buffer.getvalue()
            if len(current_result) > 500:
                trimmed_result = "[...]\n" + current_result[-500:]
                return RuntimeOutput(type="text", content=trimmed_result)

            return RuntimeOutput(
                type="text", content=current_result or "code run successfully (no output)"
            )

        return None

    def _handle_error(self, msg: dict, result_buffer: io.StringIO) -> RuntimeOutput | None:
        """Handle error messages."""
        content = msg.get("content", {})
        ename = content.get("ename", "Unknown error")
        evalue = content.get("evalue", "No details")
        error = f"{ename}: {evalue}"
        return RuntimeOutput(type="error", content=error)

    def _handle_display_data(self, msg: dict) -> tuple[str | None, RuntimeOutput | None]:
        """Handle display data messages."""
        data = msg.get("content", {}).get("data", {})

        if _IMAGE_PNG_MIME in data:
            return None, RuntimeOutput(type=_IMAGE_PNG_MIME, content=data[_IMAGE_PNG_MIME])

        if _TEXT_PLAIN_MIME in data:
            return None, RuntimeOutput(type="text", content=data[_TEXT_PLAIN_MIME])

        return None, RuntimeOutput(type="error", content="Could not parse output")

    async def arun(self, code: str) -> RuntimeOutput:
        """
        Execute code asynchronously and return the result.

        Automatically sets up matplotlib to use inline backend for plot capture.
        When plt.show() is called, plots are automatically captured as PNG images.

        Args:
            code: Python code to execute

        Returns:
            RuntimeOutput with execution result
        """
        if not self.kc:
            return UNINITIALIZED_CLIENT_ERROR

        # Set up matplotlib inline backend for automatic plot capture
        # This allows plt.show() to work without plt.savefig()
        setup_code = """
import matplotlib
matplotlib.use('module://matplotlib_inline.backend_inline')
import matplotlib.pyplot as plt
from IPython.display import set_matplotlib_formats
set_matplotlib_formats('png')
"""
        # Execute setup code first (don't wait for response)
        self.kc.execute(setup_code, silent=True)

        # Execute the actual user code
        msg_id = self.kc.execute(code)
        result = io.StringIO()

        while True:
            received_msg = await self.kc.get_iopub_msg()

            msg_type = received_msg.get("header", {}).get("msg_type")

            if msg_type == "display_data":
                _, output = self._handle_display_data(received_msg)
                if output:
                    return output
                continue

            if not self._is_relevant_message(received_msg, msg_id):
                continue

            output = self._handle_message_type(received_msg, msg_type, result)
            if output:
                return output

    def _handle_message_type(self, received_msg: dict, msg_type: Any, result: io.StringIO):
        """Dispatch message to appropriate handler."""
        handler_map = {
            "stream": self._handle_stream,
            "execute_result": self._handle_execute_result,
            "status": self._handle_status,
            "error": self._handle_error,
        }

        handler = handler_map.get(msg_type)

        if handler:
            output = handler(received_msg, result)

            if output:
                return output

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(1),
        retry=retry_if_exception_cause_type(Exception),
    )
    async def __aenter__(self):
        """Start the kernel manager and client."""
        km: AsyncKernelManager = AsyncKernelManager(connection_file=self.connection_file)
        self.km = km
        await km.start_kernel()

        self.kc = km.client()
        self.kc.start_channels()
        await self.kc.wait_for_ready()

        return self

    async def __aexit__(self, exc_type, exc, tb):
        """Shutdown the kernel manager and client."""
        try:
            if self.kc:
                self.kc.shutdown()
                self.kc.stop_channels()

            if self.km:
                await self.km.shutdown_kernel()
        finally:
            self.km = None
            self.kc = None
