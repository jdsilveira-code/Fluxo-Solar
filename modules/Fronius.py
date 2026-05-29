import requests
import os
import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from dotenv import load_dotenv
from modules.utils import limpar_e_comparar_nomes

_WORKERS = 20  # chamadas paralelas por usina

env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

FRONIUS_ID    = os.getenv("FRONIUS_API_ID")
FRONIUS_VALUE = os.getenv("FRONIUS_API_VALUE")
API_URL = "https://api.solarweb.com/swqapi"


def _cabecalhos():
    return {
        "AccessKeyId":    FRONIUS_ID,
        "AccessKeyValue": FRONIUS_VALUE,
        "Content-Type":   "application/json",
    }


# ─── COLETA DE DADOS ─────────────────────────────────────────────────────────

def _buscar_dados_usina(pv_system_id):
    """
    Retorna dict {is_online, last_update, etoday, e_month} para uma usina.

    Endpoints confirmados (diagnóstico 2026-05-28):
      status/last_update → GET /pvsystems/{id}/flowdata
        payload["status"]["isOnline"]         (bool)
        payload["data"]["logDateTime"]         (ISO timestamp)

      etoday + e_month   → GET /pvsystems/{id}/aggrdata?from=YYYY-MM-01&to=YYYY-MM-DD
        response["data"][]["logDateTime"]      (date string "YYYY-MM-DD")
        response["data"][]["channels"][]
          channelName == "EnergyProductionTotal", unit == "Wh"
        etoday  = valor do dia de hoje / 1000  (kWh)
        e_month = soma de todos os dias / 1000 (kWh)
    """
    resultado = {"is_online": None, "last_update": "", "etoday": None, "e_month": None}

    # Status e última atualização
    try:
        r = requests.get(
            f"{API_URL}/pvsystems/{pv_system_id}/flowdata",
            headers=_cabecalhos(),
            timeout=10,
        )
        if r.ok:
            payload = r.json()
            resultado["is_online"]   = (payload.get("status") or {}).get("isOnline")
            resultado["last_update"] = (payload.get("data") or {}).get("logDateTime", "")
    except Exception as e:
        print(f"[Fronius] Erro flowdata {pv_system_id}: {e}")

    # Geração diária e mensal
    hoje = datetime.date.today()
    hoje_str  = hoje.isoformat()
    date_from = hoje.replace(day=1).isoformat()
    try:
        r = requests.get(
            f"{API_URL}/pvsystems/{pv_system_id}/aggrdata",
            headers=_cabecalhos(),
            params={"from": date_from, "to": hoje_str},
            timeout=10,
        )
        if r.ok:
            dias = r.json().get("data", [])
            total_wh = 0.0
            for dia in dias:
                for ch in dia.get("channels", []):
                    if ch.get("channelName") == "EnergyProductionTotal":
                        val = ch.get("value")
                        if val is None:
                            continue
                        total_wh += val
                        if dia.get("logDateTime", "").startswith(hoje_str):
                            resultado["etoday"] = round(val / 1000, 2)
            if total_wh > 0:
                resultado["e_month"] = round(total_wh / 1000, 2)
    except Exception as e:
        print(f"[Fronius] Erro aggrdata {pv_system_id}: {e}")

    return resultado


def buscar_dados_completos():
    """Retorna a lista completa de usinas com status, last_update e dados de geração."""
    todas = []
    offset = 0
    limit  = 100
    total  = None

    while True:
        try:
            r = requests.get(
                f"{API_URL}/pvsystems",
                headers=_cabecalhos(),
                params={"offset": offset, "limit": limit},
                timeout=15,
            )
            r.raise_for_status()
            res = r.json()
        except Exception as e:
            print(f"[Fronius] Erro ao buscar sistemas (offset {offset}): {e}")
            break

        lote = res.get("pvSystems", [])
        if not lote:
            break

        if total is None:
            total = (res.get("links") or {}).get("totalItemsCount", 0)

        todas.extend(lote)

        if total and len(todas) >= total:
            break
        offset += limit

    n = len(todas)
    print(f"[Fronius] {n} usinas. Buscando dados em paralelo ({_WORKERS} workers)...")

    # Separa usinas com e sem ID válido
    com_id = [(s.get("pvSystemId") or s.get("id"), s) for s in todas]
    sem_id = [s for pid, s in com_id if not pid]
    com_id = [(pid, s) for pid, s in com_id if pid]

    concluidos = 0
    with ThreadPoolExecutor(max_workers=_WORKERS) as executor:
        futures = {executor.submit(_buscar_dados_usina, pid): sistema for pid, sistema in com_id}
        for future in as_completed(futures):
            sistema = futures[future]
            try:
                sistema.update(future.result())
            except Exception:
                sistema.update({"is_online": None, "last_update": "", "etoday": None, "e_month": None})
            concluidos += 1
            if concluidos % _WORKERS == 0 or concluidos == len(com_id):
                print(f"[Fronius]   {concluidos}/{n} processadas...")

    for s in sem_id:
        s.update({"is_online": None, "last_update": "", "etoday": None, "e_month": None})

    print(f"[Fronius] Cache pronto: {n} usinas com status e geração.")
    return todas


# ─── TRADUÇÃO DE STATUS ───────────────────────────────────────────────────────

def traduzir_status(nome_cliente, lista_fronius):
    """
    Localiza a usina pelo nome (case-insensitive) e retorna
    (status, last_update, etoday, e_month).

    Mapeamento via flowdata["status"]["isOnline"]:
      True  → On-line
      False → Off-line
      None  → Sem dados
    """
    for sistema in lista_fronius:
        nome_api = sistema.get("name") or ""

        if limpar_e_comparar_nomes(nome_cliente, nome_api):
            is_online   = sistema.get("is_online")
            last_update = sistema.get("last_update", "")
            etoday      = sistema.get("etoday")
            e_month     = sistema.get("e_month")

            if is_online is True:
                return "On-line", last_update, etoday, e_month
            if is_online is False:
                return "Off-line", last_update, etoday, e_month
            return "Sem dados", last_update, etoday, e_month

    return "Não encontrado", "", None, None