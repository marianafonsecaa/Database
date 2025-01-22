import pandas as pd

# Função para transformar a tabela
def transformar_tabela(input_file, output_file):
    # Carregar o arquivo Excel
    df = pd.read_excel(input_file, sheet_name='Folha1')  # Supondo que a primeira aba seja 'Sheet1'
    
    # Criar uma lista vazia para armazenar as linhas transformadas
    transformadas = []
    
    # Iterar sobre as linhas da tabela original
    for index, row in df.iterrows():
        sitioid = row['sitiosid']  # O 'sitiosid' permanece constante em cada linha
        
        # Para os critérios C1 a C6
        for criterioid in range(1, 7):  # Os critérios vão de C1 a C6
            criterio_col = f'C{criterioid}'  # Nome da coluna do critério (C1, C2, ..., C6)
            if criterio_col in row:  # Verificar se a coluna existe
                valor = row[criterio_col]  # Valor correspondente a cada critério
                transformadas.append([sitioid, criterioid, valor])  # Adicionar a linha transformada
        
        # Para os critérios N7 a N10
        for criterioid in range(7, 11):  # Os critérios vão de N7 a N10
            criterio_col = f'N{criterioid}'  # Nome da coluna do critério (N7, N8, ..., N10)
            if criterio_col in row:  # Verificar se a coluna existe
                valor = row[criterio_col]  # Valor correspondente a cada critério
                transformadas.append([sitioid, criterioid, valor])  # Adicionar a linha transformada
    
    # Criar um DataFrame com a tabela transformada
    df_transformada = pd.DataFrame(transformadas, columns=['sitiosid', 'criterioid', 'valor'])
    
    # Salvar a tabela transformada em uma nova aba no mesmo arquivo Excel
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Original')  # Salvar a tabela original
        df_transformada.to_excel(writer, index=False, sheet_name='Transformada')  # Salvar a tabela transformada

# Caminho do arquivo de entrada e saída
input_file = 'rascunho.xlsx'  # Substitua pelo caminho do seu arquivo
output_file = 'tabela_transformada.xlsx'  # Arquivo de saída com a aba transformada

# Executar a transformação
transformar_tabela(input_file, output_file)

print("Transformação concluída com sucesso!")
