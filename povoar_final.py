import pandas as pd
import sqlite3

# Caminhos dos arquivos
excel_file = 'whc-sites-2024_final.xlsx'
db_file = 'WorldHeritage.db'

# Conectar ao banco de dados SQLite
conn = sqlite3.connect(db_file)

# Carregar as abas do Excel
excel_data = pd.ExcelFile(excel_file)
sheet_names = excel_data.sheet_names

# Loop através das abas para inserir dados nas tabelas
for sheet in sheet_names:
    # Ler os dados da aba atual
    df = excel_data.parse(sheet)
    
    # Remover espaços dos nomes das colunas, se necessário
    df.columns = [col.strip() for col in df.columns]
    
    # Inserir os dados no banco de dados
    df.to_sql(sheet, conn, if_exists='replace', index=False)
    print(f"Tabela '{sheet}' foi inserida com sucesso no banco de dados.")

# Fechar a conexão
conn.close()
print("Processo concluído.")
