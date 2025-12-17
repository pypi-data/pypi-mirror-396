from abc import ABC, abstractmethod
from typing import Union, List
from pathlib import Path
from krypton.schema import Document

class BaseParser(ABC):
    """Abstract base class for PDF parsers."""

    @abstractmethod
    def parse(self, file_path: Union[str, Path]) -> Document:
        """
        Parse a PDF file into a Document object.

        Args:
            file_path: Path to the PDF file.

        Returns:
            Document: The parsed document structure.
        """
        pass
