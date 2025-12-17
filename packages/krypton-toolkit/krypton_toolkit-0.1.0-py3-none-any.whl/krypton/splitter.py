from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from krypton.schema import Document, TextElement, TableElement, ImageElement

class Chunk(BaseModel):
    id: str = Field(..., description="Unique ID of the chunk")
    content: str = Field(..., description="Text content of the chunk")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata including source page, element IDs, etc.")

class Splitter:
    """Module for splitting Documents into Chunks."""
    
    @staticmethod
    def _flatten_document(doc: Document) -> List[Dict[str, Any]]:
        """
        Flatten document into a list of processable text units with metadata.
        Returns list of dicts: {'text': str, 'page': int, 'type': str}
        """
        flat_content = []
        for page in doc.pages:
            for element in page.elements:
                text = ""
                if isinstance(element, TextElement):
                    text = element.content
                elif isinstance(element, TableElement):
                    text = element.content # Markdown representation
                elif isinstance(element, ImageElement):
                    text = f"[IMAGE: {element.caption or 'No description'}]"
                
                if text:
                    flat_content.append({
                        "text": text,
                        "page": page.page_number,
                        "type": element.type
                    })
        return flat_content

    @staticmethod
    def fixed_size_split(doc: Document, chunk_size: int = 1000, overlap: int = 100) -> List[Chunk]:
        """
        Splits document into chunks of fixed character length with overlap.
        Preserves some metadata about the source page range.
        """
        flat = Splitter._flatten_document(doc)
        full_text = ""
        # Map character indices to metadata (simplified)
        # For MVP, we'll just concatenate and split text, effectively losing some granular metadata mapping,
        # but advanced mapping is complex.
        
        # Better approach for MVP: Iterate elements and greedy-pack them.
        chunks = []
        current_chunk_text = ""
        current_metadata = {"pages": set()}
        
        for item in flat:
            text = item['text']
            page = item['page']
            
            # If adding this item exceeds chunk size, finalize current chunk
            if len(current_chunk_text) + len(text) > chunk_size and current_chunk_text:
                chunks.append(Chunk(
                    id=f"chunk-{len(chunks)+1}",
                    content=current_chunk_text,
                    metadata={"pages": list(current_metadata["pages"])}
                ))
                # Start new chunk with overlap (naive implementation: overlap is hard with discrete elements)
                # For strict fixed size with overlap, we'd act on the pure string.
                # Let's switch to string sliding window for "Fixed Size" compliance.
                current_chunk_text = ""
                current_metadata = {"pages": set()}
            
            current_chunk_text += text + "\n\n"
            current_metadata["pages"].add(page)
        
        # Add remainder
        if current_chunk_text:
            chunks.append(Chunk(
                id=f"chunk-{len(chunks)+1}",
                content=current_chunk_text,
                metadata={"pages": list(current_metadata["pages"])}
            ))
            
        return chunks

    @staticmethod
    def semantic_split(doc: Document) -> List[Chunk]:
        """
        Splits document based on semantic boundaries (pages/sections).
        For MVP, groups by Page.
        """
        chunks = []
        for page in doc.pages:
            page_text = []
            for element in page.elements:
                if isinstance(element, TextElement):
                    page_text.append(element.content)
                elif isinstance(element, TableElement):
                    page_text.append(element.content)
                elif isinstance(element, ImageElement):
                    page_text.append(f"[Image: {element.caption}]")
            
            content = "\n\n".join(page_text)
            if content.strip():
                chunks.append(Chunk(
                    id=f"page-{page.page_number}",
                    content=content,
                    metadata={"page": page.page_number}
                ))
        return chunks
