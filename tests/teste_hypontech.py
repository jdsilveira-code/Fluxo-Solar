import os
import requests
from dotenv import load_dotenv
import json

load_dotenv()

class HypontechAPI:
    def __init__(self):
        self.email = os.getenv("HYPONTECH_EMAIL")
        self.password = os.getenv("HYPONTECH_PASSWORD")
        self.base_url = "https://api.hypon.cloud" 
        self.token = None

    def login(self):
        """Realiza a autenticação na API v2 da Hypontech"""
        url = f"{self.base_url}/v2/login" 
        
        # 1. VERIFICAÇÃO DO .ENV
        if not self.email or not self.password:
            print("❌ ERRO CRÍTICO: E-mail ou senha estão VAZIOS no Python.")
            print("Verifique se o arquivo .env está no mesmo diretório de execução ou force o caminho no load_dotenv().")
            return None

        # 2. O PAYLOAD CORRETO (segundo a mensagem em chinês)
        payload = {
            "username": self.email, 
            "password": self.password
        }
        
        headers = {
            "Content-Type": "application/json",
            "Origin": "https://www.hypon.cloud",
            "Referer": "https://www.hypon.cloud/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        try:
            print(f"Tentando login em: {url}...")
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            
            if response.status_code != 200:
                print("Erro na requisição. Abortando.")
                return None
                
            data = response.json()
            
            # Se a API reclamar de novo, a gente vê na hora
            if data.get("code") == 40000:
                print(f"❌ Erro da API: {data.get('data')} | Mensagem: {data.get('message')}")
                return None

            dados_internos = data.get("data")
            
            if isinstance(dados_internos, dict):
                self.token = dados_internos.get("token")
            else:
                self.token = response.headers.get("Token")
            
            if self.token:
                print("✅ Login realizado com sucesso! Token obtido.")
                return self.token
            else:
                print("Falha ao encontrar o token na resposta.")
                return None
                
        except Exception as e:
            print(f"Erro ao conectar: {e}")
            return None

    def listar_usinas(self):
        """Busca a lista de usinas e imprime o formato exato da resposta"""
        if not self.token:
            if not self.login():
                return

        url = f"{self.base_url}/v2/plant/list2"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
            # Removi o header 'Token' duplicado, pois o seu print mostra que usam apenas 'Authorization'
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        try:
            todas_usinas = []
            pagina = 1
            page_size = 50

            while True:
                params = {"page": pagina, "page_size": page_size, "refresh": "true"}
                print(f"Buscando página {pagina}...")
                response = requests.get(url, headers=headers, params=params, timeout=10)

                if response.status_code != 200:
                    print(f"Erro na página {pagina}. Status: {response.status_code} | Resposta: {response.text}")
                    break

                dados = response.json()
                usinas_pagina = dados.get("data", [])

                if not usinas_pagina:
                    break

                todas_usinas.extend(usinas_pagina)

                if len(usinas_pagina) < page_size:
                    break

                pagina += 1

            print(f"\n{'='*40}")
            print(f"TOTAL DE USINAS ENCONTRADAS: {len(todas_usinas)}")
            print(f"{'='*40}")
            n = 1
            for usina in todas_usinas:
                print(n, usina["plant_name"])
                n += 1
            print(f"{'='*40}\n")

        except Exception as e:
            print(f"Erro na requisição de usinas: {e}")

if __name__ == "__main__":
    hypon = HypontechAPI()
    hypon.listar_usinas()