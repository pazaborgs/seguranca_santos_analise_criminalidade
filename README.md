
# 🛡️ Santos Safety Dashboard

    Análise de Inteligência Geográfica e Segurança Pública para a cidade de Santos/SP.

Um dashboard interativo desenvolvido em Python e Streamlit que transforma dados brutos de criminalidade em insights visuais intuitivos. O projeto utiliza geolocalização para mapear a densidade criminal, diferenciar gravidade de ocorrências e calcular um Score de Segurança (0-10) relativo para cada bairro.

## 🎯 O Problema e a Solução

Dados de segurança pública geralmente são disponibilizados em planilhas extensas e difíceis de interpretar. Além disso, olhar apenas para o "número total de crimes" gera distorções como:

- Um bairro com 100 **furtos de celular** não é necessariamente mais perigoso que um bairro com 10 **homicídios**, embora o número absoluto seja maior.
- A percepção de segurança muda drasticamente entre o **Dia e a Noite**.

Este projeto resolve isso ao:

- **Ponderar a Gravidade**: Aplica pesos diferentes para crimes contra a vida vs. crimes patrimoniais
- **Contextualizar**: Permite filtrar por tipo de crime (ex: "Onde mais se rouba carros?").
- **Normalizar**: Cria uma nota de 0 a 10 que permite comparar bairros residenciais, comerciais e turísticos de forma justa.

## 📊 Fonte dos Dados

Os dados base foram obtidos através do portal de transparência da Secretaria de Segurança Pública de São Paulo (SSP-SP).

- **Fonte Oficial**: [SSP-SP - Transparência dos Dados](https://www.ssp.sp.gov.br/estatistica/consultas)
- **Período Analisado**: 2025 (Dados consolidados)
- **Tratamento**: Os dados brutos passaram por um processo de ETL (Extração, Transformação e Carga) para limpeza, geocodificação (transformação de endereços em coordenadas) e agragação por bairros oficiais de Santos.

## ⚙️ Funcionalidades Principais

- 🗺️ **Mapa Coroplético Interativo**: Visualização térmica dos bairros baseada no índice selecionado.
- 🔍 **Filtros Inteligentes**: Tipo de visão (score ponderado x tipo de crime), período do dia e local (bairro).
- 📈 **KPIs Dinâmicos**: As métricas se adaptam ao filtro (ex: ao selecionar "Roubos", o KPI mostra a soma de roubos, não o total geral).


## 🧠 Metodologia por trás do "Safety Score"

A nota de segurança não é um ranking oficial do governo, mas um indicador estatístico relativo desenvolvido para este projeto.

- **Pesos (Weights)**: Cada natureza criminal recebeu um peso baseado no impacto na sensação de segurança:

        🔴 Crimes contra a Vida: Peso 10

        🟠 Roubos (Violência): Peso 6

        🟡 Furtos (Patrimônio): Peso 2

- **Densidade de Perigo**: Soma-se (Quantidade * Peso) para cada bairro.
- **Normalização**: Aplica-se uma escala relativa onde o bairro com maior densidade recebe nota próxima de 1.0 e o com menor densidade nota 10.0.

## 🛠️ Tecnologias Utilizadas

- **Linguagem**: Python
- **Frontend/App**: Streamlit
- **Mapas**: Folium & streamlit-folium
- **Manipulação de Dados**: Pandas & NumPy
- **Geoprocessamento**: Geopandas & Shapely
- **Visualização de Dados**: Plotly Express 

##  🚀 Como Executar o Projeto

Você pode acessar o dashboard rodando diretamente no navegador através do Streamlit Cloud:

[👉🏽 Clique aqui para acessar o Dashboard Online](https://djm7djbwzttvjbqcdvvjby.streamlit.app/)

### 💻 Rodando Localmente

1. Clone o Repositório

        git clone https://github.com/pazaborgs seguranca_santos_analise_criminalidade

2. Instale as Dependências

        pip install -r requirements.txt

3. Execute o App:

        streamlit run app.py

## 📂 Estrutura do Projeto

    santos-safety-dashboard/
    ├── app.py                      # Aplicação principal
    ├── data/
    │   └── santos_data.geojson     # Base de dados tratada
    ├── requirements.txt            # Dependências do projeto
    └── README.md                   # Documentação

## 👨‍💻 Autor


[👉🏽 Autor do Projeto - Patrick Regis](https://www.linkedin.com/in/patrickrgsanjos)

    Este projeto é estritamente educativo e analítico, não representando opinião oficial dos órgãos de segurança pública.