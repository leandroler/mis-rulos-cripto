import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# Configuración para el celular
st.set_page_config(page_title="Arbitraje Avanzado", page_icon="🔄", layout="centered")

def obtener_mercado(moneda, fiat, volumen):
    try:
        url = f"https://criptoya.com/api/{moneda}/{fiat}/{volumen}"
        return requests.get(url, timeout=5).json()
    except:
        return {}

st.title("🔄 Escáner de Triangulación")
st.write(f"Actualizado: **{datetime.now().strftime('%H:%M:%S')}**")

capital_ars = st.number_input("Capital base en Pesos ($ ARS):", min_value=10000, value=100000, step=10000)
# Estimamos un capital en USD proporcional para buscar liquidez real en esa moneda
capital_usd = capital_ars / 1000 

exchanges_monitor = ['binancep2p', 'bitgetp2p', 'kucoinp2p', 'fiwind', 'lemoncash', 'belo', 'tiendacrypto', 'buenbit', 'letsbit']

if st.button("🔄 Ejecutar Análisis Completo", type="primary"):
    with st.spinner("Analizando rutas directas y cruzadas..."):
        # Traemos todos los datos necesarios
        usdt_ars = obtener_mercado("usdt", "ars", capital_ars)
        usdc_ars = obtener_mercado("usdc", "ars", capital_ars)
        usdc_usd = obtener_mercado("usdc", "usd", capital_usd)
        usdt_usd = obtener_mercado("usdt", "usd", capital_usd)

        def buscar_mejores(datos):
            """Filtra y devuelve la mejor punta de compra y venta de un set de datos"""
            if not datos: return None, None
            mercado = []
            for ex, val in datos.items():
                if ex in exchanges_monitor and val['ask'] > 0 and val['bid'] > 0:
                    mercado.append({"Exchange": ex.replace('p2p', ' P2P').capitalize(), "Ask": val['ask'], "Bid": val['bid']})
            if not mercado: return None, None
            df = pd.DataFrame(mercado)
            mejor_compra = df.sort_values(by="Ask", ascending=True).iloc[0]
            mejor_venta = df.sort_values(by="Bid", ascending=False).iloc[0]
            return mejor_compra, mejor_venta

        # Obtenemos los campeones de cada categoría
        compra_usdt_ars, venta_usdt_ars = buscar_mejores(usdt_ars)
        compra_usdc_ars, venta_usdc_ars = buscar_mejores(usdc_ars)
        compra_usdc_usd, venta_usdc_usd = buscar_mejores(usdc_usd)

        # --- CREACIÓN DE PESTAÑAS EN LA INTERFAZ ---
        tab1, tab2, tab3 = st.tabs(["🔁 Swap USDC/USDT", "💵 Entrada en USD", "🎯 Directos (ARS)"])

        # PESTAÑA 1: TRIANGULACIÓN (SWAP)
        with tab1:
            st.subheader("El Rulo del Swap (Puro Pesos)")
            st.caption("Comprar una moneda, convertirla en Spot (0.1% de fee) y vender la otra.")
            
            if compra_usdc_ars is not None and venta_usdt_ars is not None:
                # Ruta 1: ARS -> USDC -> USDT -> ARS
                cant_usdc = capital_ars / compra_usdc_ars['Ask']
                cant_usdt_post_swap = cant_usdc * 0.999 # Descuento del 0.1% de conversión
                resultado_ruta1 = cant_usdt_post_swap * venta_usdt_ars['Bid']
                spread_ruta1 = (resultado_ruta1 / capital_ars - 1) * 100
                
                st.markdown("### 🟢 Ruta A: USDC a USDT")
                st.write(f"1️⃣ Comprás USDC en **{compra_usdc_ars['Exchange']}** a ${compra_usdc_ars['Ask']:,.2f}")
                st.write(f"2️⃣ Hacés Swap a USDT adentro de Binance/Bitget")
                st.write(f"3️⃣ Vendés USDT en **{venta_usdt_ars['Exchange']}** a ${venta_usdt_ars['Bid']:,.2f}")
                
                if spread_ruta1 > 0:
                    st.success(f"💰 **Ganancia: ${resultado_ruta1 - capital_ars:,.2f}** ({spread_ruta1:.2f}%)")
                else:
                    st.error(f"📉 **Pérdida: ${resultado_ruta1 - capital_ars:,.2f}** ({spread_ruta1:.2f}%)")
                
            st.divider()

            if compra_usdt_ars is not None and venta_usdc_ars is not None:
                # Ruta 2: ARS -> USDT -> USDC -> ARS
                cant_usdt = capital_ars / compra_usdt_ars['Ask']
                cant_usdc_post_swap = cant_usdt * 0.999
                resultado_ruta2 = cant_usdc_post_swap * venta_usdc_ars['Bid']
                spread_ruta2 = (resultado_ruta2 / capital_ars - 1) * 100
                
                st.markdown("### 🔵 Ruta B: USDT a USDC")
                st.write(f"1️⃣ Comprás USDT en **{compra_usdt_ars['Exchange']}** a ${compra_usdt_ars['Ask']:,.2f}")
                st.write(f"2️⃣ Hacés Swap a USDC adentro de Binance/Bitget")
                st.write(f"3️⃣ Vendés USDC en **{venta_usdc_ars['Exchange']}** a ${venta_usdc_ars['Bid']:,.2f}")
                
                if spread_ruta2 > 0:
                    st.success(f"💰 **Ganancia: ${resultado_ruta2 - capital_ars:,.2f}** ({spread_ruta2:.2f}%)")
                else:
                    st.error(f"📉 **Pérdida: ${resultado_ruta2 - capital_ars:,.2f}** ({spread_ruta2:.2f}%)")

        # PESTAÑA 2: ENTRADA BANCARIA EN DÓLARES (USD FIAT)
        with tab2:
            st.subheader("USD a USDC/USDT")
            st.caption("Si tenés dólares en el banco y querés salir en Pesos.")
            
            if compra_usdc_usd is not None and venta_usdt_ars is not None:
                # Cuántos dólares físicos te cuesta comprar 1 USDC
                costo_usd = compra_usdc_usd['Ask'] 
                # Si compro 1 USDC, lo paso a USDT (0.999) y lo vendo por ARS
                tipo_cambio_final = (1 * 0.999) * venta_usdt_ars['Bid'] / costo_usd
                
                st.markdown("### 💵 Dólar Banco -> Cripto -> Pesos")
                st.write(f"1️⃣ Comprás USDC en **{compra_usdc_usd['Exchange']}** pagando **U$D {costo_usd:,.3f}** por cada moneda.")
                st.write(f"2️⃣ Vendés la cripto por ARS en **{venta_usdt_ars['Exchange']}**.")
                
                st.info(f"🏆 **Tipo de Cambio Logrado: ${tipo_cambio_final:,.2f}** por cada Dólar invertido.")
                st.caption("Compará este valor con la cotización del Dólar Blue para saber si te conviene retirarlos del banco o hacer esta ruta web.")
            else:
                st.warning("No hay liquidez reportada para la compra con USD Fiat en este momento.")

        # PESTAÑA 3: DIRECTOS CLÁSICOS
        with tab3:
            st.subheader("Arbitraje Simple (Sin Swaps)")
            if compra_usdt_ars is not None and venta_usdt_ars is not None:
                spread_usdt = (venta_usdt_ars['Bid'] / compra_usdt_ars['Ask'] - 1) * 100
                st.markdown("**🟡 Clásico USDT**")
                st.write(f"Comprar en **{compra_usdt_ars['Exchange']}** | Vender en **{venta_usdt_ars['Exchange']}**")
                st.write(f"Margen: **{spread_usdt:.2f}%**")
                
            st.divider()
            
            if compra_usdc_ars is not None and venta_usdc_ars is not None:
                spread_usdc = (venta_usdc_ars['Bid'] / compra_usdc_ars['Ask'] - 1) * 100
                st.markdown("**🔵 Clásico USDC**")
                st.write(f"Comprar en **{compra_usdc_ars['Exchange']}** | Vender en **{venta_usdc_ars['Exchange']}**")
                st.write(f"Margen: **{spread_usdc:.2f}%**")
