import os
import time
import uuid
import hmac
import hashlib
import base64
import requests
from pathlib import Path
from dotenv import load_dotenv
from modules.utils import limpar_e_comparar_nomes

env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

APP_KEY    = os.getenv("SOLPLANET_ID")
APP_SECRET = os.getenv("SOLPLANET_SECRET")
TOKEN      = os.getenv("SOLPLANET_TOKEN")

BASE_URL        = "https://ap-southeast-1-api-genergal.aisweicloud.com"
_PATH           = "/pro/getPlanListPro"
_PATH_OVERVIEW  = "/pro/getPlantOverviewPro"
_METHOD         = "GET"
_PAGE_SIZE      = 50


def _gerar_assinatura(path, params, timestamp, nonce):
    headers_to_sign = {
        "X-Ca-Key":       APP_KEY,
        "X-Ca-Nonce":     nonce,
        "X-Ca-Timestamp": str(timestamp),
    }

    string_to_sign = f"{_METHOD}\napplication/json\n\n\n\n"
    for key in sorted(headers_to_sign.keys()):
        string_to_sign += f"{key}:{headers_to_sign[key]}\n"

    url_part = path
    if params:
        query_string = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
        url_part += f"?{query_string}"
    string_to_sign += url_part

    signature = base64.b64encode(
        hmac.new(
            APP_SECRET.encode("utf-8"),
            string_to_sign.encode("utf-8"),
            hashlib.sha256,
        ).digest()
    ).decode("utf-8")
    return signature


def _buscar_pagina(page_num):
    params = {
        "token":    TOKEN,
        "pageNum":  page_num,
        "pageSize": _PAGE_SIZE,
        "order":    0,
    }
    timestamp = int(time.time() * 1000)
    nonce     = str(uuid.uuid4())

    headers = {
        "Accept":                  "application/json",
        "X-Ca-Key":                APP_KEY,
        "X-Ca-Timestamp":          str(timestamp),
        "X-Ca-Nonce":              nonce,
        "X-Ca-Signature-Headers":  "X-Ca-Key,X-Ca-Nonce,X-Ca-Timestamp",
        "X-Ca-Stage":              "RELEASE",
        "X-Ca-Signature":          _gerar_assinatura(_PATH, params, timestamp, nonce),
    }

    r = requests.get(f"{BASE_URL}{_PATH}", params=params, headers=headers, timeout=15)
    r.raise_for_status()
    return r.json()


def _buscar_overview(apikey):
    """Chama getPlantOverviewPro para uma usina específica e retorna o JSON bruto."""
    params = {
        "token":  TOKEN,
        "apikey": apikey,
    }
    timestamp = int(time.time() * 1000)
    nonce     = str(uuid.uuid4())

    headers = {
        "Accept":                  "application/json",
        "X-Ca-Key":                APP_KEY,
        "X-Ca-Timestamp":          str(timestamp),
        "X-Ca-Nonce":              nonce,
        "X-Ca-Signature-Headers":  "X-Ca-Key,X-Ca-Nonce,X-Ca-Timestamp",
        "X-Ca-Stage":              "RELEASE",
        "X-Ca-Signature":          _gerar_assinatura(_PATH_OVERVIEW, params, timestamp, nonce),
    }

    r = requests.get(f"{BASE_URL}{_PATH_OVERVIEW}", params=params, headers=headers, timeout=15)
    r.raise_for_status()
    return r.json()


# ─── COLETA DE DADOS ──────────────────────────────────────────────────────────

def buscar_dados_completos():
    """Retorna a lista completa de usinas da conta Solplanet."""
    import math

    if not all([APP_KEY, APP_SECRET, TOKEN]):
        print("[Solplanet] Variáveis de ambiente ausentes no .env.")
        return []

    todas = []
    pagina = 1
    total_paginas = None

    while True:
        try:
            resultado = _buscar_pagina(pagina)
        except Exception as e:
            print(f"[Solplanet] Erro ao buscar usinas (página {pagina}): {e}")
            break

        if resultado.get("status") != 200:
            print(f"[Solplanet] Erro da API: {resultado.get('info')} (código {resultado.get('status')})")
            break

        data = resultado.get("data", {})
        lote = data.get("result", [])
        if not lote:
            break

        todas.extend(lote)

        # Na primeira iteração, descobre o total de páginas pelos metadados da API
        if total_paginas is None:
            if "pages" in data:
                total_paginas = int(data["pages"])
            elif "total" in data and data["total"]:
                total_paginas = math.ceil(int(data["total"]) / _PAGE_SIZE)

        if total_paginas is not None:
            if pagina >= total_paginas:
                break
        elif len(lote) < _PAGE_SIZE:
            # Fallback: se a API não fornece metadados, lote incompleto = última página
            break

        pagina += 1

    print(f"[Solplanet] {len(todas)} usinas carregadas. Buscando geração mensal...")
    for usina in todas:
        apikey = usina.get("apikey")
        if not apikey:
            usina["e_month"] = None
            continue
        try:
            overview = _buscar_overview(apikey)
            if overview.get("status") == 200:
                e_month_obj = overview.get("data", {}).get("E-Month", {})
                usina["e_month"] = e_month_obj.get("value")
            else:
                usina["e_month"] = None
        except Exception as e:
            print(f"[Solplanet] Erro ao buscar overview de '{usina.get('name')}': {e}")
            usina["e_month"] = None

    print(f"[Solplanet] Cache pronto: {len(todas)} usinas com dados de geração.")
    return todas


# ─── TRADUÇÃO DE STATUS ───────────────────────────────────────────────────────

def traduzir_status(nome_cliente, lista_solplanet):
    """
    Localiza a usina pelo nome (case-insensitive, bidirecional) e retorna
    (status, last_update, etoday, e_month).

    Mapeamento do campo 'status' da API Solplanet:
      1 → On-line
      0 → Off-line
      2 → Alarme
    """
    for usina in lista_solplanet:
        nome_api = usina.get("name") or ""

        if limpar_e_comparar_nomes(nome_cliente, nome_api):
            estado      = usina.get("status")
            last_update = usina.get("updateDate") or usina.get("lastUploadTime") or ""
            etoday      = usina.get("etoday")
            e_month     = usina.get("e_month")

            if estado == 1:
                return "On-line", last_update, etoday, e_month
            if estado == 0:
                return "Off-line", last_update, etoday, e_month
            if estado == 2:
                return "Alarme", last_update, etoday, e_month
            status_str = f"Sem dados ({estado})" if estado is not None else "Sem dados"
            return status_str, last_update, etoday, e_month

    return "Não encontrado", "", None, None
