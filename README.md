#Fluxo Solar
Sistema de monitoramento automatizado para usinas fotovoltaicas. O software integra APIs de diferentes fabricantes de inversores para centralizar o status de operação dos clientes em uma planilha Excel.

Funcionamento
O sistema lê uma lista de clientes e marcas de inversores a partir do arquivo clientes.xlsx. Para cada registro, o script consulta a respectiva API, extrai o estado atual do equipamento e atualiza a planilha com os status padronizados: On-line, Off-line ou Alarme.

Estrutura do Projeto
main.py: Script principal que gerencia o fluxo de leitura, roteamento de marcas e escrita dos dados.

modules/: Pasta contendo as implementações específicas de cada fabricante (Solis, Growatt, etc.).

.env: Arquivo para armazenamento de chaves de API e tokens (não incluso no repositório).

clientes.xlsx: Base de dados local com as informações das usinas.
