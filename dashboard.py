import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime, timedelta

# --- CONFIGURAÇÕES ---
CHANNEL_ID = "3204291" # <--- CONFIRA SEU ID AQUI

st.set_page_config(
    page_title="Monitoramento de Umidade",
    page_icon="🌱",
    layout="wide"
)

st.title("🌱 Monitoramento de Umidade")
st.markdown("---")

# --- BARRA LATERAL (CONTROLES) ---
st.sidebar.header("Painel de Controle")

if st.sidebar.button('🔄 Atualizar Dados'):
    st.rerun()

st.sidebar.markdown("### Filtros")
# Data padrao: ultimos 7 dias
data_padrao = datetime.now() - timedelta(days=7)
data_selecionada = st.sidebar.date_input(
    "Visualizar a partir de:",
    value=data_padrao,
    format="DD/MM/YYYY"
)

# --- BOTÃO DE DOWNLOAD ---
# Só mostra o botão se houver dados carregados
if 'df_filtrado' in locals() and not df_filtrado.empty:
    csv = df_filtrado.to_csv(index=False).encode('utf-8')
    
    st.sidebar.download_button(
        label="📥 Baixar Dados (CSV)",
        data=csv,
        file_name='historico_umidade.csv',
        mime='text/csv',
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
            # Converte TODAS as colunas de fields para numero
            cols_sensores = ['field1', 'field2', 'field3', 'field4', 'field5', 'field6']
            nomes_bonitos = {
                'field1': 'Sensor 1',
                'field2': 'Sensor 2', 
                'field3': 'Sensor 3', 
                'field4': 'Sensor 4', 
                'field5': 'Sensor 5',
                'field6': 'Sensor 6'
            }
            # Converte colunas para numero, ignorando erros
            for col in cols_sensores:
                if col in df_filtrado.columns:
                    df_filtrado[col] = pd.to_numeric(df_filtrado[col], errors='coerce')

            # Pega a ultima leitura
            ultima_leitura = df_filtrado.iloc[-1]
            hora_atual = ultima_leitura['created_at']
            
            # Métricas
            st.subheader("Status Atual")
            cols = st.columns(6) # Cria 6 colunas visuais

            sensores_ativos = [] # Lista para guardar quais sensores tem dados para o grafico
            
            for i, col_name in enumerate(cols_sensores):
                #Verifica se o dado existe (caso o ThinkSpeak retorne null em algum)
                if  col_name in ultima_leitura and not pd.isna(ultima_leitura[col_name]):
                    valor = float(ultima_leitura[col_name])
                    sensores_ativos.append(nomes_bonitos[col_name])
                    
                    with cols[i]:
                        st.metric(label=nomes_bonitos[col_name], value=f"{valor:.0f}%")
                        # Mini logica de cor (opcional)
                        if valor < 30:
                            st.caption("⚠️ Seco")
                        elif valor > 80:
                            st.caption("💧 Encharcado")
                        else:
                            st.caption("✅ Úmido")

            if not sensores_ativos:
                st.warning("Nenhum sensor ativo detectado no momento.")
                
            # --- SECAO DE GRAFICO ---
            st.markdown("---")
            st.subheader(f"Histórico")
            st.caption(f"Exibindo dados desde: {data_selecionada.strftime('%d/%m/%Y')}")
            
            #Renomeie as colunas para o gráfico ficar bonito
            df_grafico = df_filtrado.rename(columns={'created_at': 'Hora', **nomes_bonitos})

            # Cria grafico apenas com os sensores ativos
            if sensores_ativos:
                fig = px.line(df_grafico, x="Hora", y=sensores_ativos)
                st.plotly_chart(fig, width="stretch")

            # --- SECAO DE DOUNLOAD ---            
            st.markdown("### Exportar Dados")
            csv = df_filtrado.to_csv(index=False).encode('utf-8')
            
            st.download_button(
                label="📥 Baixar Planilha (CSV)",
                data=csv,
                file_name=f'umidade_{data_selecionada}.csv',
                mime='text/csv',
            )
            
            st.caption(f"Última leitura: {hora_atual.strftime('%d/%m/%Y %H:%M')}")
            
        else:
            st.warning(f"Não foram encontrados dados a partir de {data_selecionada.strftime('%d/%m/%Y')}.")
            st.info("Tente selecionar uma data anterior no menu lateral.")

    else:
        st.info("Aguardando conexão com o ThingSpeak...(Verifique se o script ponte.py esta rodando)")

st.markdown("---")




