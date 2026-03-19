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
        import traceback

        tb = traceback.format_exc()
        print(f"ERROR GENERANDO PDF:\n{tb}", flush=True)
        raise HTTPException(status_code=500, detail=f"{str(e)}\n\nTraceback:\n{tb}")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/test-pdf")
def test_pdf(key: str = Security(verify_key)):
    """Genera un PDF mínimo para verificar que WeasyPrint funciona."""
    try:
        html_test = """<!DOCTYPE html>
<html><head><meta charset="UTF-8"></head>
<body>
<h1 style="color:red">WeasyPrint funciona</h1>
<p>Folio: BS-TEST-0001</p>
<table border="1">
  <tr><th>Producto</th><th>Precio</th></tr>
  <tr><td>Piedra Bali</td><td>$1,000.00</td></tr>
</table>
</body></html>"""
        pdf_bytes = HTML(string=html_test).write_pdf()
        pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")
        return {"pdf_base64": pdf_base64, "size_bytes": len(pdf_bytes)}
    except Exception:
        import traceback

        return {"error": traceback.format_exc()}
