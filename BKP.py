from IPython.display import display, HTML
import pandas as pd
import pygsheets
import os
import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="Exportação (Sertranding)",
    page_icon="imagens/cotralti_logo.png",
    layout="wide",
)

# Formatação brasileira de valores


def format_number(value, prefix='R$'):
    if pd.isna(value):
        return f"{prefix} 0,00"
    for unit in ['', ' mil']:
        if value < 1000:
            return f"{prefix} {value:,.2f}{unit}".replace(",", "X").replace(".", ",").replace("X", ".")
        value /= 1000
    return f"{prefix} {value:,.2f} milhões".replace(",", "X").replace(".", ",").replace("X", ".")

# Conexão com Google Sheets


@st.cache_resource
def conectar_planilha():
    credenciais = pygsheets.authorize(
        service_file=os.path.join(os.getcwd(), 'cred.json'))
    url = "https://docs.google.com/spreadsheets/d/1l7G_4VAQGyN9cfmpsS-_bnjfzSqXRJViZMCZ8z6vXSc/edit#gid=0"
    arquivo = credenciais.open_by_url(url)
    aba = arquivo.worksheet_by_title("Sertranding")
    return aba


aba = conectar_planilha()

# Carregamento dos dados


@st.cache_data(show_spinner=False)
def carregar_dados():
    data = aba.get_all_values()
    data = list(
        map(list, zip(*[col for col in zip(*data) if any(cell.strip() for cell in col)])))
    data = [row for row in data if any(cell.strip() for cell in row)]
    header = [
        col if col.strip() != '' else f'Coluna_{i}' for i, col in enumerate(data[0])]
    df = pd.DataFrame(data[1:], columns=header)

    # Remove possíveis colunas de índice
    if 'index' in df.columns:
        df = df.drop(columns=['index'])

    # Converter colunas numéricas (remover R$, milhar, vírgulas etc.)
    colunas_numericas = ['VALOR NF', 'PESO']
    for col in colunas_numericas:
        if col in df.columns:
            df[col] = df[col].astype(str) \
                .str.replace(r'[^\d,.-]', '', regex=True) \
                .str.replace('.', '', regex=False) \
                .str.replace(',', '.', regex=False)
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Converter datas
    if 'DATA' in df.columns:
        df['DATA'] = pd.to_datetime(df['DATA'], dayfirst=True, errors='coerce')

    return df, header


df, header = carregar_dados()

st.markdown(
    """
    <div style='display: flex; align-items: center; gap: 10px; font-size: 30px; font-weight: bold;'>
        <span style='color: green;'>Controladoria</span> - Informações sobre o <span style='color: blue;'>Lançamentos Setranding</span>
        <img width="40" height="40" src="https://img.icons8.com/officel/80/cargo-ship.png"/>
    </div>
    <hr style='border-top: 1px solid blue; margin-top: 4px;' />
    """,
    unsafe_allow_html=True
)

# Filtros
coluna_esquerda, coluna_direita, coluna_meio = st.columns([1, 0.8, 0.5])

filtro_mes = coluna_esquerda.multiselect(
    label=":green-background[**Mês**]",
    options=df['DATA'].dt.month_name().unique(),
)

filtro_tabela_preco = coluna_direita.multiselect(
    label=":blue-background[**STATUS**]",
    options=df['STATUS'].unique(),
)

filtro_ano = coluna_meio.multiselect(
    label=":red-background[**IMO**]",
    options=df['IMO'].unique(),
)

# Aplicar filtros
df_filtrado = df.copy()

if filtro_mes:
    df_filtrado = df_filtrado[df_filtrado['DATA'].dt.month_name().isin(
        filtro_mes)]

if filtro_tabela_preco:
    df_filtrado = df_filtrado[df_filtrado['STATUS'].isin(filtro_tabela_preco)]

if filtro_ano:
    df_filtrado = df_filtrado[df_filtrado['IMO'].isin(filtro_ano)]

# Métricas
col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

with col1:
    if 'VALOR NF' in df_filtrado.columns:
        total_valor = df_filtrado['VALOR NF'].sum()
        st.metric(
            label=":blue-background[**Total de Valor Transportado**]",
            value=format_number(total_valor),
            delta="Reais"
        )

with col2:
    st.metric(
        label=":orange-background[**Quantidade de Notas**]",
        value=f"{df_filtrado.shape[0]}",
        delta="Quantidade de Notas"
    )

with col3:
    if 'PESO' in df_filtrado.columns:
        total_peso = df_filtrado['PESO'].sum()
        st.metric(
            ":blue-background[**Peso Total (Geral)**]",
            format_number(total_peso, ''),
            "kg"
        )

# Formata colunas manualmente com separador brasileiro (como texto)
df_filtrado["PESO"] = df_filtrado["PESO"].apply(
    lambda x: f"{x:,.0f} kg".replace(
        ",", "X").replace(".", ",").replace("X", ".")
)

df_filtrado["VALOR NF"] = df_filtrado["VALOR NF"].apply(
    lambda x: f"R$ {x:,.0f}".replace(
        ",", "X").replace(".", ",").replace("X", ".")
)


# Exibição da Tabela Final com formatação de colunas
st.dataframe(
    df_filtrado.reset_index(drop=True),
    use_container_width=True,
    hide_index=True,
    column_config={
        "DATA": st.column_config.DateColumn("DATA", format="DD.MM.YYYY"),
    }
)


def status_com_emoji(status):
    status = status.upper()
    if status == "CONCLUÍDO":
        return "✅ CONCLUÍDO"
    elif status == "AGUARDANDO":
        return "🕒 AGUARDANDO"
    elif status == "CANCELADO":
        return "❌ CANCELADO"
    else:
        return status


df_filtrado["STATUS_EMOJI"] = df_filtrado["STATUS"].apply(status_com_emoji)

st.data_editor(
    df_filtrado,
    use_container_width=True,
    column_config={
        "STATUS_EMOJI": st.column_config.TextColumn("STATUS"),
        "DATA": st.column_config.DateColumn("DATA", format="DD.MM.YYYY"),
        "VALOR NF": st.column_config.TextColumn("VALOR NF"),
        "PESO": st.column_config.TextColumn("PESO"),

    },
    key="tabela_lancamentos",
)

# ______________________________________


# Configuração da página
st.set_page_config(
    page_title="Exportação (Sertranding)",
    page_icon="imagens/cotralti_logo.png",
    layout="wide",
)


def format_number(value, prefix='R$'):
    if pd.isna(value):
        return f"{prefix} 0,00"
    for unit in ['', ' mil']:
        if value < 1000:
            return f"{prefix} {value:,.2f}{unit}".replace(",", "X").replace(".", ",").replace("X", ".")
        value /= 1000
    return f"{prefix} {value:,.2f} milhões".replace(",", "X").replace(".", ",").replace("X", ".")


@st.cache_resource
def conectar_planilha():
    credenciais = pygsheets.authorize(
        service_file=os.path.join(os.getcwd(), 'cred.json'))
    url = "https://docs.google.com/spreadsheets/d/1l7G_4VAQGyN9cfmpsS-_bnjfzSqXRJViZMCZ8z6vXSc/edit#gid=0"
    arquivo = credenciais.open_by_url(url)
    aba = arquivo.worksheet_by_title("Sertranding")
    return aba


aba = conectar_planilha()


@st.cache_data(show_spinner=False)
def carregar_dados():
    data = aba.get_all_values()
    data = list(
        map(list, zip(*[col for col in zip(*data) if any(cell.strip() for cell in col)])))
    data = [row for row in data if any(cell.strip() for cell in row)]
    header = [
        col if col.strip() != '' else f'Coluna_{i}' for i, col in enumerate(data[0])]
    df = pd.DataFrame(data[1:], columns=header)

    # Converter colunas numéricas
    colunas_numericas = ['VALOR NF', 'PESO']
    for col in colunas_numericas:
        if col in df.columns:
            df[col] = df[col].astype(str) \
                .str.replace(r'[^\d,.-]', '', regex=True) \
                .str.replace('.', '', regex=False) \
                .str.replace(',', '.', regex=False)
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Converter datas
    if 'DATA' in df.columns:
        df['DATA'] = pd.to_datetime(df['DATA'], dayfirst=True, errors='coerce')

    return df, header


df, header = carregar_dados()

# Filtros
coluna_esquerda, coluna_direita, coluna_meio = st.columns([1, 0.8, 0.5])

filtro_mes = coluna_esquerda.multiselect(
    label=":green-background[**Mês**]",
    options=df['DATA'].dt.month_name().dropna().unique(),
)

filtro_status = coluna_direita.multiselect(
    label=":blue-background[**STATUS**]",
    options=df['STATUS'].dropna().unique(),
)

filtro_ano = coluna_meio.multiselect(
    label=":red-background[**IMO**]",
    options=df['IMO'].dropna().unique(),
)

# Aplica filtros
df_filtrado = df.copy()

if filtro_mes:
    df_filtrado = df_filtrado[df_filtrado['DATA'].dt.month_name().isin(
        filtro_mes)]

if filtro_status:
    df_filtrado = df_filtrado[df_filtrado['STATUS'].isin(filtro_status)]

if filtro_ano:
    df_filtrado = df_filtrado[df_filtrado['IMO'].isin(filtro_ano)]

# Métricas
col1, col2, col3 = st.columns(3)

col1.metric(
    label=":blue-background[Total de Valor Transportado]",
    value=format_number(df_filtrado['VALOR NF'].sum(), "R$")
)

col2.metric(
    label=":orange-background[Quantidade de Notas]",
    value=f"{df_filtrado.shape[0]}"
)

col3.metric(
    label=":blue-background[Peso Total (Geral)]",
    value=format_number(df_filtrado['PESO'].sum(), "kg")
)

# Formata colunas como texto com separador brasileiro
df_filtrado["PESO"] = df_filtrado["PESO"].apply(
    lambda x: f"{x:,.0f} kg".replace(
        ",", "X").replace(".", ",").replace("X", ".")
)

df_filtrado["VALOR NF"] = df_filtrado["VALOR NF"].apply(
    lambda x: f"R$ {x:,.2f}".replace(
        ",", "X").replace(".", ",").replace("X", ".")
)

# Função para status com emoji


def status_com_emoji(status):
    status = str(status).upper()
    if status == "CONCLUÍDO":
        return "✅ CONCLUÍDO"
    elif status == "AGUARDANDO":
        return "🕒 AGUARDANDO"
    elif status == "CANCELADO":
        return "❌ CANCELADO"
    else:
        return status


df_filtrado["STATUS_EMOJI"] = df_filtrado["STATUS"].apply(status_com_emoji)

# Exibe tabela com status + emojis, formato texto e sem índice
st.dataframe(
    df_filtrado.reset_index(drop=True)[
        # ajuste colunas conforme necessidade
        ['DATA', 'STATUS_EMOJI', 'VALOR NF', 'PESO', 'IMO']
    ],
    use_container_width=True,
    hide_index=True,
    column_config={
        "DATA": st.column_config.DateColumn("DATA", format="DD.MM.YYYY"),
        "STATUS_EMOJI": st.column_config.TextColumn("STATUS"),
        "VALOR NF": st.column_config.TextColumn("VALOR NF"),
        "PESO": st.column_config.TextColumn("PESO"),
        "IMO": st.column_config.TextColumn("IMO"),
    }
)
