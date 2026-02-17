import streamlit as st
import pandas as pd
from supabase import create_client, Client

# --- CONFIGURACIÓN SEGURA ---
url_sb = st.secrets["SUPABASE_URL"]
key_sb = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url_sb, key_sb)

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Gestión Financiera | AP Portal", layout="wide", page_icon="💰")

# --- ESTILOS CSS CORREGIDOS ---
st.markdown("""
    <style>
    /* Estilo para las tarjetas de métricas */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
    }
    div[data-testid="metric-container"] {
        background-color: rgba(255, 255, 255, 0.05); /* Fondo sutil que sirve en ambos modos */
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 10px;
        color: inherit;
    }
    /* Estilo general */
    .stDataFrame { border-radius: 10px; }
    h1 { font-weight: 700; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE DATOS ---
try:
    response = supabase.table("facturas_pagar").select("*").execute()
    df = pd.DataFrame(response.data)

    if not df.empty:
        st.title("🚀 Panel de Control Administrativo")
        st.caption("Gestión centralizada de cuentas por pagar y flujo de caja")
        st.markdown("---")

        # KPIs
        pendientes = df[df['estado'] == 'Pendiente']
        total_deuda = pendientes['monto'].sum()
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Pendientes", len(pendientes))
        m2.metric("Total por Pagar", f"${total_deuda:,.0f} CLP")
        m3.metric("Pagadas (Mes)", len(df[df['estado'] == 'Pagada']))
        m4.metric("Proveedores", df['proveedor'].nunique())

        st.markdown("### 📋 Listado Maestro de Documentos")
        
        # TABLA DINÁMICA
        columnas = ['folio', 'proveedor', 'rut_proveedor', 'monto', 'fecha_emision', 'estado']
        st.dataframe(
            df[columnas].sort_values(by='fecha_emision', ascending=False),
            use_container_width=True,
            column_config={
                "monto": st.column_config.NumberColumn("Monto", format="$ %d"),
                "estado": st.column_config.SelectboxColumn("Estado", options=["Pendiente", "Pagada"]),
                "folio": "N° Folio"
            },
            hide_index=True # Limpia la vista quitando la columna de índices
        )

        # PANEL LATERAL
        with st.sidebar:
            st.header("⚙️ Acciones Rápidas")
            lista_folios = pendientes['folio'].unique().tolist()
            if lista_folios:
                sel_folio = st.selectbox("Documento a gestionar:", lista_folios)
                if st.button("Confirmar Pago ✅"):
                    supabase.table("facturas_pagar").update({"estado": "Pagada"}).eq("folio", sel_folio).execute()
                    st.toast(f"Factura {sel_folio} pagada")
                    st.rerun()
            else:
                st.success("¡Todo pagado! ☕")

except Exception as e:
    st.error(f"Error de conexión: {e}")
