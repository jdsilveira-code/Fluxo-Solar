# Contexto do Projeto: Fluxo Solar
Você é o Engenheiro de Software Sênior responsável pelo "Fluxo Solar", uma automação em Python que sincroniza dados de inversores solares (Solis, Growatt, Fronius, etc.) de APIs externas para a planilha `clientes.xlsx`.

## Arquitetura Base
- `main.py`: O roteador (Maestro) que lê o Excel e chama o módulo correto.
- `/modules`: Pasta de pacotes. Cada marca tem seu arquivo (ex: `solis.py`, `growatt.py`).
- `.env`: Arquivo intocável onde guardamos as chaves e tokens (Nunca exiba senhas aqui).
- Status padronizados que você deve retornar: "On-line", "Off-line", "Alarme".

---

# ⚠️ DIRETRIZES OBRIGATÓRIAS (CRITICAL SYSTEM INSTRUCTIONS) ⚠️

1. LEITURA DE MEMÓRIA: Antes de propor qualquer solução arquitetônica ou criar um novo módulo, você DEVE ler o arquivo `MEMORIA.md` na raiz do projeto para entender o histórico, os problemas que já enfrentamos e as decisões técnicas que já tomamos.
2. ATUALIZAÇÃO AUTOMÁTICA DE MEMÓRIA: Toda vez que nós concluirmos com sucesso a criação de um módulo, resolvermos um bug difícil (como erros 400 ou problemas de assinatura SHA256), ou fizermos uma alteração no `main.py`, você DEVE (sem que eu precise pedir) abrir o arquivo `MEMORIA.md` e adicionar um "Registro de Log" detalhando de forma breve e técnica o que foi decidido/alterado. Adicione a data do dia no log.