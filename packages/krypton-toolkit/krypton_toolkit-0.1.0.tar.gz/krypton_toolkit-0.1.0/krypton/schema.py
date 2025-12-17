import uuid
from typing import List, Optional, Any, Dict, Literal, Union
from enum import Enum
from pydantic import BaseModel, Field

class Element(BaseModel):
    """Base class for all content elements extracted from a PDF."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for the element")
    page_number: int = Field(..., description="Page number where the element is located (1-indexed)")
    bbox: Optional[List[float]] = Field(None, description="Bounding box [x0, y0, x1, y1]")

class TextElement(Element):
    """Represents a block of text."""
    type: Literal["text"] = "text"
    content: str
    category: Optional[str] = Field(None, description="Category of text (e.g., Title, NarrativeText, ListItem)")

class TableElement(Element):
    """Represents a table."""
    type: Literal["table"] = "table"
    content: str = Field(..., description="Markdown representation of the table")
    data: Optional[List[List[str]]] = Field(None, description="Structured data of the table as a list of rows")

class ImageElement(Element):
    """Represents an image."""
    type: Literal["image"] = "image"
    path: Optional[str] = Field(None, description="Path to the saved image file (if extracted)")
    base64: Optional[str] = Field(None, description="Base64 representation (if requested)")
    caption: Optional[str] = Field(None, description="Caption or summary of the image")
    description: Optional[str] = Field(None, description="LLM generated description")

ContentElement = Union[TextElement, TableElement, ImageElement]

class Page(BaseModel):
    """Represents a single page in the document."""
    page_number: int
    width: float
    height: float
    elements: List[ContentElement] = Field(default_factory=list)

class Document(BaseModel):
    """Represents a processed document."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    metadata: Dict[str, Any] = Field(default_factory=dict)
    pages: List[Page] = Field(default_factory=list)

class ParsingStrategy(str, Enum):
    """Strategies for LLM-based parsing."""
    VISUAL = "visual"   # Render page as image -> Vision Model
    DIRECT = "direct"   # Extract text/layout -> LLM (Text-based)
