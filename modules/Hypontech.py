import os
import requests
from pathlib import Path
from dotenv import load_dotenv
from modules.utils import limpar_e_comparar_nomes

env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

EMAIL    = os.getenv("HYPONTECH_EMAIL")
PASSWORD = os.getenv("HYPONTECH_PASSWORD")
BASE_URL = "https://api.hypon.cloud"


def _obter_token():
    try:
        r = requests.post(
            f"{BASE_URL}/v2/login",
            json={"username": EMAIL, "password": PASSWORD},
            headers={
                "Content-Type": "application/json",
                "Origin": "https://www.hypon.cloud",
                "Referer": "https://www.hypon.cloud/",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            },
            timeout=15,
        )
        r.raise_for_status()
        data = r.json()

        if data.get("code") == 40000:
            print(f"[Hypontech] Erro de autenticação: {data.get('message')}")
            return None

        dados_internos = data.get("data")
        if isinstance(dados_internos, dict):
            return dados_internos.get("token")
        return r.headers.get("Token")
    except Exception as e:
        print(f"[Hypontech] Erro ao autenticar: {e}")
        return None


# ─── COLETA DE DADOS ─────────────────────────────────────────────────────────

def buscar_dados_completos():
    """Retorna a lista completa de usinas da conta Hypontech."""
    token = _obter_token()
    if not token:
        print("[Hypontech] Sem token. Abortando busca.")
        return []

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    }

    todas = []
    pagina = 1
    page_size = 50

    while True:
        try:
            r = requests.get(
                f"{BASE_URL}/v2/plant/list2",
                headers=headers,
                params={"page": pagina, "page_size": page_size, "refresh": "true"},
                timeout=15,
            )
            r.raise_for_status()
            lote = r.json().get("data", [])
        except Exception as e:
            print(f"[Hypontech] Erro ao buscar usinas (página {pagina}): {e}")
            break

        if not lote or not isinstance(lote, list):
            break

        todas.extend(lote)

        if len(lote) < page_size:
            break

        pagina += 1

    print(f"[Hypontech] Cache pronto: {len(todas)} usinas carregadas.")
    return todas


# ─── TRADUÇÃO DE STATUS ───────────────────────────────────────────────────────

def traduzir_status(nome_cliente, lista_hypontech):
    """
    Localiza a usina pelo nome (case-insensitive, bidirecional) e retorna (status, last_update).

    Mapeamento do campo 'status' da API Hypontech:
      "normal"                    → On-line
      "offline"                   → Off-line
      "alarm" / "error" / "fault" → Alarme
    """
    for usina in lista_hypontech:
        nome_api = usina.get("plant_name") or ""

        if limpar_e_comparar_nomes(nome_cliente, nome_api):
            estado      = (usina.get("status") or "").lower()
            last_update = usina.get("time", "")

            if estado == "normal":
                return "On-line", last_update
            if estado == "offline":
                return "Off-line", last_update
            if estado in ("alarm", "error", "fault"):
                return "Alarme", last_update
            return (f"Sem dados ({estado})" if estado else "Sem dados"), last_update

    return "Não encontrado", ""
