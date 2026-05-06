import requests
import hmac
import hashlib
import base64
import os
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis do .env
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

HOST = 'https://eu-api-genergal.aisweicloud.com'
APP_KEY = os.getenv("SOLPLANET_API_ID")       # Seu 'Id'
APP_SECRET = os.getenv("SOLPLANET_API_SECRET") # Seu 'Secret'
TOKEN = os.getenv("SOLPLANET_API_USER_TOKEN")       # Seu 'Token'

def buscar_dados(api_key_cliente):
    """
    api_key_cliente: É o ID da usina que você pegará de cada linha do Excel.
    """
    path = "/pro/getDeviceListPro"
    method = "GET"
    accept = "application/json"
    content_type = "application/json; charset=UTF-8"

    # Montagem da URL com os parâmetros obrigatórios do modo Pro
    # Aqui usamos o ID da usina vindo do Excel (api_key_cliente)
    url_params = f"{path}?apikey={api_key_cliente}&token={TOKEN}"
    
    # Ordenação alfabética dos parâmetros (exigência da API para a assinatura)
    s1 = url_params.split('?')
    s2 = sorted(s1[1].split('&'))
    url_final = s1[0] + '?' + '&'.join(s2)

    # Criação da Assinatura HMAC-SHA256
    str_sign = f"{method}\n{accept}\n\n{content_type}\n\nX-Ca-Key:{APP_KEY}\n{url_final}"
    signature = base64.b64encode(
        hmac.new(APP_SECRET.encode('utf-8'), str_sign.encode('utf-8'), hashlib.sha256).digest()
    ).decode('utf-8')

    headers = {
        "Content-Type": content_type,
        "Accept": accept,
        "X-Ca-Key": APP_KEY,
        "X-Ca-Signature": signature,
        "X-Ca-Signature-Headers": "X-Ca-Key"
    }

    try:
        r = requests.get(f"{HOST}{url_final}", headers=headers, timeout=15)
        return r.json() if r.status_code == 200 else {}
    except:
        return {}

def traduzir_status(json_res):
    """Mapeia o istate: 1=Online, 0=Offline, outros=Alarme"""
    try:
        # No modo Pro, a estrutura costuma ser data[0]...
        inversor = json_res['data'][0]['inverters'][0]
        status_num = inversor.get('istate')
        
        if status_num == 1: return "On-line"
        if status_num == 0: return "Off-line"
        return "Alarme"
    except:
        return "Off-line"