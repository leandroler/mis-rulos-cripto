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

def obtener_mep():
    try:
        url = "https://dolarapi.com/v1/dolares/mep"
        return requests.get(url, timeout=5).json()
    except:
        return {}

# --- INTERFAZ ---
st.title("📈 Monitor de Cotizaciones")
st.write(f"Actualizado: **{datetime.now().strftime('%H:%M:%S')}**")

if st.button("🔄 Actualizar Precios", type="primary"):
    st.empty()

# Creamos las dos solapas
tab1, tab2 = st.tabs(["🪙 USDT (Exchanges)", "🏦 Bancos y Billeteras"])

# --- SOLAPA 1: USDT ---
with tab1:
    st.subheader("Cotización USDT / ARS")
    
    datos_usdt = obtener_usdt()
    
    if datos_usdt:
        exchanges_lista = []
        plataformas = ['binancep2p', 'bitgetp2p', 'kucoinp2p', 'fiwind', 'lemoncash', 'belo', 'buenbit', 'letsbit']
        
        for ex in plataformas:
            if ex in datos_usdt and datos_usdt[ex]['ask'] > 0:
                exchanges_lista.append({
                    "Plataforma": ex.replace('p2p', ' P2P').capitalize(),
                    "Vos Comprás a": datos_usdt[ex]['ask'],
                    "Vos Vendés a": datos_usdt[ex]['bid']
                })
        
        if exchanges_lista:
            df_usdt = pd.DataFrame(exchanges_lista).sort_values(by="Vos Comprás a", ascending=True)
            
            st.dataframe(
                df_usdt.style.format({
                    "Vos Comprás a": "${:,.2f}",
                    "Vos Vendés a": "${:,.2f}"
                }),
                use_container_width=True,
                hide_index=True
            )
    else:
        st.error("No se pudieron cargar los datos de CriptoYa.")

# --- SOLAPA 2: BANCOS Y BILLETERAS ---
with tab2:
    st.subheader("Dólar: Bancos vs Fintech")
    st.caption("Los valores de Mercado Pago y Naranja X corresponden a la cotización del Dólar MEP.")
    
    datos_bancos = obtener_bancos()
    datos_mep = obtener_mep()
    
    entidades_lista = []
    
    # 1. Cargamos los Bancos (Dólar Oficial de cada entidad)
    if datos_bancos:
        bancos_buscados = ['galicia', 'brubank', 'santander', 'bbva', 'macro', 'nacion']
        for banco in datos_bancos:
            casa = banco.get('casa', '').lower()
            if casa in bancos_buscados:
                entidades_lista.append({
                    "Entidad": banco.get('nombre', casa.capitalize()),
                    "Tipo": "Oficial del Banco",
                    # Para el banco, su "venta" es lo que VOS pagás al comprar.
                    "Vos Comprás a": banco.get('venta', 0),
                    # Para el banco, su "compra" es lo que VOS recibís al vender.
                    "Vos Vendés a": banco.get('compra', 0) 
                })
                
    # 2. Cargamos las Billeteras Virtuales (Usan Dólar MEP)
    if datos_mep:
        precio_compra_mep = datos_mep.get('venta', 0)
        precio_venta_mep = datos_mep.get('compra', 0)
        
        entidades_lista.append({
            "Entidad": "Mercado Pago",
            "Tipo": "Dólar MEP",
            "Vos Comprás a": precio_compra_mep,
            "Vos Vendés a": precio_venta_mep
        })
        entidades_lista.append({
            "Entidad": "Naranja X",
            "Tipo": "Dólar MEP",
            "Vos Comprás a": precio_compra_mep,
            "Vos Vendés a": precio_venta_mep
        })
        
    if entidades_lista:
        df_entidades = pd.DataFrame(entidades_lista)
        # Ordenamos la tabla alfabéticamente por Entidad
        df_entidades = df_entidades.sort_values(by="Entidad")
        
        st.dataframe(
            df_entidades.style.format({
                "Vos Comprás a": "${:,.2f}",
                "Vos Vendés a": "${:,.2f}"
            }),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.error("No se pudieron cargar los datos de los Bancos ni de las Billeteras.")
