import os
import json
import logging
from pathlib import Path
from ..parser import BaseParser
from typing import Any

class LlamaParser(BaseParser, name="llamaparser"):
    def __init__(self, result_type: str, model: str, parse_mode: str, provider_and_model: str,
                 merge_tables_across_pages_in_markdown: bool, preserve_layout_alignment_across_pages: bool,
                 hide_footers: bool, hide_headers: bool) -> None:

        super().__init__()
        # Capture only input parameters
        self._input_params = {
            k: v
            for k, v in locals().items()
            if k not in ("self", "__class__", "__len__")
        }

        logging.info("Configuring LlamaParser (lazy init enabled)...")

        # Store configuration only
        self.result_type = result_type
        self.model = model
        self.parse_mode = parse_mode
        self.provider_and_model = provider_and_model
        self.merge_tables_across_pages_in_markdown = merge_tables_across_pages_in_markdown
        self.preserve_layout_alignment_across_pages = preserve_layout_alignment_across_pages
        self.hide_footers = hide_footers
        self.hide_headers = hide_headers
        self.hashed = self.compute_hash(self._input_params)
        # DO NOT CREATE LlamaParse HERE
        # It creates asyncio objects bound to the wrong loop
        self._parser = None

    def _lazy_init(self):
        """Initialize LlamaParse inside the worker thread event loop."""
        if self._parser is not None:
            return

        from llama_parse import LlamaParse, ResultType

        api_key = os.getenv("LLAMA-PARSER-API-TOKEN")
        if not api_key:
            raise EnvironmentError("Missing LLAMA-PARSER-API-TOKEN in .env file.")

        rt = self.result_type

        rt_lower = str(rt).lower()
        if rt_lower in ("md", "markdown"):
            rt = ResultType.MD
        elif rt_lower in ("json", "layout_json", "jsonl"):
            rt = ResultType.JSON

        # Construct the parser INSIDE the worker thread
        self._parser = LlamaParse(
            api_key=api_key,
            result_type=rt,
            model=self.model,
            parse_mode=self.parse_mode,
            merge_tables_across_pages_in_markdown=self.merge_tables_across_pages_in_markdown,
            preserve_layout_alignment_across_pages=self.preserve_layout_alignment_across_pages,
            hide_footers=self.hide_footers,
            hide_headers=self.hide_headers,
        )

        logging.info("LlamaParser initialized inside worker thread")

    def parse(self, file_path: Path, include_pagenumbers: bool = False) -> Any:
        # Ensure parser is created inside the thread event loop
        self._lazy_init()

        # Standard calls
        if not include_pagenumbers:
            documents = self._parser.load_data(str(file_path))
            return "\n".join(doc.text for doc in documents)

        # With page numbers
        documents = self._parser.parse(file_path)

        if self.result_type.lower() in ("md", "markdown"):
            return "\n".join(
                f"<PAGE_NUMBER {idx}>{page.md}</PAGE_NUMBER {idx}>"
                for idx, page in enumerate(documents.pages, start=1)
            )

        if self.result_type.lower() in ("json", "layout_json", "jsonl"):
            return documents.model_dump() if hasattr(documents, "model_dump") else documents

        return "\n".join(
            f"<PAGE_NUMBER {idx}>{page.text}</PAGE_NUMBER {idx}>"
            for idx, page in enumerate(documents.pages, start=1)
        )

    def __call__(self, file_path: Path) -> str:
        return self.parse(file_path)

    def write_json_hyperparameter(self, folder_file_path: Path) -> None:
        self.write_parameters(self._input_params, folder_file_path)
