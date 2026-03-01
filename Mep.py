import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# Configuración para el celular
st.set_page_config(page_title="Arbitraje P2P", page_icon="⚖️", layout="centered")

def obtener_mercado_cripto(moneda, volumen):
    try:
        url = f"https://criptoya.com/api/{moneda}/ars/{volumen}"
        return requests.get(url, timeout=5).json()
    except:
        return {}

def buscar_cruces_p2p(capital):
    usdt = obtener_mercado_cripto("usdt", capital)
    usdc = obtener_mercado_cripto("usdc", capital)

    estrategias = []
    mercados = {'USDT': usdt, 'USDC': usdc}
    # Filtramos exclusivamente estos dos gigantes
    exchanges_objetivo = ['binancep2p', 'bitgetp2p']

    for moneda, datos in mercados.items():
        if not datos: continue
        
        for ex_compra in exchanges_objetivo:
            for ex_venta in exchanges_objetivo:
                if ex_compra == ex_venta: continue # No compramos y vendemos en el mismo
                
                try:
                    compra = datos[ex_compra]['ask']
                    venta = datos[ex_venta]['bid']
                    
                    if compra <= 0 or venta <= 0: continue
                    
                    spread = (venta / compra - 1) * 100
                    ganancia = ((capital / compra) * venta) - capital
                    
                    estrategias.append({
                        "Moneda": moneda,
                        "Compro en": ex_compra.replace('p2p', ' P2P').capitalize(),
                        "Vendo en": ex_venta.replace('p2p', ' P2P').capitalize(),
                        "Precio Compra": compra,
                        "Precio Venta": venta,
                        "Ganancia": ganancia,
                        "Spread (%)": round(spread, 2)
                    })
                except KeyError:
                    pass
                    
    return estrategias, usdt, usdc

# --- INTERFAZ VISUAL ---

st.title("⚖️ P2P: Binance vs Bitget")
st.write(f"Última actualización: **{datetime.now().strftime('%H:%M:%S')}**")

capital_usuario = st.number_input("Capital a mover ($ ARS):", min_value=10000, value=100000, step=10000)

if st.button("🔄 Escanear P2P Ahora", type="primary"):
    with st.spinner("Comparando puntas en Binance y Bitget..."):
        estrategias, usdt_data, usdc_data = buscar_cruces_p2p(capital_usuario)
        
        # 1. Mostrar la tabla de rulos posibles
        st.subheader("🔁 Cruces Disponibles")
        if estrategias:
            df = pd.DataFrame(estrategias).sort_values(by="Ganancia", ascending=False)
            
            # Dejamos que se pinten de rojo los negativos para que veas la realidad del mercado
            st.dataframe(
                df.style.format({
                    "Precio Compra": "${:,.2f}", 
                    "Precio Venta": "${:,.2f}", 
                    "Ganancia": "${:,.2f}"
                }).background_gradient(subset=["Spread (%)"], cmap="RdYlGn"), 
                use_container_width=True
            )
        else:
            st.warning("No hay datos suficientes de las APIs en este momento.")

        # 2. Pizarra de referencia rápida
        st.divider()
        st.subheader("📊 Pizarra Cruda (Referencia)")
        st.caption("Precio de Compra (Lo que pagás) | Precio de Venta (Lo que recibís)")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("🟡 **USDT**")
            try: st.write(f"**Binance:** \nCompra ${usdt_data['binancep2p']['ask']} \nVenta ${usdt_data['binancep2p']['bid']}") 
            except: pass
            st.write("---")
            try: st.write(f"**Bitget:** \nCompra ${usdt_data['bitgetp2p']['ask']} \nVenta ${usdt_data['bitgetp2p']['bid']}")
            except: pass
            
        with col2:
            st.markdown("🔵 **USDC**")
            try: st.write(f"**Binance:** \nCompra ${usdc_data['binancep2p']['ask']} \nVenta ${usdc_data['binancep2p']['bid']}")
            except: pass
            st.write("---")
            try: st.write(f"**Bitget:** \nCompra ${usdc_data['bitgetp2p']['ask']} \nVenta ${usdc_data['bitgetp2p']['bid']}")
            except: pass
