# MEMORIA.md — Fluxo Solar

Histórico técnico de decisões, bugs resolvidos e alterações relevantes.

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
- Import adicionado: `from modules.Fronius import buscar_dados_completos as fronius_buscar, traduzir_status as fronius_status`
- `base_fronius = []` inicializado junto com as outras bases
- Bloco de sync: `if "fronius" in marcas_presentes` → chama `fronius_buscar()`
- Bloco de processamento: `elif marca == "fronius"` → chama `fronius_status()`
- Nenhuma outra funcionalidade do `main.py` foi alterada
