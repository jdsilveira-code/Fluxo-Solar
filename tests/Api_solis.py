import hashlib
import hmac
import base64
import datetime
import requests
import json
import locale

# 1. SUAS CREDENCIAIS
API_ID = "1300386381677159258"
API_SECRET = "a6446fe6c3874ea5b9971c30fc79e2b1"
# CORREÇÃO 1: Removida a barra final '/' do API_URL
API_URL = "https://www.soliscloud.com:13333" 
RESOURCE_PATH = "/v1/api/inverterList"

def get_solis_data():
    # Garante que o JSON do corpo seja compacto e sem espaços [cite: 36]
    payload = {"pageNo": 1, "pageSize": 10}
    body = json.dumps(payload, separators=(',', ':'))
    
    # CORREÇÃO 2: Deixando exatamente igual ao exemplo de chamada (Página 7) [cite: 47]
    content_type = "application/json"
    
    # Gerar Content-MD5 [cite: 36]
    md5_hash = hashlib.md5(body.encode('utf-8')).digest()
    content_md5 = base64.b64encode(md5_hash).decode('utf-8')
    
    # Gerar Data em GMT (Forçando Locale US para evitar nomes de dias em PT-BR)
    try:
        locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')
    except:
        locale.setlocale(locale.LC_TIME, 'en_US') # Para Windows
        
    now = datetime.datetime.now(datetime.timezone.utc)
    date_gmt = now.strftime("%a, %d %b %Y %H:%M:%S GMT")
    
    # Montar a String de Assinatura (A ordem deve ser exata!) [cite: 39]
    sign_str = f"POST\n{content_md5}\n{content_type}\n{date_gmt}\n{RESOURCE_PATH}"
    
    # Gerar HMAC-SHA1 e converter para Base64 [cite: 39]
    hashed = hmac.new(
        API_SECRET.encode('utf-8'), 
        sign_str.encode('utf-8'), 
        hashlib.sha1
    ).digest()
    
    signature = base64.b64encode(hashed).decode('utf-8')
    
    # Headers obrigatórios conforme página 5 [cite: 23, 34]
    headers = {
        "Content-MD5": content_md5,
        "Content-Type": content_type,
        "Date": date_gmt,
        "Authorization": f"API {API_ID}:{signature}"
    }

    # Agora a URL ficará corretamente: https://www.soliscloud.com:13333/v1/api/inverterList
    response = requests.post(API_URL + RESOURCE_PATH, headers=headers, data=body)
    return response

# Executar
res = get_solis_data()
print(f"Status Code: {res.status_code}")
#print(res.text)