"""Configuration models for file analysis tools."""

from typing import Optional

from langchain_core.language_models import BaseChatModel
from pydantic import Field

from codemie_tools.base.models import CodeMieToolConfig, FileConfigMixin


class FileAnalysisConfig(CodeMieToolConfig, FileConfigMixin):
    """
    Unified configuration for all file analysis tools.

    This config supports file operations for PDF, DOCX, PPTX, Excel, CSV, and other file types.
    Files are provided via the input_files attribute inherited from FileConfigMixin.

    All file analysis tools (PDFTool, DocxTool, PPTXTool, XlsxTool, CSVTool, FileAnalysisTool)
    share this single configuration class.

    Attributes:
        input_files: List of FileObject instances (inherited from FileConfigMixin)
        chat_model: Optional language model for AI-powered operations (OCR, analysis, etc.)
    """

    chat_model: Optional[BaseChatModel] = Field(default=None, exclude=True)
