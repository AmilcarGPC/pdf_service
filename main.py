from fastapi import FastAPI, HTTPException, Security, Response
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
from weasyprint import HTML
import os

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
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": "inline; filename=cotizacion.pdf"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando PDF: {str(e)}")


@app.get("/health")
def health():
    return {"status": "ok"}
