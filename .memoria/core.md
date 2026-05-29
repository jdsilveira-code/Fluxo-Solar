# .memoria/core.md — Histórico Técnico: main.py e Regras Globais

---

## Padrão de Integração de Módulos no main.py

Todo novo módulo de marca segue este padrão de integração:

1. Import no topo: `from modules.NovaMarca import buscar_dados_completos as marca_buscar, traduzir_status as marca_status`
2. Inicialização: `base_novamarca = []` junto às outras bases
3. Bloco de sync: `if "novamarca" in marcas_presentes` → chama `marca_buscar()`
4. Bloco de processamento: `elif marca == "novamarca"` → chama `marca_status()`

## Padrão de Matching (Fuzzy — desde 2026-05-19)

Todos os módulos usam `limpar_e_comparar_nomes(nome_cliente, nome_api)` de `modules/utils.py`.
A função aplica 3 estratégias em cascata:
1. Substring bidirecional nos tokens normalizados (fast path)
2. Token majority overlap (cobre padrão Fronius "Microgeração {Nome}")
3. `difflib.SequenceMatcher` ratio ≥ 0.75 (cobre grafias divergentes)

A normalização inclui: lowercase, remoção de acentos (unicodedata NFD), remoção de
stopwords (`ltda`, `me`, `microgeracao`, preposições).

**Não altere a assinatura** `traduzir_status(nome_cliente, lista_X)` — o `main.py` depende dela.

## Status Padronizados

Os únicos valores válidos para a coluna de status no Excel são:
- `"On-line"`
- `"Off-line"`
- `"Alarme"`

---

## [2026-05-19] — Refatoração: Fuzzy Matching centralizado

**Arquivo criado:** `modules/utils.py`
**Arquivos alterados:** `Fronius.py`, `Hypontech.py`, `Solplanet.py`, `Solis.py`, `Growatt.py`

**Problema:** Matching por substring pura gerava falsos negativos quando a API abreviava
nomes (ex: Fronius usa "Microgeração Adelson" para "ADELSON CARVALHO FERREIRA"), quando
havia acentos diferentes ou sufixos jurídicos (LTDA).

**Solução:** `modules/utils.py` com `limpar_e_comparar_nomes(nome_planilha, nome_api, threshold=0.75)`.
Todos os módulos importam e usam essa função no lugar da comparação inline.
Teste de regressão: `tests/test_fuzzy_matching.py` (20 casos, sem dependência de API).

---

## [2026-05-07] — Bug global: str(None) no campo marca (main.py)

**Arquivo alterado:** `main.py`

**Problema:** `marca = str(sheet.cell(...).value).strip().lower()` — quando a célula está vazia
(None), `str(None)` gera a string `"none"`, que é truthy e não é pulada pelo `if not marca: continue`.
Resultado: linha sem marca cai como "Marca não mapeada".

**Correção:** `str(sheet.cell(...).value or "").strip().lower()` — garante string vazia (falsy),
e a linha é corretamente ignorada.

**Impacto:** Afeta todas as marcas. Fix aplicado globalmente no `main.py`.
