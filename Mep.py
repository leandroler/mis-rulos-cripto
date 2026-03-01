import streamlit as st
import requests
from datetime import datetime

# Configuración para el celular
st.set_page_config(page_title="Cara a Cara P2P", page_icon="🥊", layout="centered")

def obtener_mercado(moneda, volumen):
    try:
        url = f"https://criptoya.com/api/{moneda}/ars/{volumen}"
        return requests.get(url, timeout=5).json()
    except:
        return {}

st.title("🥊 Binance vs Bitget")
st.write(f"Actualizado: **{datetime.now().strftime('%H:%M:%S')}**")

capital = st.number_input("Capital a mover ($ ARS):", min_value=10000, value=100000, step=10000)

if st.button("🔄 Comparar Puntas", type="primary"):
    with st.spinner("Buscando precios en el P2P..."):
        usdt = obtener_mercado("usdt", capital)
        usdc = obtener_mercado("usdc", capital)
        
        def mostrar_comparacion(moneda, datos):
            if not datos or 'binancep2p' not in datos or 'bitgetp2p' not in datos:
                st.warning(f"Faltan datos de {moneda} en los exchanges en este momento.")
                return
            
            bin_compra = datos['binancep2p']['ask']
            bit_compra = datos['bitgetp2p']['ask']
            bin_venta = datos['binancep2p']['bid']
            bit_venta = datos['bitgetp2p']['bid']

            st.subheader(f"🪙 {moneda}")
            
            col1, col2 = st.columns(2)
            
            # --- SECCIÓN COMPRA ---
            with col1:
                st.markdown("### 🛒 COMPRA")
                st.caption("Buscás el precio más BAJO")
                st.write(f"**Binance:** ${bin_compra:,.2f}")
                st.write(f"**Bitget:** ${bit_compra:,.2f}")
                
                if bin_compra < bit_compra:
                    st.success(f"🏆 Gana Binance\n(Más barato por ${bit_compra - bin_compra:,.2f})")
                elif bit_compra < bin_compra:
                    st.success(f"🏆 Gana Bitget\n(Más barato por ${bin_compra - bit_compra:,.2f})")
                else:
                    st.info("🤝 Empate")

            # --- SECCIÓN VENTA ---
            with col2:
                st.markdown("### 💸 VENTA")
                st.caption("Buscás el precio más ALTO")
                st.write(f"**Binance:** ${bin_venta:,.2f}")
                st.write(f"**Bitget:** ${bit_venta:,.2f}")
                
                if bin_venta > bit_venta:
                    st.success(f"🏆 Gana Binance\n(Paga más por ${bin_venta - bit_venta:,.2f})")
                elif bit_venta > bin_venta:
                    st.success(f"🏆 Gana Bitget\n(Paga más por ${bit_venta - bin_venta:,.2f})")
                else:
                    st.info("🤝 Empate")
            
            # --- EL RULO IDEAL ---
            mejor_compra = min(bin_compra, bit_compra)
            mejor_venta = max(bin_venta, bit_venta)
            lugar_compra = "Binance" if mejor_compra == bin_compra else "Bitget"
            lugar_venta = "Binance" if mejor_venta == bin_venta else "Bitget"
            
            spread = (mejor_venta / mejor_compra - 1) * 100
            ganancia = (capital / mejor_compra) * mejor_venta - capital
            
            st.markdown("**⚡ La Mejor Jugada Combinada:**")
            if spread > 0:
                st.info(f"Comprar en **{lugar_compra}** y Vender en **{lugar_venta}** \nGanancia Neta: **${ganancia:,.2f}** ({spread:.2f}%)")
            else:
                st.error(f"Comprar en **{lugar_compra}** y Vender en **{lugar_venta}** \nPérdida: **${ganancia:,.2f}** ({spread:.2f}%)")
            st.divider()

        # Ejecutamos la función visual para ambas monedas
        mostrar_comparacion("USDT", usdt)
        mostrar_comparacion("USDC", usdc)
