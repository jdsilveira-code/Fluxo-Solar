# .memoria/growatt.md — Histórico Técnico: Growatt

---

## [2026-05-07] — Correção de dois bugs: matching Growatt e None na marca

**Arquivos alterados:** `modules/Growatt.py`, `main.py`

**Bug 1 — Matching unidirecional em `traduzir_status` (Growatt.py):**
A lógica original `if nome_busca in nome_api` só funcionava quando o nome da planilha era
subconjunto do nome da API (ex: planilha="DANIEL ROCHA" ⊂ api="DANIEL ROCHA").
Para o caso inverso frequente (planilha="ADAIR CORREA - MARLUCIA", api="Adair Correa"),
a busca falhava e retornava "Não encontrado" para ~95% dos clientes Growatt.
**Correção:** condição expandida para bidirecional:
`if nome_busca in nome_api or nome_api in nome_busca:`

**Bug 2 — str(None) no campo marca (main.py):**
Na linha `marca = str(sheet.cell(...).value).strip().lower()`, se a célula estivesse vazia
(None), `str(None)` produzia a string literal `"none"` — truthy, logo não pulada pelo
`if not marca: continue`, e sem match no elif → "Marca não mapeada".
**Correção:** `str(sheet.cell(...).value or "").strip().lower()` garante string vazia,
que é falsy e a linha é pulada corretamente.
(Este bug e fix também está registrado em `core.md` por impactar o `main.py` globalmente.)

**Contexto adicional:**
O commit 87f4d94 havia removido Growatt do `main.py`; o usuário o reinseriu manualmente
(alterações não commitadas). O `growatt_match.py` é uma ferramenta auxiliar de diagnóstico:
gera aba `Growatt_Match` no `clientes.xlsx` com nomes da planilha × nomes da API para
revisão manual, caso o matching bidirecional ainda não seja suficiente.

---

## [2026-05-13] — Simplificação do growatt_match.py: saída para arquivo próprio

**Arquivo alterado:** `growatt_match.py`

**Alteração:** O script foi reescrito para focar exclusivamente nos nomes da API Growatt.
Comportamento anterior: gerava aba `Growatt_Match` no `clientes.xlsx` com dois blocos
(nomes da planilha × nomes da API) para comparação manual.
Comportamento novo: cria um arquivo separado `growatt_nomes.xlsx` com apenas os nomes
das usinas retornados pela API na coluna A (aba "Usinas Growatt"), em ordem alfabética.
Cabeçalho azul para diferenciação visual. Isso simplifica o diagnóstico quando o objetivo
é apenas inspecionar o que a API retorna.
