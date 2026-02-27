import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# Configuración de la página para que se vea bien en el celular
st.set_page_config(page_title="Rulos Cripto", page_icon="💸", layout="centered")

def obtener_mep():
    try:
        url = "https://dolarapi.com/v1/dolares/mep"
        return requests.get(url, timeout=5).json()['venta']
    except:
        return None

def obtener_mercado_cripto(moneda, volumen):
    try:
        url = f"https://criptoya.com/api/{moneda}/ars/{volumen}"
        return requests.get(url, timeout=5).json()
    except:
        return {}

def buscar_oportunidades(capital):
    mep = obtener_mep()
    usdt = obtener_mercado_cripto("usdt", capital)
    usdc = obtener_mercado_cripto("usdc", capital)

    estrategias_cripto = []
    estrategias_mep = []
    mercados = {'USDT': usdt, 'USDC': usdc}

    # 1. RULOS PURO PESOS
    for moneda, datos in mercados.items():
        if not datos: continue
        exchanges = list(datos.keys())
        for ex_compra in exchanges:
            for ex_venta in exchanges:
                if ex_compra == ex_venta: continue
                try:
                    compra = datos[ex_compra]['ask']
                    venta = datos[ex_venta]['bid']
                    if compra <= 0 or venta <= 0: continue
                    
                    spread = (venta / compra - 1) * 100
                    if 1.0 <= spread < 20.0: 
                        estrategias_cripto.append({
                            "Moneda": moneda,
                            "Compro": ex_compra.replace('p2p', ' P2P').capitalize(),
                            "Vendo": ex_venta.replace('p2p', ' P2P').capitalize(),
                            "Invierto": f"${compra:,.2f}",
                            "Retiro": f"${venta:,.2f}",
                            "Ganancia": ((capital / compra) * venta) - capital,
                            "Spread (%)": round(spread, 2)
                        })
                except KeyError:
                    pass

    # 2. RULOS DESDE MEP
    if mep:
        for moneda, datos in mercados.items():
            if not datos: continue
            for ex_venta in list(datos.keys()):
                try:
                    venta = datos[ex_venta]['bid']
                    if venta <= 0: continue
                    
                    spread = (venta / mep - 1) * 100
                    if 1.0 <= spread < 20.0:
                        estrategias_mep.append({
                            "Moneda": moneda,
                            "Compro": "MEP Broker",
                            "Vendo": ex_venta.replace('p2p', ' P2P').capitalize(),
                            "Invierto": f"${mep:,.2f}",
                            "Retiro": f"${venta:,.2f}",
                            "Ganancia": ((capital / mep) * venta) - capital,
                            "Spread (%)": round(spread, 2)
                        })
                except KeyError:
                    pass

    return estrategias_cripto, estrategias_mep, mep

# --- INTERFAZ GRÁFICA DE STREAMLIT ---

st.title("📊 Dashboard de Arbitraje")
st.write(f"Última actualización: **{datetime.now().strftime('%H:%M:%S')}**")

# Controles interactivos
capital_usuario = st.number_input("Capital a invertir ($ ARS):", min_value=10000, value=100000, step=10000)

if st.button("🔄 Escanear Mercado Ahora", type="primary"):
    with st.spinner("Buscando las mejores cotizaciones..."):
        cripto, mep_rulo, valor_mep = buscar_oportunidades(capital_usuario)
        
        # Métrica rápida del MEP
        if valor_mep:
            st.metric(label="Cotización Dólar MEP", value=f"${valor_mep}")

        # Mostrar Tabla de Cripto
        st.subheader("🔁 Arbitraje Cripto a Cripto (Solo Pesos)")
        if cripto:
            df_cripto = pd.DataFrame(cripto).sort_values(by="Ganancia", ascending=False)
            # Formato visual de la tabla
            st.dataframe(df_cripto.style.format({"Ganancia": "${:,.2f}"}).background_gradient(subset=["Spread (%)"], cmap="Greens"), use_container_width=True)
        else:
            st.info("Sin oportunidades mayores al 1% en este momento.")

        # Mostrar Tabla MEP
        st.subheader("💵 Rulo MEP a Cripto")
        if mep_rulo:
            df_mep = pd.DataFrame(mep_rulo).sort_values(by="Ganancia", ascending=False)
            st.dataframe(df_mep.style.format({"Ganancia": "${:,.2f}"}).background_gradient(subset=["Spread (%)"], cmap="Greens"), use_container_width=True)
        else:
            st.info("Sin oportunidades mayores al 1% en este momento.")
