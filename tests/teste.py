import csv
from pathlib import Path

# Configura o caminho para salvar na mesma pasta do script
pasta_atual = Path(__file__).parent
caminho_csv = pasta_atual / 'matches.csv'

# Aqui estão os dados exatos da Fronius que mapeamos
dados_fronius = [
    ["Nome Original na Planilha", "Nome Correto (Fronius)"],
    ["ADELSON CARVALHO FERREIRA", "Microgeração Adelson"],
    ["Adherbal Borges", "Microgeração Adherbal"],
    ["ALINE MAULAZ CARLOS COSTA", "Microgeração Aline Maulaz"],
    ["ALISON PEREIRA SILVA", "Microgeração ALISON PEREIRA SILVA"],
    ["ÂNGELO MARIANO MATTEDI", "Microgeração Angelo"],
    ["Bruno De Moraes Ferreira Volpini", "Microgeração Bruno Volpini"],
    ["CLIMÉRIO DUBBERSTEIN", "Microgeração Climério"],
    ["COMERCIAL PROTEGER LTDA", "Microgeração Proteger"],
    ["DIMARCOS BERTHOLINI DO ROSÁRIO", "MICROGERACAO DIMARCOS"],
    ["Edgard Valle de Souza", "Microgeração Edgar"],
    ["ELTON AREIA ALVES DE SOUZA / Luciano Pinto da Silva", "Microgeração Luciano Pinto"],
    ["Fernanda Nunes", "Microgeraçao Fernanda Nunes"],
    ["Fernanda Vieira Pena Barbosa de Medeiros", "Microgeração Fernanda"],
    ["Fernando Carlos Cordeiro dos Santos", "Microgeração Fernando"],
    ["GEOBSON SOUZA DA CONCEIÇÃO", "Microgeração Geobson"],
    ["Jailson Ferreira Coelho", "Microgeração Jailson Ferreira Coelho"],
    ["JOÃO BATISTA RANGEL RIBEIRO", "Microgeração João Batista"],
    ["José Flávio Guedes Turra", "Microgeração José Turra"],
    ["JOSÉ GERALDO MARTINS COELHO", "MicroGeração José Geraldo"],
    ["José Renato Gava", "Microgeração José Renato Gava"],
    ["JOSIMAR AVANCINI", "Microgeração Josimar"],
    ["KEILA KONZEN", "Microgeração Keila Konzen"],
    ["Leonardo Lence", "Microgeração Leonardo Lence"],
    ["LEONARDO LIMA LOBATO", "Microgeração LEONARDO LIMA"],
    ["LEONIA TOZETTI SANTOS", "Microgeração Leonia"],
    ["MARCELO MATRUD BICHARA JUNIOR", "Microgeração Marcelo Bichara"],
    ["MARCELO RIZZI", "Microgeração Marcelo Rizzi"],
    ["Marcial Luiz Spagnol", "Microgeraçao Marcial"],
    ["MARGARETH COELHO", "Microgeração Margareth"],
    ["MARTA VELTEMAN - BAR DO ALEMAO", "Microgeração Marta Valteman"],
    ["Mateus Leitão / Bruno De Moraes Ferreira Ramos Volpini", "Microgeração Mateus Leitão"],
    ["MERCADINHO - ALIPIO GONÇALVES FLOR", "Microgeração Alipio"],
    ["NAIR CORSINO MENDES", "Microgeração Nair Corcino"],
    ["OLIONDE PEREIRA RAMOS", "Microgeração Olionde"],
    ["PAULO CESAR DA SILVA", "Microgeração Paulo Cesar"],
    ["RAGEM GOMES DE MENEZES", "Microgeração Ragem"],
    ["ROBERTO HENRIQUE SOARES", "Microgeração Roberto Soares"],
    ["Rodolfo Zamborlini Fraga", "Microgeração Rodolfo Fraga"],
    ["SAMIR HAIDER GHABRIS", "Microgeração Samir Haider"],
    ["TÉLIO DE ASSIS ARANTES", "Microgeração Telio"],
    ["THADEU DE OLIVEIRA", "Microgeração Thadeu"],
    ["WILLIAN VIEIRA CRESPO", "Microgeração Wilian Crespo"],
    ["Willis - RAQUEL PEREIRA SILVA CEZAR", "Microgeração Willis"],
    ["Wilma Da Vitoria Barbosa", "Microgeração Wilma da Vitória"]
]

try:
    # A codificação utf-8-sig garante que não haverá problemas com os acentos
    with open(caminho_csv, mode='w', encoding='utf-8-sig', newline='') as f:
        escritor = csv.writer(f, delimiter=',') # Força o uso da vírgula
        escritor.writerows(dados_fronius)
    
    print(f"✅ Sucesso! O arquivo 'matches.csv' foi gerado perfeitamente.")
    print(f"Ele está salvo em: {caminho_csv}")
except Exception as e:
    print(f"❌ Erro ao criar o arquivo: {e}")