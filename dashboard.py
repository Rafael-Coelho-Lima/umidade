import streamlit as st
import pandas as pd
import requests
import time

# --- CONFIGURAÇÕES ---
# IMPORTANTE: Troque pelo ID do SEU canal no ThingSpeak (é apenas o número)
CHANNEL_ID = "3204291"  # Exemplo: "2394812"

st.set_page_config(
    page_title="Monitor de Jardim",
    page_icon="🌱",
    layout="centered"
)

# Título e Cabeçalho
st.title("🌱 Monitoramento de Umidade")
st.markdown("---")

# Função para buscar dados no ThingSpeak
def get_data():
    # Busca os últimos 100 resultados
    url = f"https://api.thingspeak.com/channels/{CHANNEL_ID}/feeds.json?results=100"
    try:
        response = requests.get(url)
        data = response.json()
        return data
    except:
        return None

# Botão de atualização manual na barra lateral
if st.sidebar.button('🔄 Atualizar Agora'):
    st.rerun()

# Espaço reservado para os dados
placeholder = st.empty()

# Container principal
with placeholder.container():
    dados_json = get_data()

    # Verifica se dados_json é realmente um dicionário (e não um código de erro -1)
    if isinstance(dados_json, dict) and 'feeds' in dados_json and len(dados_json['feeds']) > 0:
        feeds = dados_json['feeds']
        last_entry = feeds[-1]
        
        # Processa o valor atual
        raw_value = last_entry['field1']
        
        # Verifica se o valor não é nulo
        if raw_value:
            umidade_atual = float(raw_value)
            
            # --- MÉTRICAS ---
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric(label="Umidade do Solo", value=f"{umidade_atual}%")
            
            with col2:
                # Lógica de Status (Ajuste seus limiares aqui)
                if umidade_atual < 30:
                    st.error("⚠️ Solo Seco! Regar.")
                elif umidade_atual > 80:
                    st.info("💧 Solo Encharcado.")
                else:
                    st.success("✅ Umidade Ideal.")

            # --- GRÁFICO ---
            st.subheader("Histórico (Últimas Leituras)")
            
            # Cria DataFrame para o gráfico
            df = pd.DataFrame(feeds)
            # Converte a coluna de data para o formato correto
            df['created_at'] = pd.to_datetime(df['created_at'])
            # Converte a coluna de valor para número
            df['field1'] = pd.to_numeric(df['field1'])
            
            # Renomeia para ficar bonito no gráfico
            df = df.rename(columns={'created_at': 'Hora', 'field1': 'Umidade (%)'})
            
            # Plota o gráfico de linha
            st.line_chart(df, x='Hora', y='Umidade (%)')
            
            st.caption(f"Última atualização: {last_entry['created_at']}")
            
        else:
            st.warning("Recebendo dados vazios. Verifique o sensor.")
    else:
        st.info("Aguardando conexão com o ThingSpeak...")

# Rodapé
st.markdown("---")

st.caption("Atualize a página para ver novos dados.")
