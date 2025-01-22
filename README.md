# Projeto: World Heritage

Este projeto é um  Flask para consulta e visualização de dados relacionados aos patrimónios mundiais da Unesco.

## Estrutura do Projeto

A organização dos arquivos deve seguir a estrutura abaixo:

```
/Trabalho WH
├── app_heritage.py          # Código main do Flask
├── WorldHeritage.db         # Base de dados SQLite
├── querys_funcoes.py        # Funções e consultas para interação com a base de dados
└── templates/               # Pasta com os templates HTML do projeto
    ├── query1.html          # Página de resultados para Q1
    ├── query2.html          # Página de resultados para Q2
    ├── query3.html          # Página de resultados para Q3
    ├── query4.html          # Página de resultados para Q4
    ├── query5.html          # Página de resultados para Q5
    ├── query6.html          # Página de resultados para Q6
    ├── query7.html          # Página de resultados para Q7
    ├── query8.html          # Página de resultados para Q8
    ├── query9.html          # Página de resultados para Q9
    ├── query10.html         # Página de resultados para Q10
    ├── query11.html         # Página de resultados para Q11
    ├── query12.html         # Página de resultados para Q12
    ├── home.html            # Página inicial
    ├── results.html         # Resultados da pesquisa por categoria
    └── region_results.html  # Resultados da pesquisa por região
```

## Configuração

1. **Instale os Módulos**  
   Instale as bibliotecas necessárias:  
   ```bash
   pip install flask pandas matplotlib
   ```

2. **Base de dados**  
   A base de dados deve ser descarregada como `WorldHeritage.db`, e deve conter as tabelas necessárias para que as consultas funcionem corretamente.

3. **Templates**  
   Certifique-se de que todos os arquivos HTML estejam na pasta `templates/` conforme descrito na estrutura acima.

## Como Executar

1. Inicie o servidor Flask:  
   ```bash
   python app_heritage.py
   ```

2. Acesse o site em [http://127.0.0.1:5000](http://127.0.0.1:5000).

## Funcionalidades

- **Página Inicial**  
  Permite realizar uma pesquisa por categoria ou região.

- **Resultados Detalhados**  
  Exibe tabelas e gráficos gerados dinamicamente para as perguntas de Q1 a Q12.

- **Listagem de Sítios**  
  Mostra todos os sítios registrados no banco de dados com a opção de visualizar detalhes de cada um.

## Módulos

- **Python 3.8+**  
- **Bibliotecas**: Flask, Pandas, Matplotlib
