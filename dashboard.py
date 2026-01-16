import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime, timedelta

# --- CONFIGURAÇÕES ---
CHANNEL_ID = "3204291" # <--- CONFIRA SEU ID AQUI

st.set_page_config(
    page_title="Monitor de Jardim",
    page_icon="🌱",
    layout="centered"
)

st.title("🌱 Monitoramento de Umidade")
st.markdown("---")

# --- BARRA LATERAL (CONTROLES) ---
st.sidebar.header("Configurações")

if st.sidebar.button('🔄 Atualizar Dados'):
    st.rerun()

st.sidebar.markdown("---")

# SELETOR DE DATA
data_padrao = datetime.now() - timedelta(days=7)

data_selecionada = st.sidebar.date_input(
    "Visualizar dados a partir de:",
    value=data_padrao,
    format="DD/MM/YYYY"
)

# --- FUNÇÃO DE DADOS ---
def get_data():
    url = f"https://api.thingspeak.com/channels/{CHANNEL_ID}/feeds.json?results=8000"
    try:
        response = requests.get(url)
        data = response.json()
        return data
    except:
        return None

# --- PROCESSAMENTO PRINCIPAL ---
placeholder = st.empty()

with placeholder.container():
    dados_json = get_data()

    if isinstance(dados_json, dict) and 'feeds' in dados_json and len(dados_json['feeds']) > 0:
        feeds = dados_json['feeds']
        df = pd.DataFrame(feeds)
        
        # --- TRATAMENTO DE DATA ---
        df['created_at'] = pd.to_datetime(df['created_at'])
        # Ajuste de Fuso Horário (-3h para Brasil)
        df['created_at'] = df['created_at'] - pd.Timedelta(hours=3)
        
        # --- APLICAÇÃO DO FILTRO (CORRIGIDO) ---
        # Aqui usamos .dt.date para pegar apenas a parte do "Dia" da coluna de data e hora
        df_filtrado = df[df['created_at'].dt.date >= data_selecionada]
        
        # --- EXIBIÇÃO ---
        if not df_filtrado.empty:
            df_filtrado['field1'] = pd.to_numeric(df_filtrado['field1'])
            
            # Pega a última leitura
            ultima_leitura = df_filtrado.iloc[-1]
            umidade_atual = float(ultima_leitura['field1'])
            hora_atual = ultima_leitura['created_at']
            
            # Métricas
            col1, col2 = st.columns(2)
            with col1:
                st.metric(label="Umidade Atual", value=f"{umidade_atual}%")
            with col2:
                if umidade_atual < 30:
                    st.error("⚠️ Solo Seco! Regar.")
                elif umidade_atual > 80:
                    st.info("💧 Solo Encharcado.")
                else:
                    st.success("✅ Umidade Ideal.")

            # Gráfico
            st.subheader(f"Histórico")
            st.caption(f"Mostrando dados desde {data_selecionada.strftime('%d/%m/%Y')}")
            
            df_grafico = df_filtrado.rename(columns={'created_at': 'Hora', 'field1': 'Umidade (%)'})
            fig = px.line(df_grafico, x='Hora', y='Umidade (%)')
            st.plotly_chart(fig, width="stretch")
            
            st.caption(f"Última leitura: {hora_atual.strftime('%d/%m/%Y %H:%M')}")
            
        else:
            st.warning(f"Não foram encontrados dados a partir de {data_selecionada.strftime('%d/%m/%Y')}.")
            st.info("Tente selecionar uma data anterior no menu ao lado.")

    else:
        st.info("Aguardando conexão com o ThingSpeak...")

st.markdown("---")
