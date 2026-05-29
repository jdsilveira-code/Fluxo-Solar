# Fluxo Solar

Automação em Python que sincroniza dados de inversores solares de múltiplas APIs externas para uma planilha Excel centralizada. O sistema consulta cada fabricante de forma independente, normaliza os dados e escreve status, geração diária e geração mensal diretamente em `clientes.xlsx`.

---

## Como funciona

O `main.py` lê a planilha, detecta automaticamente quais marcas estão presentes e conecta apenas às APIs necessárias. Em seguida, percorre cada cliente linha a linha, localiza a usina correspondente na API (via correspondência fuzzy de nomes) e atualiza as colunas de status e geração.

**Etapas de execução:**

1. **Sincronização com APIs** — baixa o cache completo de cada marca detectada na planilha
2. **Processamento** — cruza cada linha da planilha com o cache e resolve o status
3. **Salvamento** — persiste as alterações no `clientes.xlsx`

---

## Marcas suportadas

| Marca       | API                              | Autenticação          | Geração Diária | Geração Mensal |
|-------------|----------------------------------|-----------------------|:--------------:|:--------------:|
| Solis       | soliscloud.com:13333             | HMAC-SHA1 + MD5       | Sim            | Sim            |
| Growatt     | openapi.growatt.com              | Token                 | —              | —              |
| Fronius     | api.solarweb.com (Solar.web)     | AccessKeyId/Value     | Sim            | Sim            |
| Solplanet   | aisweicloud.com                  | HMAC-SHA256 + Nonce   | Sim            | Sim            |
| Hypontech   | api.hypon.cloud                  | Bearer (login/senha)  | Sim            | —              |

> Geração mensal Growatt e Hypontech não são expostas pela respectiva API na versão atual.

**Status padronizados retornados:** `On-line`, `Off-line`, `Alarme`, `Sem dados`, `Não encontrado`

---

## Estrutura do projeto

```text
Fluxo-Solar/
├── main.py               # Orquestrador principal (lê, roteia, salva)
├── app.py                # Entrypoint alternativo
├── clientes.xlsx         # Base de dados local das usinas
├── .env                  # Credenciais das APIs (não versionado)
│
├── modules/
│   ├── Solis.py          # Integração SolisCloud
│   ├── Growatt.py        # Integração Growatt OpenAPI
│   ├── Fronius.py        # Integração Fronius Solar.web
│   ├── Solplanet.py      # Integração Solplanet/Aiswei
│   ├── Hypontech.py      # Integração Hypontech Cloud
│   └── utils.py          # Correspondência fuzzy de nomes
│
└── tests/
    ├── Api_solis.py
    ├── Api_growatt.py
    ├── Fronius_teste.py
    ├── teste_solplanet.py
    ├── teste_hypontech.py
    ├── test_fuzzy_matching.py
    └── ...
```

---

## Colunas escritas na planilha

| Coluna | Conteúdo              |
|--------|-----------------------|
| 7      | Status                |
| 8      | Última Atualização    |
| 9      | Geração Hoje (kWh)    |
| 10     | Geração Mensal (kWh)  |

---

## Configuração

**1. Instale as dependências:**

```bash
pip install requests openpyxl python-dotenv
```

**2. Configure o `.env` com as credenciais de cada marca utilizada:**

```env
# Solis
SOLIS_API_ID=
SOLIS_API_SECRET=

# Growatt
GROWATT_TOKEN=

# Fronius
FRONIUS_API_ID=
FRONIUS_API_VALUE=

# Solplanet
SOLPLANET_ID=
SOLPLANET_SECRET=
SOLPLANET_TOKEN=

# Hypontech
HYPONTECH_EMAIL=
HYPONTECH_PASSWORD=
```

**3. Execute:**

```bash
python main.py
```

---

## Correspondência de nomes

O módulo `utils.py` usa três estratégias em cascata para vincular o nome da planilha ao nome retornado pela API:

1. **Substring bidirecional** — verifica se um nome contém o outro (após normalização)
2. **Token majority overlap** — compara conjuntos de tokens, tolerando ordem diferente e abreviações
3. **Fuzzy ratio** (threshold 0.75) — `difflib.SequenceMatcher` como último recurso

Acentos, stopwords jurídicas (`ltda`, `me`, `eireli`) e termos genéricos (`usina`, `microgeracao`) são removidos antes da comparação.

---

## Observações técnicas

- **Fronius** realiza buscas em paralelo com `ThreadPoolExecutor` (20 workers) para minimizar o tempo de coleta de dados por usina.
- **Solis** usa campos `dayEnergy1` / `monthEnergy1` (sempre em kWh), evitando a normalização para MWh aplicada nos campos sem sufixo em usinas de grande geração.
- O `main.py` detecta marcas presentes na planilha antes de conectar às APIs — marcas ausentes não geram chamadas desnecessárias.
