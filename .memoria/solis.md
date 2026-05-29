# .memoria/solis.md — Histórico Técnico: Solis

---

## [2026-05-13] — Criação do solis_match.py: exportação de nomes da API Solis

**Arquivo criado:** `solis_match.py`

**Comportamento:** Mesmo padrão dos scripts Growatt e Fronius. Chama `buscar_dados_completos()`
do módulo Solis, extrai o campo `stationName` (campo correto da API Solis — diferente de `name`
usado pela Fronius), ordena alfabeticamente e gera `solis_nomes.xlsx` com os nomes na coluna A
(aba "Usinas Solis"). Cabeçalho verde (#1F7A1F) para diferenciação visual.

**Atenção:** O campo de nome na API Solis é `stationName`, não `name`. Nunca trocar por `name`
ao manipular a resposta da API Solis.

---

## [2026-05-28] — Ativação da Solis no main.py + geração hoje e mensal

**Arquivos alterados:** `modules/Solis.py`, `main.py`

**Problema:** O bloco Solis em `main.py` estava comentado; a função `traduzir_status` retornava apenas 2 valores `(status, last_update)`, sem geração.

**Alterações em `modules/Solis.py`:**
- `traduzir_status` agora retorna 4 valores: `(status, last_update, etoday, e_month)`.
- `etoday` usa o campo `dayEnergy1` e `e_month` usa `monthEnergy1` — ambos **sempre em kWh**.
- **Atenção crítica:** Os campos `dayEnergy` e `monthEnergy` (sem sufixo `1`) podem ser normalizados pela API para MWh em usinas de grande geração (ex.: Usina Ezio Pereira retorna `monthEnergy: 2.155 MWh`, mas `monthEnergy1: 2154.7 kWh`). Sempre usar os campos com sufixo `1`.
- Formato da `last_update` corrigido de `"%Y-%m-%d %H:%M:%S"` para `"%d/%m/%Y %H:%M"` (padrão BR).
- O timestamp `dataTimestamp` vem em milissegundos; converter com `fromtimestamp(int(ts) / 1000)`.

**Alterações em `main.py`:**
- Bloco Solis descomentado na ETAPA 1 (`solis_buscar()` chamado condicionalmente).
- Bloco Growatt que estava comentado removido (limpeza).
- Novo bloco `if marca == "solis"` na ETAPA 2 escreve nas colunas 7 (status), 8 (última atualização), 9 (geração hoje kWh), 10 (geração mensal kWh).
