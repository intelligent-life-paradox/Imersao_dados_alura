import streamlit as st

# Configuração da página - PRIMEIRO comando Streamlit
st.set_page_config(
    page_title='Dashboard de salários para área de dados',
    page_icon='🔍',
    layout='wide'
)

import pandas as pd
import plotly.express as px


'''---Configuração da página---
Define o título, ícone e layout da página'''

# carrega os dados
df = pd.read_csv("https://raw.githubusercontent.com/guilhermeonrails/data-jobs/refs/heads/main/salaries.csv")

renomear_colunas = {
    'work_year': 'ano',
    'experience_level': "senioridade",
    'employment_type': 'cargo',
    'job_title': 'titulo_trabalho',
    'salary': 'salario',
    'salary_currency': 'moeda',
    'salary_in_usd': 'salario_dolar',
    'employee_residence': 'residencia_empregado',
    'remote_ratio': 'locação_razao',
    'company_location': 'companhia',
    'company_size': 'tamanho_companhia'
}
df.rename(columns=renomear_colunas, inplace=True)

renomear_colunas_2 = {'titulo_trabalho': 'contrato'}
df.rename(columns=renomear_colunas_2, inplace=True)

df = df.dropna()

# --- Filtros ---
st.sidebar.header("filtros")
anos_disponiveis = sorted(df['ano'].unique())
anos_selecionados = st.sidebar.multiselect("ano", anos_disponiveis, default=anos_disponiveis)

# filtro por cargo
cargos_disponiveis = sorted(df['cargo'].unique())
cargos_selecionados = st.sidebar.multiselect("cargos", cargos_disponiveis, default=cargos_disponiveis)

# filtro por senioridade
senioridade_disponiveis = sorted(df['senioridade'].unique())
senioridade_selecionada = st.sidebar.multiselect("senioridade", senioridade_disponiveis, default=senioridade_disponiveis)

# filtro por tamanho da empresa
tamanho_disponiveis = sorted(df['tamanho_companhia'].unique())
tamanho_selecionado = st.sidebar.multiselect("tamanho_companhia", tamanho_disponiveis, default=tamanho_disponiveis)

#vamos fazer um filtro pelos 10 contratos mais frequentes e colocar uma opção para selecioná-los

top_10_contratos = df['contrato'].value_counts().nlargest(10).index.tolist()
contratos_selecionados = st.sidebar.multiselect(
    "Contratos mais frequentes",
    options=top_10_contratos,
    default=top_10_contratos
)


# aplica filtros
df_filtrado = df[
    (df['ano'].isin(anos_selecionados)) &
    (df['cargo'].isin(cargos_selecionados)) &
    (df['senioridade'].isin(senioridade_selecionada)) &
    (df['tamanho_companhia'].isin(tamanho_selecionado))
]

# --- Conteúdo principal ---
st.title("Dashboard de salários para área de dados")
st.markdown(
    "Dashboard interativo para análise de salários na área de dados, com filtros por ano, contrato, senioridade e tamanho da empresa. "
    "Selecione os filtros na barra lateral para personalizar a visualização dos dados."
)

# --- Métricas principais ---
st.subheader("Métricas principais (valores anuais em dólares)")
if not df_filtrado.empty:
    salario_medio = df_filtrado['salario_dolar'].mean()
    salario_minimo = df_filtrado['salario_dolar'].min()
    salario_maximo = df_filtrado['salario_dolar'].max()
    cargo_mais_repetido = df_filtrado['contrato'].mode()[0]
else:
    salario_medio = 0
    salario_minimo = 0
    salario_maximo = 0
    cargo_mais_repetido = "N/A"

col1, col2, col3, col4 = st.columns(4)
col1.metric("Salário médio", f"${salario_medio:,.2f}")
col2.metric("Salário mínimo", f"${salario_minimo:,.2f}")
col3.metric("Salário máximo", f"${salario_maximo:,.2f}")
col4.metric("Cargo mais repetido", cargo_mais_repetido)

st.markdown("---")


st.subheader("Empregados por país/ Tamanho da Empresa/ Tipo de Trabalho")
col_pie1, col_pie2, col_pie3 = st.columns(3)
with col_pie1:
    # --- Gráfico de Pizza: Tamanho da Companhia ---    
    df_tamanho = (
        df_filtrado['tamanho_companhia']
        .value_counts()
        .reset_index()
    )
    df_tamanho.columns = ['Tamanho da Companhia', 'Quantidade']  

    fig_tamanho = px.pie(
        df_tamanho,
        names='Tamanho da Companhia',
        values='Quantidade',
        title='Proporção por Tamanho da Companhia',
        hole=0.3
    )
    st.plotly_chart(fig_tamanho, use_container_width=True)


# --- Gráfico de Pizza: Residência dos Empregados ---
with col_pie2:
    df_residencia = (
        df_filtrado['residencia_empregado']
        .value_counts()
        .head(7)
        .reset_index()
    )
    df_residencia.columns = ['Residência', 'Quantidade'] 

    fig_residencia = px.pie(
        df_residencia,
        names='Residência',
        values='Quantidade',
        title='Proporção por Residência dos Empregados',
        hole=0.3
    )
    st.plotly_chart(fig_residencia, use_container_width=True)

# --- Gráfico de Pizza: tipo de trabalho remoto, presencial ou misto---
with col_pie3:
    df_remote = (
        df_filtrado['locação_razao']
        .value_counts()
        .reset_index()
    )

    df_remote.columns = ['Tipo de Trabalho', 'Quantidade']

    mapeamento_tipos_trabalho = {
        0: 'Presencial',
        50: 'Híbrido',
        100: 'Remoto'
    }
    df_remote['Tipo de Trabalho'] = df_remote['Tipo de Trabalho'].map(mapeamento_tipos_trabalho).fillna('Outro')

    fig_remote = px.pie(
        df_remote,
        names='Tipo de Trabalho',
        values='Quantidade',
        title='Proporção por Tipo de Trabalho',
        hole=0.3
    )
    st.plotly_chart(fig_remote, use_container_width=True)


st.markdown("---")
# --- Agrupamento por cargo e senioridade ---
st.subheader("Agrupamento por cargo e senioridade")
colgrafico1, colgrafico2 = st.columns(2)

if not df_filtrado.empty:
    # Gráfico 1: Top 10 cargos
    with colgrafico1:
        top_empregos = (
            df_filtrado.groupby('contrato')['salario_dolar']
            .mean()
            .nlargest(10)
            .sort_values(ascending=True)
            .reset_index()
        )
        graficos_contrato = px.bar(
            top_empregos,
            x='salario_dolar',
            y='contrato',
            orientation='h',
            title='Top 10 cargos com maiores salários médios'
        )
        graficos_contrato.update_layout(
            xaxis_title='Salário médio (USD)',
            yaxis_title='Cargo'
        )
        st.plotly_chart(graficos_contrato, use_container_width=True)

        # Boxplot top 10 cargos mais bem pagos
        top10_cargos_salario = (
            df_filtrado.groupby('contrato')['salario_dolar']
            .mean()
            .nlargest(10)
            .index
        )
        df_top10_cargos = df_filtrado[df_filtrado['contrato'].isin(top10_cargos_salario)]
        fig_box_contrato = px.box(
            df_top10_cargos,
            x='contrato',
            y='salario_dolar',
            title='Distribuição de Salários - Top 10 Cargos mais Bem Pagos',
            labels={'contrato': 'Cargo', 'salario_dolar': 'Salário em Dólar'}
        )
        st.plotly_chart(fig_box_contrato, use_container_width=True)

    # Gráfico 2: Evolução salarial por senioridade
    with colgrafico2:
        mapeamento_senioridade = {
            'EN': 'Junior-level',
            'MI': 'Pleno-level',
            'SE': 'Senior-level',
            'EX': 'Executivo-level'
        }
        df_senioridade = df_filtrado.copy()
        df_senioridade['senioridade'] = df_senioridade['senioridade'].map(mapeamento_senioridade)

        top_senioridade = (
            df_senioridade.groupby('senioridade')['salario_dolar']
            .mean()
            .sort_values(ascending=True)
            .reset_index()
        )
        graficos_senioridade = px.bar(
            top_senioridade,
            x='salario_dolar',
            y='senioridade',
            orientation='h',
            title='Evolução salarial por senioridade'
        )
        graficos_senioridade.update_layout(
            xaxis_title='Salário médio (USD)',
            yaxis_title='Senioridade'
        )
        st.plotly_chart(graficos_senioridade, use_container_width=True)

        # Boxplot por senioridade
        ordem_senioridade = ['Junior-level', 'Pleno-level', 'Senior-level', 'Executivo-level']
        fig_box_senioridade = px.box(
            df_senioridade,
            x='senioridade',
            y='salario_dolar',
            title='Distribuição de Salários por Senioridade',
            labels={'senioridade': 'Senioridade', 'salario_dolar': 'Salário em Dólar'},
            category_orders={'senioridade': ordem_senioridade}
        )
        st.plotly_chart(fig_box_senioridade, use_container_width=True)

else:
    st.warning("Nenhum dado disponível para os filtros selecionados :(")




st.subheader("Análise de Salário por País para os Cargos Selecionados")

st.markdown(''
'Este gráfico mostra os 10 países com os maiores salários médios para cada cargo selecionado. Os top 10 cargos mais frequentes encontrados nos dados foram selecionados tal qual na barra lateral.''')

st.markdown(''' caso haja dúvida quanto ao código de algum país, consulte a lista de códigos ISO 3166-1 alpha-2 [aqui](https://pt.wikipedia.org/wiki/ISO_3166-1).''')
if not df_filtrado.empty and contratos_selecionados:
    
    # Cria abas com base nos nomes dos contratos selecionados
    lista_de_abas = st.tabs(contratos_selecionados)

    # Itera sobre cada aba e o nome do contrato correspondente
    for i, contrato in enumerate(contratos_selecionados):
        
       
        with lista_de_abas[i]:
            
           
            df_cargo_especifico = df_filtrado[df_filtrado['contrato'] == contrato]

            if not df_cargo_especifico.empty:
                # Agrupa por país e calcula a média salarial
                df_salario_pais = (
                    df_cargo_especifico.groupby('companhia')['salario_dolar']
                    .mean()
                    .nlargest(10) # Pega o Top 10 países para este cargo
                    .reset_index()
                    .sort_values(by='salario_dolar', ascending=True)
                )

                fig_salario_pais = px.bar(
                    df_salario_pais,
                    x='salario_dolar',
                    y='companhia',
                    orientation='h',
                    title=f'Top 10 Países com Maior Salário Médio para {contrato}',
                    labels={'companhia': 'País', 'salario_dolar': 'Salário Médio (USD)'}
                )
                st.plotly_chart(fig_salario_pais, use_container_width=True)
            else:
                st.warning(f"Não há dados para '{contrato}' com os filtros atuais.")
else:
    st.warning("Nenhum dado disponível. Selecione ao menos um cargo e ajuste os filtros.")







# --- Gráfico de Linha: Evolução Salarial ao Longo dos Anos usando contratos top_10_contratos
st.subheader("Evolução Salarial ao Longo dos Anos para os Cargos Selecionados")
st.markdown('''PS: alguns cargos são muito recentes, portanto não possuem dados para todos os anos''')
if not df_filtrado.empty and contratos_selecionados:
    df_evolucao = (
        df_filtrado[df_filtrado['contrato'].isin(contratos_selecionados)]
        .groupby(['ano', 'contrato'])['salario_dolar']
        .mean()
        .reset_index()
    )

    fig_evolucao = px.line(
        df_evolucao,
        x='ano',
        y='salario_dolar',
        color='contrato',
        title='Evolução Salarial ao Longo dos Anos para os Cargos Selecionados',
        labels={'ano': 'Ano', 'salario_dolar': 'Salário Médio (USD)', 'contrato': 'Cargo'}
    )
    st.plotly_chart(fig_evolucao, use_container_width=True)


st.markdown("---")

st.subheader("dados do dataset")
st.dataframe(df_filtrado, use_container_width=True)




