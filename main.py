import base64
import os
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Security
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel, Field
from weasyprint import HTML

app = FastAPI(title="Bali Stone PDF Service")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    print(f"\n--- VALIDATION ERROR ---\n{exc}\n------------------------\n", flush=True)
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )


API_KEY = os.environ["PDF_API_KEY"]
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)

MESES = {
    1: "enero",
    2: "febrero",
    3: "marzo",
    4: "abril",
    5: "mayo",
    6: "junio",
    7: "julio",
    8: "agosto",
    9: "septiembre",
    10: "octubre",
    11: "noviembre",
    12: "diciembre",
}

LOGO_DATA_URI = "data:image/png;base64,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"


try:
    with open("logo.png", "rb") as _logo_file:
        LOGO_DATA_URI = "data:image/png;base64," + base64.b64encode(
            _logo_file.read()
        ).decode("utf-8")
except Exception as e:
    print(f"Error loading logo: {e}")


def verify_key(key: str = Security(api_key_header)):
    if key != API_KEY:
        raise HTTPException(status_code=403, detail="API key inválida")
    return key


class ItemCotizacion(BaseModel):
    nombre: str = Field(..., max_length=200)
    medidas: Optional[str] = Field(default="", max_length=100)
    acabado: str = Field(..., max_length=100)
    cantidad_m2: float
    precio_unitario: float
    subtotal_linea: float
    nota: Optional[str] = Field(default="", max_length=1000)


class CotizacionRequest(BaseModel):
    folio: str = Field(..., max_length=50)
    nombre_cliente: str = Field(..., max_length=150)
    correo_cliente: str = Field(..., max_length=150)
    telefono_cliente: Optional[str] = Field(default="", max_length=50)
    tipo_cliente: Optional[str] = Field(default="", max_length=100)
    nombre_proyecto: Optional[str] = Field(default="", max_length=200)
    ciudad_entrega: Optional[str] = Field(default="", max_length=150)
    items: List[ItemCotizacion] = Field(..., max_length=150)
    subtotal_mxn: float
    descuento_mxn: float = 0
    descuento_pct: float = 0
    iva_mxn: float
    envio_mxn: float = 0
    total_mxn: float
    fecha_vencimiento: str = Field(..., max_length=20)


def _fecha_larga(iso: str) -> str:
    try:
        d = datetime.strptime(iso, "%Y-%m-%d")
        return f"{d.day} de {MESES[d.month]}, {d.year}"
    except Exception:
        return iso


def _fmt(v) -> str:
    try:
        return f"${float(v):,.2f}"
    except Exception:
        return "$0.00"


def build_html(d: CotizacionRequest) -> str:
    hoy = _fecha_larga(datetime.now().strftime("%Y-%m-%d"))
    vence = _fecha_larga(d.fecha_vencimiento)

    # ── Filas de productos ────────────────────────────────────
    filas = ""
    for item in d.items:
        medidas = (
            f'<div class="prod-detail">{item.medidas}</div>' if item.medidas else ""
        )
        nota = (
            f'<div class="prod-detail" style="font-style:italic">{item.nota}</div>'
            if item.nota
            else ""
        )

        filas += f"""
      <tr>
        <td>
          <div class="prod-name">{item.nombre}</div>
          {medidas}{nota}
        </td>
        <td>{item.acabado}</td>
        <td class="right">{item.cantidad_m2:.0f} m\u00b2</td>
        <td class="right">{_fmt(item.precio_unitario)}</td>
        <td class="right" style="color:#0A523B;font-weight:700">{_fmt(item.subtotal_linea)}</td>
      </tr>"""

    descuento_row = ""
    if float(d.descuento_mxn or 0) > 0:
        descuento_row = f'<div class="total-row discount"><span>Descuento ({int(d.descuento_pct)}%)</span><span>\u2212 {_fmt(d.descuento_mxn)}</span></div>'

    envio_row = ""
    if float(d.envio_mxn or 0) > 0:
        envio_row = f'<div class="total-row"><span>Flete estimado</span><span>{_fmt(d.envio_mxn)}</span></div>'

    tel_row = (
        f'<div class="meta-sub">{d.telefono_cliente}</div>'
        if d.telefono_cliente
        else ""
    )
    badge = f'<span class="badge">{d.tipo_cliente}</span>' if d.tipo_cliente else ""

    proyecto_block = ""
    if d.nombre_proyecto or d.ciudad_entrega:
        entrega = (
            f'<div class="meta-sub">Entrega en: {d.ciudad_entrega}</div>'
            if d.ciudad_entrega
            else ""
        )
        nombre_proy = d.nombre_proyecto or ""
        proyecto_block = f"""
    <div class="meta-block">
      <div class="meta-label">Proyecto</div>
      <div class="meta-value">{nombre_proy}</div>
      {entrega}
    </div>"""

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Raleway:wght@400;500;600;700&family=Lato:wght@400;700&display=swap');
*{{box-sizing:border-box;margin:0;padding:0}}
@page {{ size: A4; margin: 48px 52px; }}
body{{background:#fff;font-family:'Lato',sans-serif;color:#1A1A1A;font-size:13px;line-height:1.6}}
.header{{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:40px}}
.brand-name{{font-family:'Raleway',sans-serif;font-size:22px;font-weight:700;letter-spacing:.04em;color:#1A1A1A}}
.brand-sub{{font-size:10px;letter-spacing:.18em;text-transform:uppercase;color:#8C8E76;font-weight:600;margin-top:2px;font-family:'Raleway',sans-serif}}
.folio-block{{text-align:right}}
.folio-label{{font-family:'Raleway',sans-serif;font-size:10px;letter-spacing:.12em;text-transform:uppercase;color:#5A5A5A}}
.folio-num{{font-family:'Raleway',sans-serif;font-size:18px;font-weight:700;color:#1A1A1A;margin-top:2px}}
.folio-date{{font-size:11px;color:#5A5A5A;margin-top:3px}}
.divider{{height:1px;background:#CDCEB5;margin:0 0 28px}}
.meta{{display:flex;justify-content:space-between;margin-bottom:36px;width:100%}}
.meta-block{{width:48%}}
.meta-label{{font-family:'Raleway',sans-serif;font-size:10px;letter-spacing:.12em;text-transform:uppercase;color:#5A5A5A;margin-bottom:6px;font-weight:600}}
.meta-value{{font-family:'Raleway',sans-serif;font-size:13px;color:#1A1A1A;font-weight:600}}
.meta-sub{{font-size:12px;color:#5A5A5A;margin-top:1px}}
.section-title{{font-family:'Raleway',sans-serif;font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:#0A523B;margin-bottom:12px;font-weight:700}}
table{{width:100%;border-collapse:collapse;margin-bottom:28px}}
thead tr{{border-bottom:1.5px solid #0A523B}}
thead th{{text-align:left;font-family:'Raleway',sans-serif;font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:#5A5A5A;padding:0 10px 10px 10px;font-weight:600}}
thead th:first-child{{padding-left:0}}
thead th:last-child{{padding-right:0}}
thead th.right{{text-align:right}}
tbody tr{{border-bottom:1px solid #CDCEB5}}
tbody td{{padding:12px 10px;vertical-align:top;color:#5A5A5A;font-size:13px}}
tbody td:first-child{{padding-left:0}}
tbody td:last-child{{padding-right:0}}
tbody td.right{{text-align:right}}
.prod-name{{font-weight:700;color:#1A1A1A;font-size:13px;font-family:'Lato',sans-serif}}
.prod-detail{{font-size:11px;color:#5A5A5A;margin-top:2px}}
.totals{{display:flex;justify-content:flex-end}}
.totals-block{{width:260px}}
.total-row{{display:flex;justify-content:space-between;padding:5px 0;font-size:12px;color:#5A5A5A}}
.total-row.main{{padding:10px 0;font-size:14px;font-weight:700;color:#0A523B;border-top:1.5px solid #0A523B;margin-top:4px;font-family:'Raleway',sans-serif}}
.total-row.discount{{color:#0A523B}}
.footer{{position:absolute;bottom:0;left:0;right:0;padding-top:24px;border-top:1px solid #CDCEB5;display:flex;justify-content:space-between;align-items:flex-end}}
.footer-note{{font-size:11px;color:#5A5A5A;max-width:320px;line-height:1.5}}
.validity-label{{font-family:'Raleway',sans-serif;font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:#5A5A5A}}
.validity-date{{font-family:'Raleway',sans-serif;font-size:13px;font-weight:700;color:#0A523B;margin-top:3px}}
.accent-bar{{width:32px;height:3px;background:#CDCEB5;border-radius:2px;margin-bottom:16px}}
.badge{{display:inline-block;font-family:'Raleway',sans-serif;font-size:9px;letter-spacing:.1em;text-transform:uppercase;background:#edf3f0;color:#0A523B;padding:2px 8px;border-radius:20px;margin-top:4px;font-weight:600}}
.aviso{{border-left:3px solid #CDCEB5;padding:10px 14px;font-size:11px;color:#5A5A5A;line-height:1.6;margin:28px 0;background:#fafaf8}}
.aviso strong{{color:#0A523B;font-family:'Raleway',sans-serif;font-weight:700}}
</style>
</head>
<body>
  <div class="header">
    <div class="brand">
      <div class="accent-bar"></div>
      <img src="{LOGO_DATA_URI}" style="height:21px;width:auto;display:block;margin-bottom:5px" alt="Bali Stone"/>
      <div class="brand-sub">Elegancia Natural</div>
    </div>
    <div class="folio-block">
      <div class="folio-label">Cotizaci\u00f3n</div>
      <div class="folio-num">{d.folio}</div>
      <div class="folio-date">{hoy}</div>
    </div>
  </div>
  <div class="divider"></div>
  <div class="meta">
    <div class="meta-block">
      <div class="meta-label">Cliente</div>
      <div class="meta-value">{d.nombre_cliente}</div>
      <div class="meta-sub">{d.correo_cliente}</div>
      {tel_row}
      {badge}
    </div>
    {proyecto_block}
  </div>
  <div class="section-title">Productos cotizados</div>
  <table>
    <thead>
      <tr>
        <th style="width:40%">Producto</th>
        <th>Acabado</th>
        <th class="right">Cantidad</th>
        <th class="right">Precio / m\u00b2</th>
        <th class="right">Subtotal</th>
      </tr>
    </thead>
    <tbody>
      {filas}
    </tbody>
  </table>
  <div class="totals">
    <div class="totals-block">
      <div class="total-row"><span>Subtotal</span><span>{_fmt(d.subtotal_mxn)}</span></div>
      {descuento_row}
      <div class="total-row"><span>IVA (16%)</span><span>{_fmt(d.iva_mxn)}</span></div>
      {envio_row}
      <div class="total-row main"><span>Total</span><span>{_fmt(d.total_mxn)}</span></div>
    </div>
  </div>
  <div class="aviso">
    <strong>Importante:</strong> Esta cotizaci\u00f3n no garantiza disponibilidad ni reserva de material. Los productos se apartan \u00fanicamente una vez confirmado el pago.
  </div>
  <div class="footer">
    <div class="footer-note">Precios en MXN. Flete estimado sujeto a confirmaci\u00f3n. Esta cotizaci\u00f3n no constituye un pedido en firme.</div>
    <div class="validity">
      <div class="validity-label">Vigente hasta</div>
      <div class="validity-date">{vence}</div>
    </div>
  </div>
</body>
</html>"""


@app.post("/generate")
def generate_pdf(req: CotizacionRequest, key: str = Security(verify_key)):
    try:
        html = build_html(req)
        pdf_bytes = HTML(string=html).write_pdf()
        pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")
        return {"pdf_base64": pdf_base64}
    except Exception as e:
        import traceback

        tb = traceback.format_exc()
        print(f"ERROR:\n{tb}", flush=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/test-pdf")
def test_pdf(key: str = Security(verify_key)):
    try:
        html_test = """<!DOCTYPE html>
<html><head><meta charset="UTF-8"></head>
<body style="background:#fff;font-family:Raleway,sans-serif">
<h1 style="color:#0A523B">WeasyPrint OK</h1>
<p style="font-family:Lato,sans-serif;color:#5A5A5A">Raleway + Lato activos</p>
</body></html>"""
        pdf_bytes = HTML(string=html_test).write_pdf()
        return {"size_bytes": len(pdf_bytes)}
    except Exception:
        import traceback

        return {"error": traceback.format_exc()}
