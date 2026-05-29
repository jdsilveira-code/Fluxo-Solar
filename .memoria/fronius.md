# .memoria/fronius.md — Histórico Técnico: Fronius

---

## [2026-04-28] — Módulo Fronius: implementação final e integração no main.py

**Arquivos alterados:** `modules/Fronius.py`, `main.py`

**Descoberta crítica de autenticação:**
A API Fronius Solar.web (SWQAPI) NÃO usa JWT via endpoint `/iam/jwt` na prática.
Tentativas de autenticar via POST com body JSON retornaram erro 401 com a mensagem
`"AccessKeyId and Value not sent."`.
A autenticação correta é via **headers HTTP diretos** em cada requisição:

- `AccessKeyId: <valor>`
- `AccessKeyValue: <valor>`

**Variáveis de ambiente (`.env`):**

- `FRONIUS_API_ID` → header `AccessKeyId`
- `FRONIUS_API_VALUE` → header `AccessKeyValue`

**Estrutura final do módulo (`modules/Fronius.py`):**

- `_cabecalhos()`: monta os headers com as credenciais
- `buscar_dados_completos()`: GET paginado em `/pvsystems` com os headers; retorna lista de usinas
- `traduzir_status(nome_cliente, lista_fronius)`: busca case-insensitive por nome; mapeia
  `running` → On-line | `warning`/`error` → Alarme | `offline` → Off-line

**Integração no `main.py`:**

- Import: `from modules.Fronius import buscar_dados_completos as fronius_buscar, traduzir_status as fronius_status`
- `base_fronius = []` inicializado junto com as outras bases
- Bloco de sync: `if "fronius" in marcas_presentes` → chama `fronius_buscar()`
- Bloco de processamento: `elif marca == "fronius"` → chama `fronius_status()`

---

## [2026-05-28] — Mapeamento definitivo de endpoints e campos (confirmado por diagnóstico)

**Arquivos alterados:** `modules/Fronius.py`

**Endpoints e campos confirmados:**

| Dado | Endpoint | Campo |
|------|----------|-------|
| Status online | `GET /pvsystems/{id}/flowdata` | `payload["status"]["isOnline"]` (bool) |
| Última atualização | `GET /pvsystems/{id}/flowdata` | `payload["data"]["logDateTime"]` (ISO timestamp) |
| Geração diária | `GET /pvsystems/{id}/aggrdata?from=YYYY-MM-01&to=YYYY-MM-DD` | dia cujo `logDateTime == hoje` → canal `EnergyProductionTotal` (Wh ÷ 1000) |
| Geração mensal | mesma chamada aggrdata | soma de todos os `EnergyProductionTotal` no array `data` (Wh ÷ 1000) |

**Estrutura confirmada do aggrdata:**
```
{ "data": [ { "logDateTime": "YYYY-MM-DD", "channels": [
    { "channelName": "EnergyProductionTotal", "channelType": "Energy", "unit": "Wh", "value": N },
    ...
  ] }, ...], "links": { "totalItemsCount": N } }
```
Params corretos: `from`/`to` (ISO date strings). Params errados: `dateFrom`/`dateTo`, `period=month`.

**Paginação de /pvsystems:** total de usinas em `res["links"]["totalItemsCount"]` (não `totalCount`).

**Mapeamento de status:** `isOnline: true` → On-line | `false` → Off-line | `None` → Sem dados. Não há campo de Alarme na SWQAPI.

---

## [2026-05-28] — Correção completa: status, geração diária e mensal (pós-diagnóstico)

**Arquivos alterados:** `modules/Fronius.py`

**Descobertas críticas do diagnóstico:**

| Campo | Onde estava errado | Fonte correta confirmada |
|-------|--------------------|--------------------------|
| `status` | `sistema["status"]` — não existe em `/pvsystems` | `flowdata["status"]["isOnline"]` (bool) |
| `totalCount` | `res["totalCount"]` — campo inexistente | `res["links"]["totalItemsCount"]` |
| `lastDataTransfer` | Campo inexistente na resposta | `flowdata["data"]["logDateTime"]` |
| `etoday` | Tentava `flowData.site.E_Day` (SolarAPIv1 local) | Canal `channelType == "Energy"` no flowdata (pode ser None se inversor não expõe) |
| `e_month` | `aggrdata?dateFrom=...&dateTo=...` → HTTP 400 | Parâmetros incorretos; código tenta `from`/`to` e `period=month` — confirmar em produção |

**Arquitetura final:**
- `_buscar_dados_usina(pv_id)` substitui `_buscar_geracao()` — retorna dict `{is_online, last_update, etoday, e_month}`
- `buscar_dados_completos()`: paginação corrigida; enriquece cada usina via `.update()`
- `traduzir_status()`: usa `is_online` bool: `True`→On-line, `False`→Off-line, `None`→Sem dados

**Pendente:** Parâmetros corretos do `aggrdata` para geração mensal ainda a confirmar — rodar `python -m modules.Fronius` e observar seção [3].

---

## [2026-05-28] — Geração diária e mensal: mapeamento e implementação

**Arquivos alterados:** `modules/Fronius.py`, `main.py`

**Mapeamento de campos (SWQAPI cloud vs SolarAPIv1 local):**
- O `files/fronius.json` documenta a **SolarAPIv1 (API local)**: tem `DAY_ENERGY` mas **não tem campo mensal**.
- O módulo usa a **SWQAPI (cloud)**: `https://api.solarweb.com/swqapi`

**Endpoints SWQAPI adicionados:**
- `GET /pvsystems/{pvSystemId}/flowdata` → geração diária: `flowData.site.E_Day` (Wh ÷ 1000 = kWh)
- `GET /pvsystems/{pvSystemId}/aggrdata?period=month&dateFrom=YYYY-MM-01&dateTo=YYYY-MM-DD`
  → geração mensal: campo `energyProductionKwh` direto ou soma de `aggrData[].energyProductionKwh`

**Alterações no módulo:**
- Nova função `_buscar_geracao(pv_system_id)`: chama flowdata + aggrdata e retorna `(etoday_kwh, e_month_kwh)`
- `buscar_dados_completos()`: após paginar `/pvsystems`, enriquece cada sistema com `etoday` e `e_month`; `pvSystemId` obtido via `sistema.get("pvSystemId") or sistema.get("id")`
- `traduzir_status()`: agora retorna 4 valores `(status, last_update, etoday, e_month)` — padrão idêntico ao Solplanet

**Integração em `main.py`:**
- Bloco de sync Fronius descomentado
- Bloco de processamento: `if marca == "fronius"` com desempacotamento de 4 valores; escreve nas colunas 9 (I) e 10 (J)

**Alerta de verificação:** Os nomes dos campos da SWQAPI (`flowData.site.E_Day`, `energyProductionKwh`) foram inferidos — confirmar em produção via log da resposta bruta caso os valores apareçam como `None`.

---

## [2026-05-13] — Criação do fronius_match.py: exportação de nomes da API Fronius

**Arquivo criado:** `fronius_match.py`

**Comportamento:** Idêntico ao `growatt_match.py` simplificado. Chama `buscar_dados_completos()`
do módulo Fronius, ordena os nomes (`u.get("name")`) alfabeticamente e gera `fronius_nomes.xlsx`
com os nomes na coluna A (aba "Usinas Fronius"). Cabeçalho laranja (#FF6600) para diferenciar
visualmente do arquivo Growatt (azul). Filtra entradas sem campo `name` antes de salvar.
