"""
Script de testes da API Growatt
================================
Versão 2 — Conta Distribuidor/Instalador

O /v1/plant/list retornou 0 usinas pois o token pertence a uma conta
instalador. Nesse modelo a estrutura é:

  Conta Instalador (token)
    └── Clientes finais (c_user_id)  ← /v1/user/c_user_list
          └── Usinas (plant_id)      ← /v1/plant/user_plant_list
                └── Dados da usina  ← /v1/plant/data

Sequência dos testes:
  1. Listar clientes finais da conta
  2. Buscar usinas do 1º cliente encontrado
  3. Buscar dados resumidos da 1ª usina encontrada

Como usar:
  1. Certifique-se que o .env tem: GROWATT_TOKEN=seu_token_aqui
  2. Execute: python growatt_teste.py
"""

import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

# ─── CONFIGURAÇÃO ────────────────────────────────────────────────────────────

GROWATT_TOKEN = os.getenv("GROWATT_TOKEN")

API_URL = "https://openapi.growatt.com"
# Caso receba error_code -1, troque pelo servidor da sua região:
#   Norte-americano : https://openapi-us.growatt.com
#   Chinês          : https://openapi-cn.growatt.com

# ─── HELPERS ─────────────────────────────────────────────────────────────────

def cabecalhos():
    return {"token": GROWATT_TOKEN}

def imprimir_resultado(titulo, response):
    """Imprime o resultado formatado de uma requisição."""
    sep = "─" * 60
    print(f"\n{sep}")
    print(f"  {titulo}")
    print(f"  HTTP: {response.status_code}")
    print(sep)

    try:
        dados = response.json()
        code  = dados.get("error_code")
        msg   = dados.get("error_msg", "")

        if code == 0:
            print("  ✅ Sucesso (error_code: 0)")
        elif code == -1:
            print("  ⚠️  Servidor errado! Troque o API_URL pela sua região.")
            print(f"     msg: {msg}")
        elif code == 10011:
            print("  ❌ Sem permissão — verifique se o token está correto.")
        elif code == 10012:
            print("  ⏳ Limite de frequência atingido (aguarde 5 minutos).")
        else:
            print(f"  ❌ Erro — code: {code} | msg: {msg}")

        print("\n  Resposta JSON:")
        print(json.dumps(dados, indent=4, ensure_ascii=False))
        return dados

    except Exception as e:
        print(f"  ❌ Falha ao interpretar resposta: {e}")
        print(f"  Conteúdo bruto: {response.text[:500]}")
        return {}

def secao(titulo):
    print("\n" + "═" * 60)
    print(f"  {titulo}")
    print("═" * 60)

# ─── TESTES ──────────────────────────────────────────────────────────────────

def teste_1_listar_clientes():
    """
    Teste 1: Lista os clientes finais vinculados à conta do instalador.
    Endpoint: GET /v1/user/c_user_list
    Retorna: c_user_id, c_user_name, c_user_email de cada cliente.
    """
    secao("TESTE 1 — Listar clientes da conta instalador")
    print("  Endpoint: GET /v1/user/c_user_list\n")

    try:
        r = requests.get(
            f"{API_URL}/v1/user/c_user_list",
            headers=cabecalhos(),
            params={"page": 1, "perpage": 5},
            timeout=15,
        )
        dados = imprimir_resultado("GET /v1/user/c_user_list", r)

        usuarios = dados.get("data", {}).get("c_user", [])
        total    = dados.get("data", {}).get("count", 0)

        print(f"\n  → Total de clientes na conta: {total}")

        if usuarios:
            primeiro = usuarios[0]
            print(f"  → Usando cliente '{primeiro.get('c_user_name')}' "
                  f"(c_user_id={primeiro.get('c_user_id')}) nos próximos testes.")
            return primeiro.get("c_user_id"), primeiro.get("c_user_name")
        else:
            print("  ⚠️  Nenhum cliente encontrado na conta.")
            return None, None

    except requests.exceptions.ConnectionError:
        print(f"  ❌ Falha de conexão com {API_URL}")
        return None, None
    except requests.exceptions.Timeout:
        print("  ❌ Timeout — servidor não respondeu em 15s.")
        return None, None


def teste_2_usinas_do_cliente(c_user_id, c_user_name):
    """
    Teste 2: Busca as usinas de um cliente específico.
    Endpoint: POST /v1/plant/user_plant_list
    Parâmetro obrigatório: user_name (o username do cliente, não o ID)
    """
    secao("TESTE 2 — Listar usinas de um cliente")
    print(f"  Endpoint: POST /v1/plant/user_plant_list")
    print(f"  Cliente: '{c_user_name}' (id={c_user_id})\n")

    if not c_user_name:
        print("  ⏭️  Pulado — Teste 1 não retornou nenhum cliente.")
        return None

    try:
        r = requests.post(
            f"{API_URL}/v1/plant/user_plant_list",
            headers=cabecalhos(),
            data={
                "user_name": c_user_name,
                "page": 1,
                "perpage": 5,
            },
            timeout=15,
        )
        dados = imprimir_resultado(
            f"POST /v1/plant/user_plant_list (user={c_user_name})", r
        )

        plants = dados.get("data", {}).get("plants", [])
        total  = dados.get("data", {}).get("count", 0)

        print(f"\n  → Total de usinas deste cliente: {total}")

        if plants:
            primeira = plants[0]
            print(f"  → Usando usina '{primeira.get('name')}' "
                  f"(plant_id={primeira.get('plant_id')}) no próximo teste.")
            return primeira.get("plant_id")
        else:
            print("  ⚠️  Nenhuma usina encontrada para este cliente.")
            return None

    except requests.exceptions.RequestException as e:
        print(f"  ❌ Erro na requisição: {e}")
        return None


def teste_3_dados_usina(plant_id):
    """
    Teste 3: Busca dados operacionais de uma usina (potência atual, energia, etc).
    Endpoint: GET /v1/plant/data
    Este é o endpoint mais relevante para o sistema de monitoramento.
    """
    secao("TESTE 3 — Dados operacionais da usina")
    print(f"  Endpoint: GET /v1/plant/data\n")

    if not plant_id:
        print("  ⏭️  Pulado — Teste 2 não retornou nenhuma usina.")
        return

    try:
        r = requests.get(
            f"{API_URL}/v1/plant/data",
            headers=cabecalhos(),
            params={"plant_id": plant_id},
            timeout=15,
        )
        imprimir_resultado(f"GET /v1/plant/data (plant_id={plant_id})", r)

    except requests.exceptions.RequestException as e:
        print(f"  ❌ Erro na requisição: {e}")


# ─── EXECUÇÃO ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n" + "█" * 60)
    print("   TESTES DA API GROWATT — v2 (conta instalador)")
    print(f"   Servidor : {API_URL}")

    if not GROWATT_TOKEN:
        print("\n  ❌ GROWATT_TOKEN não encontrado no .env!")
        print("     Verifique se o arquivo .env existe e contém GROWATT_TOKEN=...\n")
    else:
        token_preview = f"{'*' * 20}{GROWATT_TOKEN[-6:]}"
        print(f"   Token     : {token_preview}")
        print("█" * 60)

        c_user_id, c_user_name = teste_1_listar_clientes()
        plant_id = teste_2_usinas_do_cliente(c_user_id, c_user_name)
        teste_3_dados_usina(plant_id)

        print("\n" + "═" * 60)
        print("  FIM DOS TESTES")
        print("═" * 60 + "\n")