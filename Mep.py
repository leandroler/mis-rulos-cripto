import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Cotizaciones en Vivo", page_icon="📈", layout="centered")

# --- FUNCIONES DE CONEXIÓN ---
def obtener_usdt():
    try:
        url = "https://criptoya.com/api/usdt/ars/100000"
        return requests.get(url, timeout=5).json()
    except:
        return {}

def obtener_bancos():
    try:
        url = "https://dolarapi.com/v1/cotizaciones/bancos"
        return requests.get(url, timeout=5).json()
    except:
        return []

# --- INTERFAZ ---
st.title("📈 Monitor de Cotizaciones")
st.write(f"Actualizado: **{datetime.now().strftime('%H:%M:%S')}**")

if st.button("🔄 Actualizar Precios", type="primary"):
    # Limpiamos la caché visual
    st.empty()

# Creamos las dos solapas
tab1, tab2 = st.tabs(["🪙 USDT (Exchanges)", "🏦 Dólar Oficial (Bancos)"])

# --- SOLAPA 1: USDT ---
with tab1:
    st.subheader("Cotización USDT / ARS")
    st.caption("Lo que te cuesta comprar (Ask) | Lo que te pagan al vender (Bid)")
    
    datos_usdt = obtener_usdt()
    
    if datos_usdt:
        exchanges_lista = []
        # Seleccionamos las plataformas más conocidas
        plataformas = ['binancep2p', 'bitgetp2p', 'kucoinp2p', 'fiwind', 'lemoncash', 'belo', 'buenbit', 'letsbit']
        
        for ex in plataformas:
            if ex in datos_usdt and datos_usdt[ex]['ask'] > 0:
                exchanges_lista.append({
                    "Plataforma": ex.replace('p2p', ' P2P').capitalize(),
                    "Precio de Compra": datos_usdt[ex]['ask'],
                    "Precio de Venta": datos_usdt[ex]['bid']
                })
        
        if exchanges_lista:
            df_usdt = pd.DataFrame(exchanges_lista)
            # Ordenamos por el mejor precio de compra (el más barato primero)
            df_usdt = df_usdt.sort_values(by="Precio de Compra", ascending=True)
            
            st.dataframe(
                df_usdt.style.format({
                    "Precio de Compra": "${:,.2f}",
                    "Precio de Venta": "${:,.2f}"
                }),
                use_container_width=True,
                hide_index=True
            )
    else:
        st.error("No se pudieron cargar los datos de CriptoYa.")

# --- SOLAPA 2: BANCOS ---
with tab2:
    st.subheader("Dólar Oficial Básico")
    st.info("⚠️ **Atención:** Los precios de 'Compra para vos' (Venta del banco) mostrados aquí son el valor **SIN IMPUESTOS**. Al momento de comprar en tu homebanking, el Estado le suma los impuestos correspondientes (Dólar Tarjeta/Solidario).")
    
    datos_bancos = obtener_bancos()
    
    if datos_bancos:
        bancos_lista = []
        # Filtramos algunos bancos principales y Brubank
        bancos_buscados = ['Galicia', 'Brubank', 'Santander', 'BBVA', 'Macro', 'Supervielle', 'Ciudad', 'Nacion']
        
        for banco in datos_bancos:
            # DolarAPI trae el nombre en el campo 'casa'
            nombre_banco = banco.get('casa', '')
            if nombre_banco in bancos_buscados:
                bancos_lista.append({
                    "Entidad": nombre_banco,
                    "El Banco te Compra a": banco.get('compra', 0),
                    "El Banco te Vende a": banco.get('venta', 0)
                })
        
        if bancos_lista:
            df_bancos = pd.DataFrame(bancos_lista)
            # Ordenamos alfabéticamente
            df_bancos = df_bancos.sort_values(by="Entidad")
            
            st.dataframe(
                df_bancos.style.format({
                    "El Banco te Compra a": "${:,.2f}",
                    "El Banco te Vende a": "${:,.2f}"
                }),
                use_container_width=True,
                hide_index=True
            )
    else:
        st.error("No se pudieron cargar los datos de DolarAPI.")
            
