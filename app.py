import os
from datetime import datetime
from html import escape

from flask import Flask, request

import read_value_yf

app = Flask(__name__)

DEFAULT_STOCK = os.getenv("STOCK", "GOOGL")
DEFAULT_START = "2020-01-01"

PAGE = """<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Stock Market - {ticker}</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 2rem; color: #222; }}
    table {{ border-collapse: collapse; font-size: .85rem; }}
    th, td {{ border: 1px solid #ccc; padding: .3rem .6rem; text-align: right; }}
    th {{ background: #f3f3f3; }}
    .meta {{ color: #666; font-size: .9rem; }}
    .error {{ color: #b00020; }}
  </style>
</head>
<body>
  <h1>Stock Market: {ticker}</h1>
  <p class="meta">Desde {start} hasta {end} &middot; Contenedor: {host} &middot; {now}</p>
  <form action="/stock" method="get">
    <input name="ticker" value="{ticker}" size="8" aria-label="Ticker">
    <input name="start" type="date" value="{start}" aria-label="Fecha inicial">
    <input name="end" type="date" value="{end_value}" aria-label="Fecha final">
    <button>Consultar</button>
  </form>
  {summary}
  {body}
</body>
</html>"""


def render(ticker, start, end):
    ticker = ticker.upper().strip()
    status = 200
    summary = ""
    try:
        data = read_value_yf.get_stock_data(start, ticker, end)
        if data.empty:
            body = f'<p class="error">No se encontraron datos para {escape(ticker)}.</p>'
        else:
            avg = data["Close"].mean()
            summary = f"<p><strong>Valor promedio de cierre:</strong> {avg:,.2f}</p>"
            body = data.to_html(float_format=lambda v: f"{v:,.2f}")
    except Exception as exc:  # Yahoo puede limitar peticiones o cambiar su API
        body = f'<p class="error">Error consultando Yahoo Finance: {escape(str(exc))}</p>'
        status = 502
    html = PAGE.format(
        ticker=escape(ticker),
        start=escape(start),
        end=escape(end or "hoy"),
        end_value=escape(end or ""),
        host=escape(os.uname().nodename),
        now=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        summary=summary,
        body=body,
    )
    return html, status


@app.route("/")
def hello_world():
    """Igual que el taller: datos de GOOGL (o $STOCK) desde 2020-01-01."""
    return render(DEFAULT_STOCK, DEFAULT_START, None)


@app.route("/stock")
@app.route("/stock/<ticker>")
def stock(ticker=None):
    ticker = ticker or request.args.get("ticker", DEFAULT_STOCK)
    start = request.args.get("start") or DEFAULT_START
    end = request.args.get("end") or None
    return render(ticker, start, end)


@app.route("/health")
def health():
    return {"status": "ok", "time": datetime.now().isoformat()}


if __name__ == "__main__":
    print(f"{datetime.now()}")
    app.run(host="0.0.0.0", port=5000)
