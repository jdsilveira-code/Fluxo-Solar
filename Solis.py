import hashlib
import hmac
import base64
import datetime
import requests
import json
import locale
import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

API_ID = os.getenv("SOLIS_API_ID")
API_SECRET = os.getenv("SOLIS_API_SECRET")
API_URL = "https://www.soliscloud.com:13333"


def _fetch_page(page_no):
    resource_path = "/v1/api/userStationList"
    payload = {"pageNo": page_no, "pageSize": 100}
    body = json.dumps(payload, separators=(',', ':'))
    content_type = "application/json"

    md5_hash = hashlib.md5(body.encode('utf-8')).digest()
    content_md5 = base64.b64encode(md5_hash).decode('utf-8')

    try:
        locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')
    except:
        locale.setlocale(locale.LC_TIME, 'en_US')

    now = datetime.datetime.now(datetime.timezone.utc)
    date_gmt = now.strftime("%a, %d %b %Y %H:%M:%S GMT")

    sign_str = f"POST\n{content_md5}\n{content_type}\n{date_gmt}\n{resource_path}"
    hashed = hmac.new(API_SECRET.encode('utf-8'), sign_str.encode('utf-8'), hashlib.sha1).digest()
    signature = base64.b64encode(hashed).decode('utf-8')

    headers = {
        "Content-MD5": content_md5,
        "Content-Type": content_type,
        "Date": date_gmt,
        "Authorization": f"API {API_ID}:{signature}"
    }

    response = requests.post(API_URL + resource_path, headers=headers, data=body)
    return response.json()


def buscar_dados_completos():
    """Baixa todas as usinas da Solis percorrendo a paginação."""
    todas_estacoes = []
    pagina = 1
    while True:
        res = _fetch_page(pagina)
        if res.get("code") == "0":
            records = res.get("data", {}).get("page", {}).get("records", [])
            todas_estacoes.extend(records)
            total_paginas = res.get("data", {}).get("page", {}).get("pages", 1)
            if pagina >= total_paginas:
                break
            pagina += 1
        else:
            break
    return todas_estacoes


def traduzir_status(nome_cliente, lista_solis):
    """
    Filtra o status e padroniza para o retorno do sistema.
    Retorna uma tupla (str_status, str_last_update).

    Mapeamento de status Solis:
      1 = On-line
      2 = Off-line
      3 = Alarme
    """
    for estacao in lista_solis:
        nome_api = estacao.get("stationName", "")
        if nome_cliente.strip().lower() in nome_api.lower():
            estado = estacao.get("state")
            # dataTimestamp vem em milissegundos (Unix), convertemos para string legível
            ts = estacao.get("dataTimestamp")
            if ts:
                try:
                    dt = datetime.datetime.fromtimestamp(int(ts) / 1000)
                    last_update = dt.strftime("%Y-%m-%d %H:%M:%S")
                except Exception:
                    last_update = ""
            else:
                last_update = ""

            if estado == 1:
                return "On-line", last_update
            if estado == 2:
                return "Off-line", last_update
            if estado == 3:
                return "Alarme", last_update
            return f"Erro ({estado})", last_update

    return "Não encontrado", ""
