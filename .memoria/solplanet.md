# .memoria/solplanet.md — Histórico Técnico: Solplanet

---

## [2026-05-14] — Módulo Solplanet: implementação final e integração no main.py

**Arquivos criados/alterados:** `modules/Solplanet.py`, `main.py`

**Autenticação:** HMAC-SHA256 via headers `X-Ca-*` (mesmo padrão do `teste_solplanet.py`).
A assinatura é gerada pela função `_gerar_assinatura()` que monta o `StringToSign` no formato:
`METHOD\naccept\n\n\n\n` + headers ordenados + path + query string ordenada.

**Variáveis de ambiente (`.env`):**
- `SOLPLANET_ID` → `X-Ca-Key` e parâmetro `APP_KEY`
- `SOLPLANET_SECRET` → chave HMAC
- `SOLPLANET_TOKEN` → parâmetro `token` na query string

**Endpoint:** GET `https://ap-southeast-1-api-genergal.aisweicloud.com/pro/getPlanListPro`
Paginação via `pageNum`/`pageSize=50`; loop encerra quando `len(lote) < pageSize` ou lista vazia.
Cada usina contém `name`, `status` e campos de data (`updateDate`, `lastUploadTime`).

**Mapeamento de status (campo inteiro):**
- `1` → On-line
- `0` → Off-line
- `2` → Alarme

**Matching:** bidirecional case-insensitive (`nome_busca in nome_api or nome_api in nome_busca`), mesmo padrão dos módulos anteriores.

**Integração no `main.py`:**
- Import corrigido de `teste_solplanet` para `modules.Solplanet` (`buscar_dados_completos as solplanet_buscar`, `traduzir_status as solplanet_status`)
- `base_solplanet = []` inicializado junto às outras bases
- Bloco de sync: `if "solplanet" in marcas_presentes` → chama `solplanet_buscar()`
- Bloco de processamento: `elif marca == "solplanet"` → chama `solplanet_status()`

---

## [2026-05-22] — Integração de Geração Hoje e Geração Mensal

**Arquivos alterados:** `modules/Solplanet.py`, `main.py`

**Geração Hoje (`etoday`):** já retornado pelo endpoint `getPlanListPro` (campo `etoday`, float em kWh). Nenhuma chamada extra necessária.

**Geração Mensal (`e_month`):** obtida via novo endpoint `getPlantOverviewPro` usando o `apikey` de cada usina.
- Endpoint: `GET /pro/getPlantOverviewPro?token=...&apikey=...`
- Mesma assinatura HMAC-SHA256 (`_gerar_assinatura`) com `_PATH_OVERVIEW`
- Campo extraído: `data["E-Month"]["value"]` (float, kWh)

**Alterações no módulo:**
- Nova constante `_PATH_OVERVIEW = "/pro/getPlantOverviewPro"`
- Nova função `_buscar_overview(apikey)` → retorna JSON bruto da API
- `buscar_dados_completos()` enriquece cada usina com `e_month` após carregar a lista
- `traduzir_status()` retorna tupla de **4 valores**: `(status, last_update, etoday, e_month)`

**Integração no `main.py`:**
- Desempacotamento: `status, last_update, etoday, e_month = solplanet_status(...)`
- Bloco Solplanet usa `continue` para escrever independentemente das outras marcas
- Escrita: col H (8) = last_update | col I (9) = etoday | col J (10) = e_month
- Cabeçalhos adicionados: col 9 = "Geração Hoje (kWh)" | col 10 = "Geração Mensal (kWh)"
