import base64
import io
import os
from pathlib import Path
from typing import Union, List, Optional
import instructor
import litellm
from pydantic import BaseModel, Field
from krypton.schema import Document, Page, TextElement, TableElement, ImageElement, ContentElement, ParsingStrategy
from krypton.parser.base import BaseParser
from krypton.core.prompts.parser_prompts import PDF_PAGE_EXTRACTION_PROMPT
import pdfplumber
from pypdf import PdfReader, PdfWriter

class LLMPageContent(BaseModel):
    """Schema for LLM structured output for a single page."""
    elements: List[Union[TextElement, TableElement, ImageElement]] = Field(
        ..., description="List of content elements extracted from the page."
    )
    summary: Optional[str] = Field(None, description="Brief summary of the page content.")

class LLMParser(BaseParser):
    """
    High-fidelity PDF parser using LLMs via Instructor.
    Supports 'Visual' (Image-based) and 'Direct' (Text-based) strategies.
    """
    def __init__(self, model: str = "gpt-4o", api_key: Optional[str] = None):
        self.model = model
        self.client = instructor.from_litellm(litellm.completion)
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key 

    def parse(self, file_path: Union[str, Path], strategy: ParsingStrategy = ParsingStrategy.VISUAL) -> Document:
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        doc_model = Document(metadata={
            "filename": file_path.name, 
            "parser": "llm", 
            "model": self.model,
            "strategy": strategy.value
        })

        with pdfplumber.open(file_path) as pdf:
            for i, page in enumerate(pdf.pages):
                try:
                    content_payload = []
                    
                    # Construct message payload based on strategy
                    if strategy == ParsingStrategy.VISUAL:
                        # 1. Render page to image
                        pil_image = page.to_image(resolution=150).original
                        buffered = io.BytesIO()
                        pil_image.save(buffered, format="PNG")
                        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
                        data_url = f"data:image/png;base64,{img_str}"
                        
                        content_payload = [
                            {"type": "text", "text": PDF_PAGE_EXTRACTION_PROMPT},
                            {"type": "image_url", "image_url": {"url": data_url}}
                        ]
                        
                    elif strategy == ParsingStrategy.DIRECT:
                        # 1. Extract specific page as PDF bytes
                        # We re-open the file with pypdf to extract the page
                        reader = PdfReader(file_path)
                        writer = PdfWriter()
                        writer.add_page(reader.pages[i])
                        
                        pdf_bytes = io.BytesIO()
                        writer.write(pdf_bytes)
                        pdf_bytes.seek(0)
                        
                        pdf_base64 = base64.b64encode(pdf_bytes.getvalue()).decode("utf-8")
                        pdf_data_url = f"data:application/pdf;base64,{pdf_base64}"
                        
                        content_payload = [
                            {"type": "text", "text": PDF_PAGE_EXTRACTION_PROMPT},
                            {"type": "image_url", "image_url": {"url": pdf_data_url}}
                        ]

                    # 2. Call LLM
                    extraction: LLMPageContent = self.client.chat.completions.create(
                        model=self.model,
                        response_model=LLMPageContent,
                        messages=[
                            {
                                "role": "user",
                                "content": content_payload
                            }
                        ]
                    )
                    
                    # 3. Convert to internal Page model
                    page_model = Page(
                        page_number=i + 1,
                        width=float(page.width),
                        height=float(page.height),
                        elements=extraction.elements
                    )
                    doc_model.pages.append(page_model)

                except Exception as e:
                    print(f"Error parsing page {i+1} with LLM: {e}")
                    doc_model.pages.append(Page(page_number=i+1, width=float(page.width), height=float(page.height)))

        return doc_model
