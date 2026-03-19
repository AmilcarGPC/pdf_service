import base64
import os
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
from weasyprint import HTML

app = FastAPI(title="Bali Stone PDF Service")

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


def verify_key(key: str = Security(api_key_header)):
    if key != API_KEY:
        raise HTTPException(status_code=403, detail="API key inválida")
    return key


class ItemCotizacion(BaseModel):
    nombre: str
    medidas: Optional[str] = ""
    acabado: str
    cantidad_m2: float
    precio_unitario: float
    subtotal_linea: float
    nota: Optional[str] = ""


class CotizacionRequest(BaseModel):
    folio: str
    nombre_cliente: str
    correo_cliente: str
    telefono_cliente: Optional[str] = ""
    tipo_cliente: Optional[str] = ""
    nombre_proyecto: Optional[str] = ""
    ciudad_entrega: Optional[str] = ""
    items: List[ItemCotizacion]
    subtotal_mxn: float
    descuento_mxn: float = 0
    descuento_pct: float = 0
    iva_mxn: float
    envio_mxn: float = 0
    total_mxn: float
    fecha_vencimiento: str


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

    filas = ""
    for item in d.items:
        medidas = (
            f'<br/><span style="font-size:11px;color:#8a7a6a">{item.medidas}</span>'
            if item.medidas
            else ""
        )
        nota = (
            f'<br/><span style="font-size:11px;color:#8a7a6a;font-style:italic">{item.nota}</span>'
            if item.nota
            else ""
        )
        filas += f"""
        <tr style="background:#faf8f5">
          <td style="padding:10px 12px;border-bottom:1px solid #f0ebe4;font-size:13px">
            <strong style="color:#1a1a1a;font-weight:500">{item.nombre}</strong>{medidas}{nota}
          </td>
          <td style="padding:10px 12px;border-bottom:1px solid #f0ebe4;font-size:12px;color:#5a4f45">{item.acabado}</td>
          <td style="padding:10px 12px;border-bottom:1px solid #f0ebe4;font-size:12px;color:#5a4f45;text-align:right">{item.cantidad_m2:.1f} m\u00b2</td>
          <td style="padding:10px 12px;border-bottom:1px solid #f0ebe4;font-size:12px;color:#5a4f45;text-align:right">{_fmt(item.precio_unitario)}</td>
          <td style="padding:10px 12px;border-bottom:1px solid #f0ebe4;font-size:13px;color:#1a1a1a;text-align:right;font-weight:500">{_fmt(item.subtotal_linea)}</td>
        </tr>"""

    descuento_row = ""
    if float(d.descuento_mxn or 0) > 0:
        descuento_row = f"""
        <tr>
          <td colspan="4" style="text-align:right;padding:4px 12px;font-size:12px;color:#7a9a6a">Descuento ({int(d.descuento_pct)}%)</td>
          <td style="text-align:right;padding:4px 12px;font-size:12px;color:#7a9a6a">\u2212 {_fmt(d.descuento_mxn)}</td>
        </tr>"""

    envio_row = ""
    if float(d.envio_mxn or 0) > 0:
        envio_row = f"""
        <tr>
          <td colspan="4" style="text-align:right;padding:4px 12px;font-size:12px;color:#5a4f45">Flete estimado</td>
          <td style="text-align:right;padding:4px 12px;font-size:12px;color:#5a4f45">{_fmt(d.envio_mxn)}</td>
        </tr>"""

    telefono_row = f"<br/>{d.telefono_cliente}" if d.telefono_cliente else ""
    tipo_badge = (
        f'<br/><span style="font-size:9px;letter-spacing:.1em;text-transform:uppercase;background:#f5f0ea;color:#8a7a6a;padding:2px 8px;border-radius:10px">{d.tipo_cliente}</span>'
        if d.tipo_cliente
        else ""
    )

    proyecto_td = ""
    if d.nombre_proyecto or d.ciudad_entrega:
        entrega = (
            f'<br/><span style="font-size:12px;color:#5a4f45">Entrega en: {d.ciudad_entrega}</span>'
            if d.ciudad_entrega
            else ""
        )
        proyecto_td = f"""
        <td style="vertical-align:top;width:50%;padding-left:20px">
          <div style="font-size:10px;letter-spacing:.12em;text-transform:uppercase;color:#8a7a6a;margin-bottom:6px">Proyecto</div>
          <div style="font-size:13px;color:#1a1a1a;font-weight:500">{d.nombre_proyecto or "\u2014"}{entrega}</div>
        </td>"""

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: #fff; font-family: 'Inter', Helvetica, Arial, sans-serif;
         color: #1a1a1a; font-size: 13px; line-height: 1.6; }}
  @page {{ size: A4; margin: 48px 52px; }}
</style>
</head>
<body>

<table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:32px">
  <tr>
    <td style="vertical-align:top">
      <div style="width:32px;height:3px;background:#c9b99a;border-radius:2px;margin-bottom:14px"></div>
      <div style="font-size:22px;font-weight:600;letter-spacing:.04em;color:#1a1a1a">BALI STONE</div>
      <div style="font-size:10px;letter-spacing:.18em;text-transform:uppercase;color:#8a7a6a;margin-top:2px">Piedras volc\u00e1nicas de Indonesia</div>
    </td>
    <td style="vertical-align:top;text-align:right">
      <div style="font-size:10px;letter-spacing:.12em;text-transform:uppercase;color:#8a7a6a">Cotizaci\u00f3n</div>
      <div style="font-size:18px;font-weight:600;color:#1a1a1a;margin-top:2px">{d.folio}</div>
      <div style="font-size:11px;color:#8a7a6a;margin-top:3px">{hoy}</div>
    </td>
  </tr>
</table>

<table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:24px">
  <tr><td style="height:1px;background:#c9b99a;font-size:0">&nbsp;</td></tr>
</table>

<table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:32px">
  <tr>
    <td style="vertical-align:top;width:50%">
      <div style="font-size:10px;letter-spacing:.12em;text-transform:uppercase;color:#8a7a6a;margin-bottom:6px">Cliente</div>
      <div style="font-size:13px;color:#1a1a1a;font-weight:500">{d.nombre_cliente}</div>
      <div style="font-size:12px;color:#5a4f45;margin-top:1px">{d.correo_cliente}{telefono_row}{tipo_badge}</div>
    </td>
    {proyecto_td}
  </tr>
</table>

<div style="font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:#8a7a6a;margin-bottom:10px">Productos cotizados</div>

<table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;margin-bottom:24px">
  <thead>
    <tr style="border-bottom:1.5px solid #c9b99a">
      <th style="text-align:left;font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:#8a7a6a;padding:0 12px 10px 12px;font-weight:500;width:36%">Producto</th>
      <th style="text-align:left;font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:#8a7a6a;padding:0 12px 10px;font-weight:500">Acabado</th>
      <th style="text-align:right;font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:#8a7a6a;padding:0 12px 10px;font-weight:500">Cantidad</th>
      <th style="text-align:right;font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:#8a7a6a;padding:0 12px 10px;font-weight:500">Precio / m\u00b2</th>
      <th style="text-align:right;font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:#8a7a6a;padding:0 12px 10px;font-weight:500">Subtotal</th>
    </tr>
  </thead>
  <tbody>{filas}</tbody>
  <tfoot>
    <tr><td colspan="5" style="padding:8px 0;font-size:0">&nbsp;</td></tr>
    <tr>
      <td colspan="4" style="text-align:right;padding:4px 12px;font-size:12px;color:#5a4f45">Subtotal</td>
      <td style="text-align:right;padding:4px 12px;font-size:12px;color:#5a4f45">{_fmt(d.subtotal_mxn)}</td>
    </tr>
    {descuento_row}
    <tr>
      <td colspan="4" style="text-align:right;padding:4px 12px;font-size:12px;color:#5a4f45">IVA (16%)</td>
      <td style="text-align:right;padding:4px 12px;font-size:12px;color:#5a4f45">{_fmt(d.iva_mxn)}</td>
    </tr>
    {envio_row}
    <tr style="border-top:1.5px solid #c9b99a">
      <td colspan="4" style="text-align:right;padding:10px 12px 4px;font-size:14px;font-weight:600;color:#1a1a1a">Total</td>
      <td style="text-align:right;padding:10px 12px 4px;font-size:14px;font-weight:600;color:#1a1a1a">{_fmt(d.total_mxn)}</td>
    </tr>
  </tfoot>
</table>

<table width="100%" cellpadding="0" cellspacing="0" style="border-top:1px solid #f0ebe4;padding-top:20px;margin-top:32px">
  <tr>
    <td style="vertical-align:bottom;font-size:11px;color:#8a7a6a;line-height:1.5;width:65%">
      Los precios est\u00e1n expresados en MXN. El flete es un estimado sujeto a confirmaci\u00f3n.
      Esta cotizaci\u00f3n no constituye un pedido en firme.
    </td>
    <td style="vertical-align:bottom;text-align:right">
      <div style="font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:#8a7a6a">Vigente hasta</div>
      <div style="font-size:13px;font-weight:500;color:#1a1a1a;margin-top:3px">{vence}</div>
    </td>
  </tr>
</table>

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
