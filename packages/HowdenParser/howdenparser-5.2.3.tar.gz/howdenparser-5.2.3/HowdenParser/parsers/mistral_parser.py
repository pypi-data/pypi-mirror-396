import os
from pathlib import Path
from ..parser import BaseParser
from PyPDF2 import PdfReader


class MistralOCRParser(BaseParser, name="mistralocr"):
    def __init__(self, provider_and_model: str) -> None:
        from mistralai import Mistral
        self.model = provider_and_model.split(":")[1]
        self.current_cost: float = 0.0
        self.total_cost_euro: float = 0.0
        api_key = os.getenv("MISTRAL-OCR-API-TOKEN")
        if not api_key:
            raise EnvironmentError("Missing MISTRAL-OCR-API-TOKEN in .env file.")
        self.client = Mistral(api_key=api_key)

    def parse(self, file_path: Path) -> str:
        def upload_pdf(filename):
            uploaded_pdf = self.client.files.upload(
                file={"file_name": filename, "content": open(filename, "rb")},
                purpose="ocr",
            )
            signed_url = self.client.files.get_signed_url(file_id=uploaded_pdf.id)
            return signed_url.url

        ocr_response = self.client.ocr.process(
            model=self.model,
            document={"type": "document_url", "document_url": upload_pdf(file_path)},
            include_image_base64=True,
        )
        self.current_cost = 1 / 1000 * self._count_pages(file_path)
        self.total_cost_euro += self.current_cost
        return "\n".join(doc.markdown for doc in ocr_response.pages)

    def __call__(self, file_path: Path) -> str:
        return self.parse(file_path)

    @staticmethod
    def _count_pages(file_path: Path) -> int:
        reader = PdfReader(str(file_path))
        return len(reader.pages)

