import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# Configuración para el celular
st.set_page_config(page_title="Radar Cripto", page_icon="🌍", layout="centered")

def obtener_mercado(moneda, volumen):
    try:
        url = f"https://criptoya.com/api/{moneda}/ars/{volumen}"
        return requests.get(url, timeout=5).json()
    except:
        return {}

st.title("🌍 Radar Multi-Exchange")
st.write(f"Actualizado: **{datetime.now().strftime('%H:%M:%S')}**")

capital = st.number_input("Capital a mover ($ ARS):", min_value=10000, value=100000, step=10000)

# Lista ampliada de plataformas a monitorear
exchanges_monitor = [
    'binancep2p', 'bitgetp2p', 'kucoinp2p', 'okxp2p', 
    'fiwind', 'lemoncash', 'belo', 'tiendacrypto', 'buenbit', 'letsbit'
]

if st.button("🔄 Escanear Todo el Mercado", type="primary"):
    with st.spinner("Rastreando cotizaciones en 10+ plataformas..."):
        usdt = obtener_mercado("usdt", capital)
        usdc = obtener_mercado("usdc", capital)
        
        def analizar_y_mostrar(moneda, datos):
            if not datos:
                st.warning(f"No hay datos de {moneda} en este momento.")
                return
            
            # Filtramos solo los exchanges que nos interesan y que tengan datos válidos
            mercado_filtrado = []
            for ex, valores in datos.items():
                if ex in exchanges_monitor and valores['ask'] > 0 and valores['bid'] > 0:
                    mercado_filtrado.append({
                        "Exchange": ex.replace('p2p', ' P2P').capitalize(),
                        "Compra (Ask)": valores['ask'],
                        "Venta (Bid)": valores['bid']
                    })
            
            if not mercado_filtrado:
                return

            df = pd.DataFrame(mercado_filtrado)
            
            # Ordenamos para encontrar los mejores precios
            top_compras = df.sort_values(by="Compra (Ask)", ascending=True).head(3)
            top_ventas = df.sort_values(by="Venta (Bid)", ascending=False).head(3)
            
            # Datos de la mejor jugada
            mejor_compra = top_compras.iloc[0]
            mejor_venta = top_ventas.iloc[0]
            
            ganancia = (capital / mejor_compra['Compra (Ask)']) * mejor_venta['Venta (Bid)'] - capital
            spread = (mejor_venta['Venta (Bid)'] / mejor_compra['Compra (Ask)'] - 1) * 100

            st.subheader(f"🪙 {moneda}")
            
            # --- LA JUGADA MAESTRA ---
            st.markdown("**⚡ La Mejor Ruta de Arbitraje:**")
            if spread > 0:
                st.success(f"1️⃣ Comprar en **{mejor_compra['Exchange']}** a ${mejor_compra['Compra (Ask)']:,.2f}\n"
                           f"2️⃣ Vender en **{mejor_venta['Exchange']}** a ${mejor_venta['Venta (Bid)']:,.2f}\n"
                           f"💰 **Ganancia Neta: ${ganancia:,.2f}** ({spread:.2f}%)")
            else:
                st.error(f"Mercado en rojo. La 'mejor' opción da pérdida:\n"
                         f"Comprar en **{mejor_compra['Exchange']}** y Vender en **{mejor_venta['Exchange']}**\n"
                         f"📉 **Pérdida: ${ganancia:,.2f}** ({spread:.2f}%)")

            # --- EL PODIO VISUAL ---
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🛒 Top 3 Compras")
                st.caption("Los más baratos para entrar")
                for i, row in top_compras.iterrows():
                    st.write(f"**{row['Exchange']}:** ${row['Compra (Ask)']:,.2f}")
                    
            with col2:
                st.markdown("### 💸 Top 3 Ventas")
                st.caption("Los que más pagan al salir")
                for i, row in top_ventas.iterrows():
                    st.write(f"**{row['Exchange']}:** ${row['Venta (Bid)']:,.2f}")
            
            st.divider()

        # Ejecutamos el análisis para USDT y USDC
        analizar_y_mostrar("USDT", usdt)
        analizar_y_mostrar("USDC", usdc)
