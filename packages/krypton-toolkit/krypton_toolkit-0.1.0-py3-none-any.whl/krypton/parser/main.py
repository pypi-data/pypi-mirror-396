from pathlib import Path
from typing import Union, List, Literal
from krypton.schema import Document, ParsingStrategy
from krypton.parser.generic import GenericParser
from krypton.parser.llm import LLMParser

def parse(
    source: Union[str, Path],
    mode: Literal["generic", "llm"] = "generic",
    model_name: str = "gpt-4o",
    strategy: ParsingStrategy = ParsingStrategy.VISUAL,
    recursive: bool = False
) -> Union[Document, List[Document]]:
    """
    Main entry point to parse PDF files or directories.

    Args:
        source: Path to a PDF file or a directory containing PDFs.
        mode: Parsing mode ('generic' or 'llm').
        model_name: LLM model name (only used if mode='llm').
        strategy: Parsing strategy for LLM mode ('visual' or 'direct').
        recursive: Whether to search directories recursively.

    Returns:
        Document object (if source is file) or List[Document] (if source is dir).
    """
    source_path = Path(source)
    
    # Initialize Parser
    if mode == "llm":
        parser = LLMParser(model=model_name)
    else:
        parser = GenericParser()

    # Handle Directory
    if source_path.is_dir():
        pattern = "**/*.pdf" if recursive else "*.pdf"
        files = list(source_path.glob(pattern))
        documents = []
        for f in files:
            try:
                # Dispatch strategies if applicable
                if mode == "llm":
                    documents.append(parser.parse(f, strategy=strategy))
                else:
                    documents.append(parser.parse(f))
            except Exception as e:
                print(f"Failed to parse {f}: {e}")
        return documents

    # Handle File
    elif source_path.is_file() and source_path.suffix.lower() == ".pdf":
        if mode == "llm":
            return parser.parse(source_path, strategy=strategy)
        else:
            return parser.parse(source_path)
    
    else:
        raise ValueError(f"Invalid source: {source}. Must be a PDF file or directory.")
