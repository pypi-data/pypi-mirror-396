from .parser import Parser

# Import all parsers to trigger registration (side effect imports)
from .parsers.llama_parser import LlamaParser  # noqa: F401
from .parsers.mistral_parser import MistralOCRParser  # noqa: F401
from .parsers.langchain_parser import LangChainParser  # noqa: F401

__all__ = ["Parser"]