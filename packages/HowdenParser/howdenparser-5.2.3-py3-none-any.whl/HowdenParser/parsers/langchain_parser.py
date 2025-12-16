from pathlib import Path
from ..parser import BaseParser



class LangChainParser(BaseParser, name="langchain"):
    def __init__(self, provider_and_model: str):
        from langchain.llms import OpenAI
        self.model = provider_and_model.split(":")[1]
        self.model = OpenAI(model_name=self.model)

    def parse(self, text: str) -> dict:
        response = self.model(text)
        return {"source": "LangChain", "output": response}

    def __call__(self, file_path: Path) -> str:
        return self.parse(file_path)

