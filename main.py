import base64
import os

from fastapi import FastAPI, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
from weasyprint import HTML

app = FastAPI(title="Bali Stone PDF Service")

API_KEY = os.environ["PDF_API_KEY"]
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)


def verify_key(key: str = Security(api_key_header)):
    if key != API_KEY:
        raise HTTPException(status_code=403, detail="API key inválida")
    return key


class PDFRequest(BaseModel):
    html: str


@app.post("/generate")
def generate_pdf(req: PDFRequest, key: str = Security(verify_key)):
    try:
        pdf_bytes = HTML(string=req.html).write_pdf()
        pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")
        return {"pdf_base64": pdf_base64}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando PDF: {str(e)}")


@app.get("/health")
def health():
    return {"status": "ok"}
