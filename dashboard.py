import streamlit as st
import pandas as pd
import requests
import time
import plotly.express as px  # <--- NOVA IMPORTAÇÃO NECESSÁRIA

# --- CONFIGURAÇÕES ---
# IMPORTANTE: Troque pelo ID do SEU canal no ThingSpeak (somente números)
CHANNEL_ID = "SEU_CHANNEL_ID_AQUI" 

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
    # <--- ALTERADO AQUI: Mudamos de 100 para 8000 para pegar todo o histórico
    url = f"https://api.thingspeak.com/channels/{CHANNEL_ID}/feeds.json?results=8000"
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

    # Verifica se os dados são válidos
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

            # --- GRÁFICO (PLOTLY) ---
            st.subheader("Histórico Completo")
            
            # Cria DataFrame para o gráfico
            df = pd.DataFrame(feeds)
            
            # Converte a coluna de data para o formato correto (Timezone Brasil)
            df['created_at'] = pd.to_datetime(df['created_at'])
            # Ajuste opcional de fuso horário (-3h se o servidor estiver em UTC)
            # df['created_at'] = df['created_at'] - pd.Timedelta(hours=3)

            # Converte a coluna de valor para número
            df['field1'] = pd.to_numeric(df['field1'])
            
            # Renomeia para ficar bonito no gráfico
            df = df.rename(columns={'created_at': 'Hora', 'field1': 'Umidade (%)'})
            
            # Plota o gráfico INTERATIVO com Plotly
            fig = px.line(df, x='Hora', y='Umidade (%)')
            
            # <--- CORREÇÃO APLICADA AQUI: width="stretch"
            st.plotly_chart(fig, width="stretch")
            
            st.caption(f"Última atualização: {last_entry['created_at']}")
            
        else:
            st.warning("Recebendo dados vazios. Verifique o sensor.")
    else:
        st.info("Aguardando conexão com o ThingSpeak ou dados insuficientes...")

# Rodapé
st.markdown("---")
st.caption("Atualize a página para ver novos dados.")
