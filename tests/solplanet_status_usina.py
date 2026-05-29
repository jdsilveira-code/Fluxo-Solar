"""
Consulta interativa de status de usina Solplanet.

Uso:
    python tests/solplanet_status_usina.py

O script busca todas as usinas da conta via API e retorna o status
da usina cujo nome corresponde ao texto digitado pelo usuário.

Mapeamento de status (campo 'status' da API Solplanet):
  1 → On-line
  0 → Off-line
  2 → Alarme
"""

import sys
from pathlib import Path

# Permite rodar a partir da raiz do projeto ou de dentro de /tests
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.Solplanet import buscar_dados_completos, traduzir_status

STATUS_LABEL = {
    "On-line":      "[ON-LINE]",
    "Off-line":     "[OFF-LINE]",
    "Alarme":       "[ALARME]",
    "Não encontrado": "[NAO ENCONTRADO]",
}


def main():
    nome = input("Nome da usina: ").strip()
    if not nome:
        print("Nenhum nome informado. Encerrando.")
        return

    print(f"\nBuscando dados na API Solplanet...")
    usinas = buscar_dados_completos()

    if not usinas:
        print("Nao foi possivel obter dados da API. Verifique o .env e a conexao.")
        return

    status, ultima_atualizacao = traduzir_status(nome, usinas)
    label = STATUS_LABEL.get(status, f"[{status.upper()}]")

    print(f"\nUsina  : {nome}")
    print(f"Status : {label} {status}")
    if ultima_atualizacao:
        print(f"Ultima atualizacao: {ultima_atualizacao}")


if __name__ == "__main__":
    main()
