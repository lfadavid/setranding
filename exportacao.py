import streamlit as st
import pandas as pd
import pygsheets
import datetime
import os


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


def carregar_dados():
    aba = conectar_planilha()
    data = aba.get_all_values()

    data = list(
        map(list, zip(*[col for col in zip(*data) if any(cell.strip() for cell in col)])))
    data = [row for row in data if any(cell.strip() for cell in row)]
    header = [
        col if col.strip() != '' else f'Coluna_{i}' for i, col in enumerate(data[0])]
    df = pd.DataFrame(data[1:], columns=header)

    colunas_numericas = ['VALOR NF', 'PESO']
    for col in colunas_numericas:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(r'[^\d,.-]', '', regex=True)\
                .str.replace('.', '', regex=False)\
                .str.replace(',', '.', regex=False)
            df[col] = pd.to_numeric(df[col], errors='coerce')

    if 'DATA' in df.columns:
        df['DATA'] = pd.to_datetime(df['DATA'], dayfirst=True, errors='coerce')

    return df


st.markdown("""
<div style='display: flex; align-items: center; gap: 10px; font-size: 30px; font-weight: bold;'>
    <span style='color: green;'>Controladoria</span> <span style='color: blue;'>Sertranding</span>
    <img width="40" height="40" src="https://img.icons8.com/officel/80/cargo-ship.png"/>
</div>
<hr style='border-top: 1px solid blue; margin-top: 4px;' />
""", unsafe_allow_html=True)

df = carregar_dados()

# Filtros
col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

filtro_mes = col1.multiselect(
    "📅 Mês", options=df['DATA'].dt.month_name().dropna().unique())
filtro_status = col2.multiselect(
    "📌 Status", options=df['STATUS'].dropna().unique())
filtro_imo = col3.multiselect("☣️ IMO", options=df['IMO'].dropna().unique())
filtro_carga = col4.multiselect(
    "🚛 Tipo de Carga", options=df['TIPO DE CARGA'].dropna().unique())

# Aplicar filtros
df_filtrado = df.copy()
if filtro_mes:
    df_filtrado = df_filtrado[df_filtrado['DATA'].dt.month_name().isin(
        filtro_mes)]
if filtro_status:
    df_filtrado = df_filtrado[df_filtrado['STATUS'].isin(filtro_status)]
if filtro_imo:
    df_filtrado = df_filtrado[df_filtrado['IMO'].isin(filtro_imo)]
if filtro_carga:
    df_filtrado = df_filtrado[df_filtrado['TIPO DE CARGA'].isin(filtro_carga)]

# Métricas
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("💰 Total Transportado", format_number(df_filtrado['VALOR NF'].sum()))
m2.metric("📄 NFs Emitidas", f"{df_filtrado.shape[0]}")
m3.metric("⚖️ Peso Total", format_number(df_filtrado['PESO'].sum(), "kg"))

aguardando = df_filtrado[df_filtrado['STATUS'].str.upper()
                         == 'AGUARDANDO'].shape[0]
concluido = df_filtrado[df_filtrado['STATUS'].str.upper()
                        == 'CONCLUÍDO'].shape[0]
m4.metric("🟡 Aguardando", aguardando)
m5.metric("✅ Concluídos", concluido)

# Emojis e formatações


def status_com_emoji(s):
    s = str(s).upper()
    if s == "CONCLUÍDO":
        return "✅ CONCLUÍDO"
    if s == "AGUARDANDO":
        return "🟡 AGUARDANDO"
    if s == "CANCELADO":
        return "❌ CANCELADO"
    return s


def status_imo(s):
    if s == "SIM":
        return "☣️ SIM"
    if s == "NÃO":
        return "🟢 NÃO"
    return s


df_filtrado["STATUS_EMOJI"] = df_filtrado["STATUS"].apply(status_com_emoji)
df_filtrado["IMO_EMOJI"] = df_filtrado["IMO"].apply(status_imo)

# Painel de alertas
hoje = pd.Timestamp(datetime.datetime.now().date())
if 'DATA' in df_filtrado.columns and 'STATUS' in df_filtrado.columns:
    pendentes = df_filtrado[df_filtrado['STATUS'].str.upper()
                            == 'AGUARDANDO'].copy()
    pendentes['DIAS_RESTANTES'] = (pendentes['DATA'] - hoje).dt.days

    with st.expander("📌 Processos Pendentes", expanded=False):
        if pendentes.empty:
            st.success("✅ Nenhum processo com status 'AGUARDANDO'.")
        else:
            pendentes = pendentes.sort_values('DIAS_RESTANTES')
            for _, row in pendentes.iterrows():
                dias = row['DIAS_RESTANTES']
                data_str = row['DATA'].strftime(
                    '%d/%m/%Y') if pd.notna(row['DATA']) else "sem data"
                processo = row.get('PROCESSO', '---')
                if dias < 0:
                    st.error(
                        f"❌ Processo `{processo}` — vencido há {-dias} dias ({data_str})")
                elif dias == 0:
                    st.warning(
                        f"⚠️ Processo `{processo}` — vence hoje ({data_str})")
                else:
                    st.info(
                        f"📅 Processo `{processo}` — faltam {dias} dias ({data_str})")

# Formatar valores
df_filtrado["PESO"] = df_filtrado["PESO"].apply(
    lambda x: f"{x:,.0f} kg".replace(",", "X").replace(".", ",").replace("X", "."))
df_filtrado["VALOR NF"] = df_filtrado["VALOR NF"].apply(
    lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

# Exibir a tabela
st.dataframe(
    df_filtrado.reset_index(drop=True)[
        ['STATUS_EMOJI', 'DATA', 'Nº DI', 'PROCESSO', 'PO', 'TERMINAL',
         'TIPO DE CARGA', 'Nº CONTAINER', 'PRODUTO', 'QTD[VOLUME]', 'MOTORISTA',
         'PESO', 'IMO_EMOJI', 'DAST', 'NOTA FISCAL', 'VALOR NF']
    ],
    use_container_width=True,
    column_config={
        "STATUS_EMOJI": st.column_config.TextColumn("STATUS"),
        "IMO_EMOJI": st.column_config.TextColumn("IMO"),
        "DATA": st.column_config.DateColumn("DATA", format="DD/MM/YYYY"),
        "VALOR NF": st.column_config.TextColumn("VALOR NF"),
        "PESO": st.column_config.TextColumn("PESO"),
    }
)
