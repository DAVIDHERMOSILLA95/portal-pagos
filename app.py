import streamlit as st
import pandas as pd
from supabase import create_client, Client

# --- CONFIGURACIÓN SEGURA (Usando Secrets) ---
# Estas llaves se configuran en el panel de Streamlit Cloud, no en el código
url_sb = st.secrets["SUPABASE_URL"]
key_sb = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url_sb, key_sb)

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Portal de Cuentas por Pagar", layout="wide")

st.title("📑 Panel de Cuentas por Pagar")
st.markdown("---")

# --- CARGA DE DATOS DESDE SUPABASE ---
try:
    response = supabase.table("facturas_pagar").select("*").execute()
    df = pd.DataFrame(response.data)

    if not df.empty:
        # Métricas principales
        col1, col2, col3 = st.columns(3)
        pendientes = df[df['estado'] == 'Pendiente']
        
        col1.metric("Facturas Pendientes", len(pendientes))
        col2.metric("Total por Pagar", f"${pendientes['monto'].sum():,.0f}")
        col3.metric("Proveedores Activos", df['proveedor'].nunique())

        st.subheader("Listado de Documentos")
        
# Busca esta línea en tu archivo app.py y agrega 'folio'
columnas_visibles = ['id', 'folio', 'proveedor', 'rut_proveedor', 'monto', 'fecha_emision', 'estado']
st.dataframe(df[columnas_visibles].sort_values(by='id', ascending=False), use_container_width=True)
        
        # Panel lateral para acciones
        with st.sidebar:
            st.header("Acciones de Gestión")
            id_pago = st.number_input("ID de Factura para gestionar", min_value=int(df['id'].min()), step=1)
            
            if st.button("Marcar como PAGADA"):
                supabase.table("facturas_pagar").update({"estado": "Pagada"}).eq("id", id_pago).execute()
                st.success(f"Factura #{id_pago} actualizada.")
                st.rerun()
                
            if st.button("Marcar como PENDIENTE"):
                supabase.table("facturas_pagar").update({"estado": "Pendiente"}).eq("id", id_pago).execute()
                st.info(f"Factura #{id_pago} reseteada.")
                st.rerun()
    else:
        st.info("Aún no hay facturas registradas en la base de datos.")

except Exception as e:
    st.error(f"Error de conexión: {e}")
    st.info("Asegúrate de haber configurado correctamente los 'Secrets' en Streamlit Cloud.")

  




