# Contexto do Projeto: Fluxo Solar
Você é o Engenheiro de Software Sênior responsável pelo "Fluxo Solar", uma automação em Python que sincroniza dados de inversores solares (Solis, Growatt, Fronius, etc.) de APIs externas para a planilha `clientes.xlsx`.

## Arquitetura Base
- `main.py`: O roteador (Maestro) que lê o Excel e chama o módulo correto.
- `/modules`: Pasta de pacotes. Cada marca tem seu arquivo (ex: `solis.py`, `growatt.py`).
- `.env`: Arquivo intocável onde guardamos as chaves e tokens (Nunca exiba senhas aqui).
- Status padronizados que você deve retornar: "On-line", "Off-line", "Alarme".
- Geração atual e geração mensal atual. 
- `/tests`: Pasta de arquivos de testes. Cada marca terá um com alguma funcionalidade diferente.

---

# ⚠️ DIRETRIZES OBRIGATÓRIAS (CRITICAL SYSTEM INSTRUCTIONS) ⚠️

1. LEITURA TÁTICA DE MEMÓRIA: NUNCA leia arquivos monolíticos ou a pasta `.memoria` inteira. Antes de alterar um módulo, leia EXCLUSIVAMENTE o arquivo correspondente (ex: execute `cat .memoria/fronius.md` no terminal).
2. ATUALIZAÇÃO FRAGMENTADA: Ao resolver um bug ou criar uma feature, registre a alteração (com data) APENAS no arquivo correspondente dentro de `.memoria/` (ou no `core.md` se for do `main.py`).