import pandas as pd
import pygsheets
import os
import streamlit as st
import datetime


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

# Título com ícone
st.markdown(
    """
    <div style='display: flex; align-items: center; gap: 10px; font-size: 30px; font-weight: bold;'>
        <span style='color: green;'>Controladoria</span>  <span style='color: blue;'>Sertranding</span>
        <img width="40" height="40" src="https://img.icons8.com/officel/80/cargo-ship.png"/>
    </div>
    <hr style='border-top: 1px solid blue; margin-top: 4px;' />
    """,
    unsafe_allow_html=True
)


# Filtros
coluna_esquerda, coluna_direita, coluna_meio, coluna_final = st.columns([
                                                                        1, 0.8, 0.5, 1])

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

filtro_carga = coluna_final.multiselect(
    label=":orange-background[**Tipo de Carga**]",
    options=df['TIPO DE CARGA'].dropna().unique(),
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
if filtro_carga:
    df_filtrado = df_filtrado[df_filtrado['TIPO DE CARGA'].isin(filtro_carga)]

# Métricas principais
col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    label=":blue-background[**Total de Valor Transportado**]",
    value=format_number(df_filtrado['VALOR NF'].sum(), "R$")
)

col2.metric(
    label=":orange-background[**Nota Fiscal**]",
    value=f"{df_filtrado.shape[0]}"
)

col3.metric(
    label=":blue-background[**Peso Total (Geral)**]",
    value=format_number(df_filtrado['PESO'].sum(), "kg")
)

total_aguardando = df_filtrado[df_filtrado['STATUS'].str.upper(
) == 'AGUARDANDO'].shape[0]
total_concluido = df_filtrado[df_filtrado['STATUS'].str.upper(
) == 'CONCLUÍDO'].shape[0]

col4.metric(
    label="🟡 :orange-background[**Processos Aguardando**]",
    value=f"{total_aguardando}"
)

col5.metric(
    label="✅ :green-background[**Processos Concluídos**]",
    value=f"{total_concluido}"
)

# Formata colunas numéricas como texto
df_filtrado["PESO"] = df_filtrado["PESO"].apply(
    lambda x: f"{x:,.0f} kg".replace(
        ",", "X").replace(".", ",").replace("X", ".")
)
df_filtrado["VALOR NF"] = df_filtrado["VALOR NF"].apply(
    lambda x: f"R$ {x:,.2f}".replace(
        ",", "X").replace(".", ",").replace("X", ".")
)

# Emojis


def status_com_emoji(status):
    status = str(status).upper()
    if status == "CONCLUÍDO":
        return "✅ 𝗖𝗢𝗡𝗖𝗟𝗨𝗜́𝗗𝗢"
    elif status == "AGUARDANDO":
        return "🟡 𝗔𝗚𝗨𝗔𝗥𝗗𝗔𝗡𝗗𝗢"
    elif status == "CANCELADO":
        return "❌ 𝗖𝗔𝗡𝗖𝗘𝗟𝗔𝗗𝗢"
    else:
        return status


def status_IMO(imo):
    status = str(imo).upper()
    if imo == "SIM":
        return "☣️ SIM"
    elif imo == "NÃO":
        return "🟢 NÃO"


df_filtrado["STATUS_EMOJI"] = df_filtrado["STATUS"].apply(status_com_emoji)
df_filtrado["IMO_EMOGI"] = df_filtrado["IMO"].apply(status_IMO)

# Painel de alertas - Processos Aguardando
hoje = pd.Timestamp(datetime.datetime.now().date())

if 'DATA' in df_filtrado.columns and 'STATUS' in df_filtrado.columns:
    df_alertas = df_filtrado[df_filtrado['STATUS'].str.upper(
    ) == 'AGUARDANDO'].copy()
    df_alertas['DIAS_RESTANTES'] = (df_alertas['DATA'] - hoje).dt.days

    with st.expander("📌:orange-background[**Processos Pendentes**]", expanded=False):
        if df_alertas.empty:
            st.success("✅ Nenhum processo com status 'AGUARDANDO'.")
        else:
            df_alertas = df_alertas.sort_values('DIAS_RESTANTES')
            for _, row in df_alertas.iterrows():
                dias = row['DIAS_RESTANTES']
                data_str = row['DATA'].strftime(
                    '%d/%m/%Y') if pd.notna(row['DATA']) else "sem data"
                processo = row.get('PROCESSO', '---')

                if dias < 0:
                    st.error(
                        f"❌ Processo `{processo}` — Data {data_str} já passou há {-dias} dias.")
                elif dias == 0:
                    st.warning(
                        f"⚠️ Processo `{processo}` — Data é hoje! ({data_str})")
                else:
                    st.info(
                        f"📅 Processo `{processo}` — Faltam {dias} dias até {data_str}.")

# Exibe tabela formatada
st.dataframe(
    df_filtrado.reset_index(drop=True)[
        ['STATUS_EMOJI', 'DATA', 'Nº DI', 'PROCESSO', 'PO', 'TERMINAL', 'TIPO DE CARGA',
         'Nº CONTAINER', 'PRODUTO', 'QTD[VOLUME]', 'MOTORISTA', 'PESO', 'IMO_EMOGI',
         'DAST', 'NOTA FISCAL', 'VALOR NF']
    ],
    use_container_width=True,
    hide_index=True,
    column_config={
        "STATUS_EMOJI": st.column_config.TextColumn("𝗦𝗧𝗔𝗧𝗨𝗦"),
        "DATA": st.column_config.DateColumn("DATA", format="DD.MM.YYYY"),
        "VALOR NF": st.column_config.TextColumn("VALOR NF"),
        "PESO": st.column_config.TextColumn("PESO"),
        "IMO_EMOGI": st.column_config.TextColumn("IMO"),
    }
)
