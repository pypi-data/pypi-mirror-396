from abc import ABC, abstractmethod
import logging
import dotenv
from typing import overload, Literal
from inspect import signature, Signature
from typing import Any
import json
import hashlib
from pathlib import Path
dotenv.load_dotenv()
logger = logging.getLogger(__name__)


class BaseParser(ABC):
    _registry: dict[str, type["BaseParser"]] = {}

    def __init__(self):
        # Every instance gets a .name attribute
        self.name = getattr(self.__class__, "_parser_name", self.__class__.__name__)

    def __init_subclass__(cls, name: str | None = None, **kwargs):
        """Automatically register subclasses under a key."""
        super().__init_subclass__(**kwargs)
        key = name or cls.__name__.lower().replace("parser", "")
        BaseParser._registry[key] = cls
        BaseParser._registry.pop("", None)

    @abstractmethod
    def parse(self, text: str, include_pagenumbers: bool = False):
        pass

    def make_serializable(self, obj: Any) -> Any:
        if obj is None or isinstance(obj, (str, int, float, bool)):
            return obj
        if isinstance(obj, (list, tuple, set)):
            return [self.make_serializable(v) for v in obj]
        if isinstance(obj, dict):
            return {k: self.make_serializable(v) for k, v in sorted(obj.items())}
        if hasattr(obj, "__dict__"):
            return self.make_serializable(vars(obj))
        return f"{type(obj).__name__}:{repr(obj)}"

    def compute_hash(self, parameter:dict) -> str:

        attrs = {
            k: v
            for k, v in parameter.items()
            if k != "hash"
               and not k.startswith("_")
               and k not in ("client", "provider")
        }
        serializable = self.make_serializable(attrs)
        attrs_str = json.dumps(serializable, sort_keys=True, ensure_ascii=True)
        hashed = hashlib.sha256(attrs_str.encode()).hexdigest()[:8]
        return hashed

    @staticmethod
    def write_parameters(parameter: dict, folder_file_path: Path) -> None:
        folder_file_path.write_text(
            json.dumps(
                parameter,
                indent=2,
                sort_keys=True,
                ensure_ascii=True,
            ),
            encoding="utf-8",
        )


class Parser(BaseParser):
    """Factory + registry interface for all parsers."""

    def __new__(cls, config_or_dict: "Parameter | dict | str" = None, **kwargs) -> BaseParser:
        """
        Factory entrypoint.
        Allows calling Parser(...) directly to create the correct subclass.
        """
        return cls._create(config_or_dict, **kwargs)

    @classmethod
    def available_parsers(cls) -> None:
        """Print registered parsers and their init arguments."""
        import inspect
        result = {}
        for name, parser_cls in BaseParser._registry.items():
            sig = inspect.signature(parser_cls.__init__)
            result[name] = [p for p in sig.parameters if p != "self"]
        result.pop("", None)
        for key, values in result.items():
            print(f"{key} with parameters: {values}")

    # ---- Overloads for IDE autocomplete ----
    @overload
    @classmethod
    def _create(
            cls,
            *,
            provider_and_model: Literal["llamaparser:"],
            result_type: str,
            model: str,
            parse_mode: str,
            preserve_layout_alignment_across_pages: bool,
            merge_tables_across_pages_in_markdown: bool,
            hide_footers: bool,
            hide_headers: bool,
    ) -> "LlamaParser": ...

    @overload
    @classmethod
    def _create(
            cls,
            *,
            provider_and_model: Literal["mistralocr:ocr-large", "mistralocr:ocr-small"],
    ) -> "MistralOCRParser": ...

    @overload
    @classmethod
    def _create(
            cls,
            *,
            provider_and_model: Literal["langchain:gpt-3.5-turbo", "langchain:gpt-4"],
    ) -> "LangChainParser": ...

    # ---- Implementation ----
    @classmethod
    def _create(cls, config_or_dict: "Parameter | dict | str" = None, **kwargs) -> BaseParser:
        """
        Dynamically create parser instances.
        Supports: Parameter, dict, str (provider_and_model), or kwargs.
        """

        if config_or_dict is None:
            config_dict = {}
        elif hasattr(config_or_dict, "model_dump"):
            config_dict = config_or_dict.model_dump()
        elif isinstance(config_or_dict, dict):
            config_dict = config_or_dict
        elif isinstance(config_or_dict, str):  # shorthand
            config_dict = {"provider_and_model": config_or_dict}
        else:
            raise TypeError("Expected Parameter instance, dict, str, or None for config_or_dict")

        merged_args = {**config_dict, **kwargs}

        if "provider_and_model" not in merged_args:
            raise ValueError("provider_and_model must be specified, e.g. 'llamaparser:'")

        provider_and_model = str(merged_args.get("provider_and_model")).strip()

        if ":" not in provider_and_model:
            raise ValueError("provider_and_model must include a colon, e.g. 'llamaparser:'")

        provider, model = provider_and_model.split(":", 1)
        provider = (provider or "").strip().lower()
        model = (model or "").strip().lower()

        if not provider:
            raise ValueError(f"Invalid provider_and_model '{provider_and_model}': provider part is empty.")

        if provider not in BaseParser._registry:
            raise ValueError(f"Unknown parser '{provider}'. Available: {list(BaseParser._registry)}")

        parser_cls = BaseParser._registry[provider]

        # --- Filter valid constructor args ---
        sig = signature(parser_cls.__init__)
        valid_args = {k: v for k, v in merged_args.items() if k in sig.parameters and k != "self"}

        # Auto-fill common args
        if "model" in sig.parameters and "model" not in valid_args:
            valid_args["model"] = model
        if "provider_and_model" in sig.parameters and "provider_and_model" not in valid_args:
            valid_args["provider_and_model"] = provider_and_model

        # --- Check required args ---
        required_params = [
            p.name
            for p in sig.parameters.values()
            if p.name != "self"
               and p.default is Signature.empty
               and p.kind in (p.POSITIONAL_OR_KEYWORD, p.KEYWORD_ONLY)
        ]
        missing = [name for name in required_params if name not in valid_args]

        # Special rule: for llamaparser we allow empty `model`
        if provider != "llamaparser" and not model:
            missing.append("model")

        if missing:
            example = ""
            if provider == "llamaparser":
                example = "Example: Parser('llamaparser:', result_type='md', mode=True, extract_tables=True, parse_mode='parse_page_with_agent', model='anthropic-sonnet-4.5)"
            elif provider == "mistralocr":
                example = "Example: Parser('mistralocr:ocr-large')"
            elif provider == "langchain":
                example = "Example: Parser('langchain:gpt-3.5-turbo')"

            raise TypeError(
                f"{parser_cls.__name__} cannot be created because it is missing required argument(s): {', '.join(missing)}. {example}"
            )

        return parser_cls(**valid_args)

    @abstractmethod
    def parse(self, text: str, include_pagenumbers: bool = False):
        pass
