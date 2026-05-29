import unicodedata
import difflib
import re

_STOPWORDS = frozenset({
    "da", "de", "do", "das", "dos", "e", "em", "a", "o", "as", "os",
    "ltda", "me", "eireli", "sa",
    "microgeracao", "usina"
})


def _normalizar(nome: str) -> str:
    nome = nome.strip().lower()
    nome = unicodedata.normalize("NFD", nome)
    nome = "".join(c for c in nome if unicodedata.category(c) != "Mn")
    nome = re.sub(r"[^a-z0-9\s]", " ", nome)
    tokens = [t for t in nome.split() if t and t not in _STOPWORDS]
    return " ".join(tokens)


def limpar_e_comparar_nomes(nome_planilha: str, nome_api: str, threshold: float = 0.75) -> bool:
    """
    Retorna True se nome_planilha e nome_api correspondem ao mesmo cliente/usina.

    Estratégias em cascata:
      1. Substring nos tokens normalizados (retrocompatível e rápido)
      2. Token majority overlap (cobre abreviações e ordem invertida)
      3. difflib SequenceMatcher ratio >= threshold (cobre grafias divergentes leves)
    """
    p = _normalizar(nome_planilha)
    a = _normalizar(nome_api)

    if not p or not a:
        return False

    # 1. Fast path: substring bidirecional
    if p in a or a in p:
        return True

    # 2. Token overlap
    tokens_p = set(p.split())
    tokens_a = set(a.split())
    shorter = tokens_p if len(tokens_p) <= len(tokens_a) else tokens_a
    longer  = tokens_a if shorter is tokens_p else tokens_p
    overlap = shorter & longer

    n = len(shorter)
    if n == 1:
        min_match = 1
    elif n == 2:
        min_match = 2          # exige ambos para evitar falso positivo em nomes genéricos
    else:
        min_match = (n + 1) // 2  # ceil(n/2)

    if len(overlap) >= min_match:
        return True

    # 3. Fuzzy ratio como último recurso
    ratio = difflib.SequenceMatcher(None, p, a).ratio()
    return ratio >= threshold
