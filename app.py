import streamlit as st
import pandas as pd
from supabase import create_client, Client

# --- CONFIGURACIÓN SEGURA ---
url_sb = st.secrets["SUPABASE_URL"]
key_sb = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url_sb, key_sb)

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Gestión Financiera | AP Portal", layout="wide", page_icon="💰")

# --- ESTILOS CSS PERSONALIZADOS ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .stDataFrame { border: none; border-radius: 10px; overflow: hidden; }
    h1 { color: #1e293b; font-weight: 700; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #2563eb; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE DATOS ---
try:
    response = supabase.table("facturas_pagar").select("*").execute()
    df = pd.DataFrame(response.data)

    if not df.empty:
        # TÍTULO Y MÉTRICAS
        st.title("🚀 Panel de Control Administrativo")
        st.caption("Gestión centralizada de cuentas por pagar y flujo de caja")
        st.markdown("---")

        # FILA DE MÉTRICAS (KPIs)
        pendientes = df[df['estado'] == 'Pendiente']
        total_deuda = pendientes['monto'].sum()
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Pendientes", len(pendientes), delta_color="inverse")
        m2.metric("Total por Pagar", f"${total_deuda:,.0f} CLP")
        m3.metric("Pagadas (Mes)", len(df[df['estado'] == 'Pagada']))
        m4.metric("Proveedores", df['proveedor'].nunique())

        st.markdown("### 📋 Listado Maestro de Documentos")
        
        # TABLA CON FORMATO
        columnas = ['folio', 'proveedor', 'rut_proveedor', 'monto', 'fecha_emision', 'estado']
        # Aplicamos un estilo visual a la tabla
        st.dataframe(
            df[columnas].sort_values(by='fecha_emision', ascending=False),
            use_container_width=True,
            column_config={
                "monto": st.column_config.NumberColumn("Monto", format="$ %d"),
                "estado": st.column_config.SelectboxColumn("Estado", options=["Pendiente", "Pagada"]),
                "folio": "N° Folio"
            }
        )

        # PANEL LATERAL DE GESTIÓN
        with st.sidebar:
            st.image("https://cdn-icons-png.flaticon.com/512/3135/3135706.png", width=80)
            st.header("Acciones Rápidas")
            st.write("Selecciona un documento para actualizar su estado de pago.")
            
            lista_folios = pendientes['folio'].unique().tolist()
            if lista_folios:
                sel_folio = st.selectbox("Documento a gestionar:", lista_folios)
                if st.button("Confirmar Pago ✅"):
                    supabase.table("facturas_pagar").update({"estado": "Pagada"}).eq("folio", sel_folio).execute()
                    st.toast(f"Factura {sel_folio} pagada con éxito")
                    st.rerun()
            else:
                st.success("¡Al día! No hay facturas pendientes.")

    else:
        st.info("Esperando recepción de nuevos documentos...")

except Exception as e:
    st.error(f"Error de conexión: {e}")






