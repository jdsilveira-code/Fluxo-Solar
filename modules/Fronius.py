import requests
import os
from pathlib import Path
from dotenv import load_dotenv

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

def buscar_dados_completos():
    """Retorna a lista completa de usinas da conta Fronius Solar.web."""
    todas = []
    offset = 0
    limit = 100

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

        lote  = res.get("pvSystems", [])
        total = res.get("totalCount", 0)

        if not lote:
            break

        todas.extend(lote)

        if len(todas) >= total:
            break
        offset += limit

    print(f"[Fronius] Cache pronto: {len(todas)} usinas carregadas.")
    return todas


# ─── TRADUÇÃO DE STATUS ───────────────────────────────────────────────────────

def traduzir_status(nome_cliente, lista_fronius):
    """
    Localiza a usina pelo nome (case-insensitive) e retorna (status, last_update).

    Mapeamento do campo 'status' da API Fronius Solar.web:
      "running" → On-line
      "warning" → Alarme
      "error"   → Alarme
      "offline" → Off-line
      outros    → Sem dados
    """
    nome_busca = nome_cliente.strip().lower()

    for sistema in lista_fronius:
        nome_api = sistema.get("name", "").strip().lower()

        if nome_busca in nome_api:
            estado      = (sistema.get("status") or sistema.get("state") or "").lower()
            last_update = sistema.get("lastDataTransfer") or ""

            if estado == "running":
                return "On-line", last_update
            if estado in ("warning", "error"):
                return "Alarme", last_update
            if estado == "offline":
                return "Off-line", last_update
            return (f"Sem dados ({estado})" if estado else "Sem dados"), last_update

    return "Não encontrado", ""
