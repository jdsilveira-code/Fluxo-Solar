import requests
import os
from pathlib import Path
from dotenv import load_dotenv

# 1. Ajuste de Caminho (Procura na pasta atual E na pasta pai para garantir)
env_path = Path(__file__).parent / '.env'
if not env_path.exists():
    env_path = Path(__file__).parent.parent / '.env'

load_dotenv(dotenv_path=env_path)

# 2. Captura das chaves (Use os nomes exatos do seu .env)
FRONIUS_ID = os.getenv("FRONIUS_API_ID")
FRONIUS_VALUE = os.getenv("FRONIUS_API_VALUE")
API_URL = "https://api.solarweb.com/swqapi"

def testar_conexao_direta():
    print(f"--- Debug Fronius ---")
    print(f"Arquivo .env: {env_path.absolute()}")
    print(f"Chave ID: {'OK' if FRONIUS_ID else 'VAZIA! Verifique o .env'}")
    print(f"Chave Value: {'OK' if FRONIUS_VALUE else 'VAZIA! Verifique o .env'}")
    print("-" * 20)

    if not FRONIUS_ID or not FRONIUS_VALUE:
        return

    # NA FRONIUS, VOCÊ PODE USAR AS CHAVES DIRETO NO HEADER!
    # Isso evita o erro 400 do endpoint de JWT.
    headers = {
        "AccessKeyId": FRONIUS_ID,
        "AccessKeyValue": FRONIUS_VALUE,
        "Content-Type": "application/json"
    }

    print("\n[Fronius] Solicitando lista de usinas...")
    try:
        r = requests.get(f"{API_URL}/pvsystems", headers=headers, timeout=15)
        
        if r.status_code == 200:
            dados = r.json()
            usinas = dados.get("pvSystems", [])
            print(f"✅ Conexão bem-sucedida! {len(usinas)} usinas encontradas:\n")
            
            for i, u in enumerate(usinas, 1):
                nome = u.get("name")
                id_usina = u.get("pvSystemId")
                # O status na lista simplificada pode vir como 'status' ou estar em branco
                status = u.get("status", "Verificar via Flow") 
                print(f"  {i}. {nome} (ID: {id_usina}) [{status}]")
        else:
            print(f"❌ Erro na API: {r.status_code}")
            print(f"Mensagem: {r.text}")

    except Exception as e:
        print(f"💥 Erro de conexão: {e}")

if __name__ == "__main__":
    testar_conexao_direta()