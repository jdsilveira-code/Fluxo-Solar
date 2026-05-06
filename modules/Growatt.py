import requests
import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

GROWATT_TOKEN = os.getenv("GROWATT_TOKEN")
API_URL = "https://openapi.growatt.com"


def _cabecalhos():
    return {"token": GROWATT_TOKEN}


# ─── COLETA DE DADOS ─────────────────────────────────────────────────────────

def _buscar_todos_clientes():
    """
    Percorre todas as páginas de /v1/user/c_user_list e retorna
    a lista completa de clientes finais da conta.
    """
    todos = []
    pagina = 1
    while True:
        try:
            r = requests.get(
                f"{API_URL}/v1/user/c_user_list",
                headers=_cabecalhos(),
                params={"page": pagina, "perpage": 100},
                timeout=15,
            )
            res = r.json()
        except Exception as e:
            print(f"[Growatt] Erro ao buscar clientes (pág {pagina}): {e}")
            break

        if res.get("error_code") != 0:
            print(f"[Growatt] Erro na API de clientes: {res.get('error_msg')}")
            break

        lote = res.get("data", {}).get("c_user", [])
        total = res.get("data", {}).get("count", 0)
        todos.extend(lote)

        if len(todos) >= total or not lote:
            break
        pagina += 1

    return todos


def _buscar_usinas_do_cliente(c_user_name):
    """
    Retorna todas as usinas de um cliente via /v1/plant/user_plant_list.
    Percorre paginação se necessário.
    Retorna (lista_usinas, mensagem_erro_ou_None).
    """
    usinas = []
    pagina = 1
    while True:
        try:
            r = requests.post(
                f"{API_URL}/v1/plant/user_plant_list",
                headers=_cabecalhos(),
                data={"user_name": c_user_name, "page": pagina, "perpage": 100},
                timeout=15,
            )
            res = r.json()
        except Exception as e:
            return usinas, str(e)

        if res.get("error_code") != 0:
            break

        lote = res.get("data", {}).get("plants", [])
        total = res.get("data", {}).get("count", 0)
        usinas.extend(lote)

        if len(usinas) >= total or not lote:
            break
        pagina += 1

    return usinas, None


def _buscar_last_update(plant_id):
    """
    Busca o last_update_time de uma usina via /v1/plant/data.
    Retorna a string da data ou None em caso de falha.
    """
    try:
        r = requests.get(
            f"{API_URL}/v1/plant/data",
            headers=_cabecalhos(),
            params={"plant_id": plant_id},
            timeout=15,
        )
        res = r.json()
        if res.get("error_code") == 0:
            return res.get("data", {}).get("last_update_time")
    except Exception as e:
        print(f"[Growatt] Erro ao buscar dados da usina {plant_id}: {e}")
    return None


def buscar_dados_completos():
    """
    Ponto de entrada principal — monta o cache completo de todas as usinas.

    Fluxo:
      1. Busca todos os clientes da conta (/v1/user/c_user_list)
      2. Para cada cliente, busca suas usinas (/v1/plant/user_plant_list)
      3. Para cada usina, busca o last_update_time (/v1/plant/data)

    Retorna lista de dicts:
      {
        "name":             str,   # nome da usina na API
        "status":           int,   # 1=Online, 2=Offline, 3=Alarme, 4=Sem dados
        "last_update_time": str,   # ex: "2025-02-24 08:57:01" ou None
      }
    """
    cache = []

    clientes = _buscar_todos_clientes()
    total = len(clientes)
    print(f"[Growatt] {total} clientes encontrados. Buscando usinas...")

    for i, cliente in enumerate(clientes, start=1):
        nome_cliente = cliente.get("c_user_name", "")
        usinas, erro = _buscar_usinas_do_cliente(nome_cliente)
        total_usinas = len(usinas)

        if erro:
            print(
                f"\n  [{i}/{total}] {nome_cliente[:28]:<28}  ERRO: {erro[:50]}",
            )
            continue

        if not usinas:
            print(
                f"  [{i}/{total}] {nome_cliente[:28]:<28}  sem usinas          ",
                end="\r", flush=True,
            )
            continue

        print(
            f"  [{i}/{total}] {nome_cliente[:28]:<28}  {total_usinas} usina(s)      ",
            end="\r", flush=True,
        )
        for usina in usinas:
            cache.append({
                "name":     usina.get("name", ""),
                "status":   usina.get("status"),
                "plant_id": usina.get("plant_id"),
            })

    print()  # limpa a linha do \r
    print(f"[Growatt] Cache pronto: {len(cache)} usinas carregadas.")
    return cache


# ─── TRADUÇÃO DE STATUS ───────────────────────────────────────────────────────

def traduzir_status(nome_cliente, lista_growatt):
    """
    Busca a usina pelo nome do cliente (lógica 'in') e retorna
    uma tupla (status, last_update_time) padronizada.

    Mapeamento de status Growatt:
      1 = On-line
      2 = Off-line
      3 = Alarme
      4 = Sem dados  (usina sem dispositivos associados)

    Retorno: (str_status, str_data_ou_vazio)
    """
    nome_busca = nome_cliente.strip().lower()

    for usina in lista_growatt:
        nome_api = usina.get("name", "").strip().lower()

        if nome_busca in nome_api:
            status = usina.get("status")
            last_update = _buscar_last_update(usina.get("plant_id")) or ""

            if status == 1:
                return "On-line", last_update
            elif status == 2:
                return "Off-line", last_update
            elif status == 3:
                return "Alarme", last_update
            elif status == 4:
                return "Sem dados", last_update
            else:
                return f"Desconhecido ({status})", last_update

    return "Não encontrado", ""
