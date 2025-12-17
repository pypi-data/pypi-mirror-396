import pdfplumber
from pathlib import Path
from typing import Union, List
import uuid
from krypton.schema import Document, Page, TextElement, TableElement
from krypton.parser.base import BaseParser

class GenericParser(BaseParser):
    """
    Fast, rule-based PDF parser using pdfplumber.
    Extracts text and simple tables.
    """

    def parse(self, file_path: Union[str, Path]) -> Document:
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        doc_model = Document(metadata={"filename": file_path.name})

        with pdfplumber.open(file_path) as pdf:
            for i, page in enumerate(pdf.pages):
                page_model = Page(
                    page_number=i + 1,
                    width=float(page.width),
                    height=float(page.height)
                )

                # 1. Extract Text
                text = page.extract_text()
                if text:
                    # Simple heuristic: split by double newlines for paragraphs
                    # This is very basic; can be improved
                    paragraphs = text.split('\n\n')
                    for para in paragraphs:
                        if para.strip():
                            page_model.elements.append(
                                TextElement(
                                    page_number=page_model.page_number,
                                    content=para.strip()
                                )
                            )

                # 2. Extract Tables
                tables = page.extract_tables()
                for table_data in tables:
                     # Filter None and handle types upfront
                    cleaned_data = [[str(cell) if cell is not None else "" for cell in row] for row in table_data]
                    
                    # simplistic markdown conversion
                    md_table = self._table_to_markdown(cleaned_data)
                    page_model.elements.append(
                        TableElement(
                            page_number=page_model.page_number,
                            content=md_table,
                            data=cleaned_data 
                        )
                    )

                doc_model.pages.append(page_model)

        return doc_model

    def _table_to_markdown(self, data: List[List[str]]) -> str:
        """Helper to convert list of lists to markdown table."""
        if not data:
            return ""
        
        # Data is already cleaned
        cleaned_data = data
        
        headers = cleaned_data[0]
        # If headers are empty implies no table or headless, but let's assume first row is header for now
        
        md = "| " + " | ".join(headers) + " |\n"
        md += "| " + " | ".join(["---"] * len(headers)) + " |\n"
        
        for row in cleaned_data[1:]:
            md += "| " + " | ".join(row) + " |\n"
            
        return md
