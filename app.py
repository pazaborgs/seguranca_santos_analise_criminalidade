import folium
import geopandas as gpd
import numpy as np
import plotly.express as px
import streamlit as st
from streamlit_folium import st_folium

# --- Configuração da página ---

st.set_page_config(layout='wide', page_title='Santos Safety Dashboard', page_icon='🛡️')

# --- CSS para boas práticas --- 

st.markdown("""
    <style>
            
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

        html, body, [class*='css']  {
            font-family: 'Poppins', sans-serif;
        }
        
        h1, h2, h3, h4, h5, h6, .stMarkdown, .stMetricLabel, .stMetricValue {
            font-family: 'Poppins', sans-serif !important;
        }
            
    </style
    """, unsafe_allow_html= True
)

# --- Carregamento dos dados ---

@st.cache_data
def load_data():
    return gpd.read_file('data/santos_data.geojson')

try:
    geodata = load_data()
except Exception as e:
    st.error(f'Erro ao carregar os dados: {e}')
    st.stop()

# --- Barra de Filtros (lateral) ---

st.sidebar.header('Filtros')

# Filtro de Visão

st.sidebar.markdown('#### 🎯 Foco da Análise')
map_vision = st.sidebar.radio(
    'O que você quer visualizar?',
    options=['Geral (Tudo)', 'Violência (Roubos)', 'Patrimônio (Furtos)', 'Crimes Graves a Vida', 'Drogas e Armas', 'Acidentes'],
    help='Isso mudará as cores e as notas do mapa baseadas no tipo de crime selecionado.'
)

map_col_dict = {
    'Geral (Tudo)': 'TOTAL_DANGER_SCORE',
    'Violência (Roubos)': 'Roubos (Geral)',
    'Patrimônio (Furtos)': 'Furtos (Geral)',
    'Crimes contra a Vida': 'Crimes contra a Vida',
    'Drogas e Armas': 'Drogas e Armas',
    'Acidentes': 'Acidentes de Trânsito'
}

active_column = map_col_dict.get(map_vision, 'TOTAL_DANGER_SCORE')

# Filtro de Período

st.sidebar.markdown('#### 🌙 Período')
period_selected = st.sidebar.selectbox(
    'Horário da Ocorrência',
    options=['Dia e Noite', 'Apenas Noite', 'Apenas Dia'],
    index=0
)

# Filtro de Notas de Segurança

st.sidebar.markdown('#### ⚠️ Nota Mínima de Segurança')
min_safety = st.sidebar.slider('Selecione uma nota mínima para comparação', 0.0, 10.0, 0.0, step = 0.5, help='0 = Crítico, 10 = Excelente')

# Filtro de Bairros

st.sidebar.markdown('#### 🏘️ Seleção de Bairros')
neighborhoods = sorted(geodata['NM_BAIRRO_MATCH'].unique())
neighborhood_selected = st.sidebar.multiselect('Escolha para comparar (Vazio = Todos)', 
                                               neighborhoods, 
                                               default = None, 
                                               placeholder = 'Selecione os bairros')

# Aplicação dos filtros

filtered_data = geodata.copy()

# 1. Define a coluna ativa baseada na visão do mapa

if active_column in filtered_data.columns:
    filtered_data['FILTERED_OCCURRENCES'] = filtered_data[active_column].fillna(0)
    target_values = np.sqrt(filtered_data[active_column].fillna(0))
else:
    filtered_data['FILTERED_OCCURRENCES'] = filtered_data['TOTAL_CRIMES']
    target_values = np.sqrt(filtered_data['TOTAL_DANGER_SCORE'].fillna(0))

# Recalcula o Score

min_v, max_v = target_values.min(), target_values.max()

if max_v > min_v:
    
    # Normalizamos de 0 a 9
    relative_score = (target_values - min_v) / (max_v - min_v) * 9
    
    # Subtraímos de 10, resultando em uma escala de 10.0 a 1.0
    filtered_data['SAFETY_SCORE'] = 10 - relative_score
else:
    filtered_data['SAFETY_SCORE'] = 10.0

# Garante que não exista valor menor que 1

filtered_data['SAFETY_SCORE'] = filtered_data['SAFETY_SCORE'].clip(lower=1.0).round(1)

# Filtro de Bairros

if neighborhood_selected:
    filtered_data = filtered_data[filtered_data['NM_BAIRRO_MATCH'].isin(neighborhood_selected)]

# Filtro de Nota Mínima

filtered_data = filtered_data[filtered_data['SAFETY_SCORE'] >= min_safety]

# Filtro de Período

if period_selected == 'Apenas Noite':
    # Aqui você pode decidir se filtra por volume de crimes noturnos
    filtered_data = filtered_data[filtered_data['NIGHT_CRIMES'] > 0]

# --- KPIs ---

st.title('🛡️ Santos Safety Dashboard')
st.markdown('##### *Análise de risco baseada em dados oficiais da SSP-SP (2025)*')
with st.expander('📚 Entenda como a nota é calculada', expanded=False):
    st.markdown("""
        ### Segurança, aos meus olhos.
        A nota de **0 a 10** não é um ranking absoluto contra outras cidades, mas sim uma **comparação interna** entre os bairros de Santos.
        
        * **Por que o Centro tem nota baixa?** Áreas comerciais e centrais possuem um fluxo de pessoas muito maior por m². Isso gera mais oportunidades de registros (furtos/roubos), resultando em uma **alta densidade criminal**, mesmo que o bairro não seja 'intransitável'.
        * **Por que os Morros e Porto têm notas altas?** 
          - 1. **Acesso Restrito:** Locais como o *Morro Santa Terezinha* possuem segurança privada e baixo fluxo de não-residentes.
          - 2. **Baixa Densidade Populacional:** Áreas portuárias e industriais têm poucos pedestres circulando, o que diminui drasticamente o crime de oportunidade (roubo de celular).
        
        **Metodologia:** Utilizei a **Raiz Quadrada da Densidade de Perigo** para garantir que a diferença entre o Centro e os bairros residenciais seja visível no mapa de forma justa.
    """)

if not filtered_data.empty:
    col1, col2, col3, col4 = st.columns(4)

    # Cálculos e métricas

    local_average_safety = filtered_data['SAFETY_SCORE'].mean()                             # Média de segurança local
    total_crimes = int(filtered_data['TOTAL_CRIMES'].sum())                                 # Total de crimes na área filtrada             
    safest_neighborhood = filtered_data.loc[filtered_data['SAFETY_SCORE'].idxmax()]         # Bairro mais seguro
    least_safe_neighborhood = filtered_data.loc[filtered_data['SAFETY_SCORE'].idxmin()]     # Bairro menos seguro

    with col1:
        st.metric('⭐ Nota Média de Segurança', f'{local_average_safety:.2f}/10')

    with col2:
        st.metric('🚨 Total de Incidentes', f'{total_crimes}')

    with col3:
        st.metric('🏆 Bairro Mais Seguro', safest_neighborhood['NM_BAIRRO_MATCH'], f'{safest_neighborhood['SAFETY_SCORE']:.1f}')

    with col4:
        st.metric('⚠️ Bairro Menos Seguro', least_safe_neighborhood['NM_BAIRRO_MATCH'], f'{least_safe_neighborhood['SAFETY_SCORE']:.1f}')
    
else:
    st.warning('Nenhum bairro atende aos filtros selecionados.')
    st.stop()

st.divider()

# --- Mapa Interativo ---

st.markdown('### 🗺️ Mapa de Segurança por Bairro')

    # Configuração do mapa

m = folium.Map(
    location=[-23.9618, -46.3322], 
    zoom_start = 14, 
    tiles='Cartodb dark_matter',
    zoom_control=False, 
    control_scale=False, 
    attribution_control=False)

# Adiciona os bairros ao mapa

folium.Choropleth(  
    geo_data = filtered_data,
    data = filtered_data,
    columns = ['NM_BAIRRO_MATCH', 'SAFETY_SCORE'],
    key_on = 'feature.properties.NM_BAIRRO_MATCH',
    fill_color='RdYlGn',
    fill_opacity = 0.7,
    line_opacity = 0.3,
    line_weight = 2,
    name = 'Nota de Segurança (0 a 10)',
    legend_name = 'Indice de Segurança por Bairro',
    highlight = True).add_to(m)
    
    
style_function = lambda x: {
    'fillColor': '#ffffff', 
    'color':'#000000', 
    'fillOpacity': 0.1, 
    'weight': 0.1, 
    'padding': '4px', 
    'border-radius': '20px'}
highlight_function = lambda x: {'fillColor': '#000000', 'color':'#000000', 'fillOpacity': 0.50, 'weight': 0.1}

# GeoJson Hover

hover = folium.features.GeoJson(
    data=filtered_data,
    style_function=style_function,
    control=False,
    highlight_function=highlight_function,
    tooltip=folium.features.GeoJsonTooltip(
        fields=['NM_BAIRRO_MATCH', 'FILTERED_OCCURRENCES', 'SAFETY_SCORE'],
        aliases=['📍 Bairro:', f'📊 Ocorrências — {map_vision}:', '🛡️ Índice de Segurança:'],
        style=(
            'background-color: #12151C; '
            'color: white; '
            'font-family: Poppins, sans-serif; '
            'font-size: 14px; '
            'padding: 15px; '
            'border-radius: 10px; '
            'border: 1px solid #00D4FF; '
            'box-shadow: 3px 3px 10px rgba(0,0,0,0.5);'
        ),
        localize=True,
        sticky=True
    )
).add_to(m)

st_folium(m, width = 'stretch', height=600, returned_objects = [])

st.divider()

# --- Gráficos ---

st.markdown('### 📊 Bairros Mais e Menos Seguros')

g_col1, g_col2 = st.columns(2)

with g_col1:


    # Col1- Bairros Mais Seguros

    with g_col1:
        top_safest = filtered_data.sort_values('SAFETY_SCORE', ascending=False).head(10)
        fig1 = px.bar(
                        top_safest, x='SAFETY_SCORE', y='NM_BAIRRO_MATCH', 
                        orientation='h',
                        text = 'SAFETY_SCORE',
                        labels={'SAFETY_SCORE': 'Índice de Segurança', 'NM_BAIRRO_MATCH': 'Bairro'},
                        title='Top 10 Bairros Mais Seguros',
                        color='SAFETY_SCORE', color_continuous_scale='RdYlGn', range_color=[0, 10]
                        )
        fig1.update_layout(yaxis={'categoryorder':'total ascending', 'title': ''}, xaxis={'title': ''}, height=600)
        st.plotly_chart(fig1, width = 'stretch')

    # Col2 - Bairros Mais Críticos

    with g_col2:
        top_least_safe = filtered_data.sort_values('SAFETY_SCORE', ascending=True).head(10)
        fig2 = px.bar(
                        top_least_safe, x='SAFETY_SCORE', y='NM_BAIRRO_MATCH', 
                        orientation='h',
                        text = 'SAFETY_SCORE',
                        labels={'SAFETY_SCORE': 'Índice de Segurança', 'NM_BAIRRO_MATCH': 'Bairro'},
                        title='Top 10 Bairros Mais Críticos',
                        color='SAFETY_SCORE', color_continuous_scale='RdYlGn', range_color=[0, 10]
                        )
        fig2.update_layout(yaxis={'categoryorder':'total ascending', 'title': ''}, xaxis={'title': ''}, height=600)
        st.plotly_chart(fig2, width = 'stretch')

# --- Tabela de Dados ---

with st.expander('📋 Ver Dados Detalhados dos Bairros'):
    st.dataframe(
        filtered_data[['NM_BAIRRO_MATCH', 'SAFETY_SCORE', 'TOTAL_CRIMES', 'DANGER_DENSITY']].sort_values(by='SAFETY_SCORE', ascending=False),
        column_config={
            'NM_BAIRRO_MATCH': 'Bairro',
            'SAFETY_SCORE': st.column_config.ProgressColumn('Nota (0-10)', min_value=0, max_value=10, format='%.1f'),
            'TOTAL_CRIMES': st.column_config.NumberColumn('Total de Ocorrências'),
            'DANGER_DENSITY': st.column_config.NumberColumn('Densidade de Risco (por km²)', format='%.2f'),
        },
        width = 'stretch',
        hide_index = True
    )



    
