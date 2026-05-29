import os
import time
import uuid
import hmac
import hashlib
import base64
import requests
from dotenv import load_dotenv

load_dotenv()

APP_KEY    = os.getenv("SOLPLANET_ID")
APP_SECRET = os.getenv("SOLPLANET_SECRET")
TOKEN      = os.getenv("SOLPLANET_TOKEN")

missing = [k for k, v in {"SOLPLANET_ID": APP_KEY, "SOLPLANET_SECRET": APP_SECRET, "SOLPLANET_TOKEN": TOKEN}.items() if not v]
if missing:
    raise EnvironmentError(f"Variáveis ausentes no .env: {', '.join(missing)}")

DOMAIN = "https://ap-southeast-1-api-genergal.aisweicloud.com"
PATH = "/pro/getPlanListPro"
METHOD = "GET"

def generate_signature(path, params, app_key, app_secret, timestamp, nonce):
    """
    Gera a assinatura conforme seções 4.3.2 e 4.3.3 da documentação.
    """
    # 1. Preparar Headers do Sistema que participam da assinatura
    # Conforme 4.2 e 4.3.2, headers X-Ca devem ser ordenados
    headers_to_sign = {
        "X-Ca-Key": app_key,
        "X-Ca-Nonce": nonce,
        "X-Ca-Timestamp": str(timestamp),
    }
    
    # 2. Construir StringToSign (Seção 4.3.2)
    # Formato: Method + \n + Accept + \n + MD5 + \n + Type + \n + Date + \n + Headers + Url
    accept = "application/json" # Recomendado na seção 2.1.4
    content_md5 = ""
    content_type = ""
    date = ""
    
    string_to_sign = f"{METHOD}\n{accept}\n{content_md5}\n{content_type}\n{date}\n"
    
    # Adicionar headers formatados (Seção 4.3.2.7)
    for key in sorted(headers_to_sign.keys()):
        string_to_sign += f"{key}:{headers_to_sign[key]}\n"
    
    # 3. Organizar URL (Path + Query Params ordenados) - Seção 4.3.2.Url
    url_part = path
    if params:
        sorted_params = sorted(params.items())
        query_string = "&".join([f"{k}={v}" for k, v in sorted_params])
        url_part += f"?{query_string}"
    
    string_to_sign += url_part

    # 4. Calcular HMAC-SHA256 (Seção 4.3.3)
    secret_bytes = app_secret.encode('utf-8')
    message_bytes = string_to_sign.encode('utf-8')
    signature = base64.b64encode(hmac.new(secret_bytes, message_bytes, hashlib.sha256).digest()).decode('utf-8')
    
    return signature

def list_solar_plants():
    import math

    PAGE_SIZE = 50
    pagina = 1
    total_paginas = None

    while True:
        params = {
            "token": TOKEN,
            "pageNum": pagina,
            "pageSize": PAGE_SIZE,
            "order": 0
        }

        timestamp = int(time.time() * 1000)
        nonce = str(uuid.uuid4())

        headers = {
            "Accept": "application/json",
            "X-Ca-Key": APP_KEY,
            "X-Ca-Timestamp": str(timestamp),
            "X-Ca-Nonce": nonce,
            "X-Ca-Signature-Headers": "X-Ca-Key,X-Ca-Nonce,X-Ca-Timestamp",
            "X-Ca-Stage": "RELEASE"
        }
        headers["X-Ca-Signature"] = generate_signature(PATH, params, APP_KEY, APP_SECRET, timestamp, nonce)

        try:
            response = requests.get(f"{DOMAIN}{PATH}", params=params, headers=headers)
            response.raise_for_status()
            result = response.json()
        except Exception as e:
            print(f"Erro na requisição (página {pagina}): {e}")
            break

        if result.get("status") != 200:
            print(f"Erro na API: {result.get('info')} (Código: {result.get('status')})")
            break

        data = result.get("data", {})
        plants = data.get("result", [])

        if not plants:
            break

        for plant in plants:
            print(plant.get("name", "N/A"))

        if total_paginas is None:
            if "pages" in data:
                total_paginas = int(data["pages"])
            elif "total" in data and data["total"]:
                total_paginas = math.ceil(int(data["total"]) / PAGE_SIZE)

        if total_paginas is not None:
            if pagina >= total_paginas:
                break
        elif len(plants) < PAGE_SIZE:
            break

        pagina += 1

if __name__ == "__main__":
    list_solar_plants()