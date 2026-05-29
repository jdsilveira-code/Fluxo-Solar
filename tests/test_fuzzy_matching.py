"""
Testes unitários para modules/utils.py — sem chamadas de API, sem arquivos Excel.
Execute a partir da raiz do projeto:
    python tests/test_fuzzy_matching.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.utils import limpar_e_comparar_nomes

# ── Casos que DEVEM dar True ─────────────────────────────────────────────────

MATCHES = [
    # Padrão Fronius: API abrevia para primeiro nome apenas
    ("ADELSON CARVALHO FERREIRA",            "Microgeração Adelson"),
    ("Adherbal Borges",                      "Microgeração Adherbal"),
    ("CLIMÉRIO DUBBERSTEIN",                 "Microgeração Climério"),
    ("JOSIMAR AVANCINI",                     "Microgeração Josimar"),
    ("KEILA KONZEN",                         "Microgeração Keila Konzen"),
    ("MARCELO RIZZI",                        "Microgeração Marcelo Rizzi"),
    # Fronius: API com 2 palavras significativas
    ("ALINE MAULAZ CARLOS COSTA",            "Microgeração Aline Maulaz"),
    ("JOSE GERALDO MARTINS COELHO",          "MicroGeração José Geraldo"),
    ("Jailson Ferreira Coelho",              "Microgeração Jailson Ferreira Coelho"),
    # Sufixo jurídico removido
    ("COMERCIAL PROTEGER LTDA",              "Microgeração Proteger"),
    # Acento diferente
    ("ANGELO MARIANO MATTEDI",               "Microgeração Angelo"),
    # Nome completo na API
    ("ALISON PEREIRA SILVA",                 "Microgeração ALISON PEREIRA SILVA"),
    # Ordem invertida das palavras
    ("Silva Joao",                           "Joao Silva"),
    # Correspondência exata normalizada
    ("Fernanda Nunes",                       "Microgeraçao Fernanda Nunes"),
    # Bidirecional simples (retrocompatibilidade)
    ("Usina Solar ABC",                      "ABC"),
]

# ── Casos que NÃO devem dar True (controle de falsos positivos) ───────────────

NON_MATCHES = [
    # "jose" genérico não deve casar com outro José
    ("JOSE TURRA",                           "Microgeração José Geraldo"),
    # Sobrenome diferente com 2 tokens
    ("MARCELO BICHARA",                      "Microgeração Marcelo Rizzi"),
    # Nome genérico + sobrenome errado
    ("PAULO CESAR DA SILVA",                 "Microgeração Paulo Ferreira"),
    # Completamente diferente
    ("João Silva",                           "Maria Souza"),
    # String vazia
    ("",                                     "Microgeração Teste"),
]


def _run():
    erros = []

    for planilha, api in MATCHES:
        resultado = limpar_e_comparar_nomes(planilha, api)
        if not resultado:
            erros.append(f"  FALHA (deveria ser True):  '{planilha}'  vs  '{api}'")

    for planilha, api in NON_MATCHES:
        resultado = limpar_e_comparar_nomes(planilha, api)
        if resultado:
            erros.append(f"  FALHA (deveria ser False): '{planilha}'  vs  '{api}'")

    total = len(MATCHES) + len(NON_MATCHES)
    if erros:
        print(f"\n[REPROVADO] {len(erros)}/{total} casos falharam:\n")
        for e in erros:
            print(e)
        sys.exit(1)
    else:
        print(f"\n[APROVADO] Todos os {total} casos passaram.\n")


if __name__ == "__main__":
    _run()
