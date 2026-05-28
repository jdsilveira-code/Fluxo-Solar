# Fluxo Solar

O **Fluxo Solar** é um sistema de monitoramento automatizado voltado para usinas fotovoltaicas. O software integra APIs de diferentes fabricantes de inversores para centralizar o status de operação dos clientes, consolidando os dados em uma planilha Excel e oferecendo uma interface visual para acompanhamento.

> **Nota:** Este projeto encontra-se atualmente em fase de desenvolvimento.

---

## Funcionamento Geral

O sistema realiza a leitura de uma base de dados local (`clientes.xlsx`) contendo a lista de clientes e as respectivas marcas de seus inversores. Para cada registro, o script principal consulta a API do fabricante correspondente, extrai o estado atual do equipamento e os dados de desempenho, e atualiza a planilha.

Os status de operação são padronizados em:
* **On-line**
* **Off-line**
* **Alarme**

Além do status, o sistema captura as seguintes métricas de cada usina:
* Geração de energia em tempo real (atual).
* Geração de energia acumulada no mês vigente.

---

## Arquitetura e Estrutura do Projeto

O projeto está organizado da seguinte forma:

* **`main.py`**: Script principal que gerencia o fluxo de leitura, roteamento por fabricante e escrita dos dados consolidada.
* **`app.py`**: Interface gráfica desenvolvida em Streamlit para visualização interativa dos dados e monitoramento das usinas (ajuste o nome do arquivo caso necessário).
* **`modules/`**: Diretório que contém as implementações e integrações específicas de cada API de fabricante (Solis, Growatt, etc.).
* **`tests/`**: Diretório contendo os arquivos de testes de cada marca de inversor suportada.
* **`Claude.md`**: Documentação técnica e guia contextualizado estruturado para o consumo e assistência do modelo Claude (Anthropic).
* **Arquivos de memória**: Arquivos dedicados ao armazenamento de contextos específicos por marca de inversor para leitura do assistente Claude.
* **`.env`**: Arquivo para armazenamento seguro de variáveis de ambiente, chaves de API e tokens (não incluso no repositório por questões de segurança).
* **`clientes.xlsx`**: Base de dados local em formato de planilha com as informações cadastrais das usinas (não incluso no repositório).

---

## Marcas Suportadas

O sistema possui integração configurada para os seguintes fabricantes de inversores:

* Fronius
* Growatt
* Hypontech
* Solis
* Solplanet

---

## Pré-requisitos e Configuração

Como o projeto está em desenvolvimento, os passos básicos para execução local envolvem:

1. Clonar o repositório.
2. Criar o arquivo `.env` na raiz do projeto com as credenciais necessárias.
3. Estruturar o arquivo `clientes.xlsx` conforme o modelo aceito pelo sistema.
4. Executar o script principal ou a aplicação Streamlit.
