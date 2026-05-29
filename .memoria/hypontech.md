# .memoria/hypontech.md — Histórico Técnico: Hypontech

---

## [2026-05-13] — Módulo Hypontech: implementação e integração no main.py

**Arquivos criados/alterados:** `modules/Hypontech.py`, `main.py`

**Autenticação:** POST `https://api.hypon.cloud/v2/login` com payload `{"username": email, "password": password}`.
Token retornado em `data["data"]["token"]`. Caso `data["code"] == 40000`, a API sinaliza credencial inválida.

**Listagem de usinas:** GET `/v2/plant/list2` com `Authorization: Bearer {token}`.
Paginação via params `page` e `page_size=50`; loop encerra quando `len(lote) < page_size` ou lista vazia.
Cada usina contém `plant_name`, `status` e `time`.

**Mapeamento de status:**

- `"normal"` → On-line
- `"offline"` → Off-line
- `"alarm"` / `"error"` / `"fault"` → Alarme

**Matching:** bidirecional case-insensitive (`nome_busca in nome_api or nome_api in nome_busca`), mesmo padrão do fix Growatt de 2026-05-07.

**Variáveis de ambiente (`.env`):** `HYPONTECH_EMAIL`, `HYPONTECH_PASSWORD`.

**Integração no `main.py`:**

- Import: `from modules.Hypontech import buscar_dados_completos as hypontech_buscar, traduzir_status as hypontech_status`
- `base_hypontech = []` inicializado junto às outras bases
- Bloco de sync: `if "hypontech" in marcas_presentes`
- Bloco de processamento: `elif marca == "hypontech"` — unpacks 4 valores e grava Col 7, 8, 9, 10

---

## [2026-05-29] — Adição de geração atual (Col I); limitação de geração mensal

**Arquivos alterados:** `modules/Hypontech.py`, `main.py`

**Reconhecimento da API:** endpoint `/v2/plant/list2` retorna por usina:
`status`, `time`, `plant_name`, `e_today` (kWh do dia), `e_total` (acumulado histórico), `power` (W instantâneo).

**Endpoints testados para e_month (todos retornaram 404):**
`/v2/plant/detail`, `/v2/plant/energy`, `/v2/plant/chart`, `/v2/plant/stat`, `/v2/plant/generation`, `/v2/plant/data`

**Limitação documentada:** A API Hypontech v2 **não expõe geração mensal por usina**. Campo `e_month` sempre retorna `None`.

**`traduzir_status` agora retorna 4 valores:**
`(status, last_update, etoday, e_month)` — padrão idêntico a Fronius/Solplanet/Solis.

**Mapeamento de colunas:**
- Col 7 → status
- Col 8 → last_update
- Col 9 → `e_today` (geração do dia em kWh)
- Col 10 → `None` (mensal indisponível na API)
