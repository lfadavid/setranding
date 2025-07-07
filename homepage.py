import streamlit as st

st.markdown(
    """
    <style>
        [data-testid=stSidebar] [data-testid=stImage]{
            text-align: center;
            display: block;
            margin-left: auto;
            margin-right: auto;
            width:50%;
        }
    </style>
    """, unsafe_allow_html=True
)
# containers
# columns

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

coluna_esquerda, coluna_direita = st.columns([1, 1.5])

coluna_esquerda.header("Cotralti :blue[T] & :gray[L] ", divider='green')

coluna_esquerda.write(f"#### Olá, **:red[Usuário]**")  # markdown

st.markdown(
    '𝑨𝒄𝒆𝒔𝒔𝒆 𝒏𝒐𝒔𝒔𝒐 𝒔𝒊𝒕𝒆 𝒑𝒂𝒓𝒂 𝒄𝒐𝒏𝒉𝒆𝒄𝒆𝒓 𝒏𝒐𝒔𝒔𝒐𝒔 𝒔𝒆𝒓𝒗𝒊𝒄̧𝒐𝒔 [𝑪𝒍𝒊𝒒𝒖𝒆 𝒂𝒒𝒖𝒊 𝒑𝒂𝒓𝒂 𝒂𝒄𝒆𝒔𝒔𝒂𝒓 𝒐 𝒔𝒊𝒕𝒆](http://cotralti.com.br)', unsafe_allow_html=True)


container = coluna_direita.container(border=False)
container.image("cotraltiimage.jpg")
st.write("""
         Informações extraídas do sistema de gestão de transporte e logística da Cotralti.
         """)

st.markdown("""
<div style='text-align: center; font-size: 15px; font-weight: bold; font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif; color: #333; padding: 20px 0; margin-top: 40px; background-color: #f8f9fa; border-top: 1px solid #ccc; box-shadow: 0 -2px 5px rgba(0,0,0,0.03);'>
  🛡️ <span style='color:#0056b3;'>Cotralti Transporte e Logistica</span> &copy; 2024. <br>
  All intellectual property rights reserved.
</div>
""", unsafe_allow_html=True)
