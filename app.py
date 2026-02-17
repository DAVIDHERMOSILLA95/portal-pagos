import streamlit as st
import pandas as pd
from supabase import create_client, Client

# --- CONFIGURACIÓN SEGURA ---
url_sb = st.secrets["SUPABASE_URL"]
key_sb = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url_sb, key_sb)

st.set_page_config(page_title="Portal AP", layout="wide")

st.title("📑 Panel de Cuentas por Pagar")
st.markdown("---")

# --- CARGA DE DATOS ---
try:
    response = supabase.table("facturas_pagar").select("*").execute()
    df = pd.DataFrame(response.data)

    if not df.empty:
        # Métricas
        col1, col2 = st.columns(2)
        pendientes = df[df['estado'] == 'Pendiente']
        col1.metric("Facturas Pendientes", len(pendientes))
        col2.metric("Total por Pagar", f"${pendientes['monto'].sum():,.0f}")

        st.subheader("Listado de Documentos")
        
        # DEFINICIÓN DE COLUMNAS (Aquí incluimos el folio real)
        # Asegúrate de que esta lista coincida exactamente con los nombres en Supabase
        columnas_visibles = ['id', 'folio', 'proveedor', 'rut_proveedor', 'monto', 'fecha_emision', 'estado']
        
        # Mostramos la tabla filtrando solo las columnas que queremos
        st.dataframe(df[columnas_visibles].sort_values(by='id', ascending=False), use_container_width=True)
        
        # Panel lateral de acciones
        with st.sidebar:
            st.header("Acciones")
            id_pago = st.number_input("ID de registro para pagar", min_value=int(df['id'].min()), step=1)
            if st.button("Marcar como Pagada"):
                supabase.table("facturas_pagar").update({"estado": "Pagada"}).eq("id", id_pago).execute()
                st.success(f"Registro {id_pago} actualizado.")
                st.rerun()
    else:
        st.info("No hay facturas en la base de datos.")

except Exception as e:
    st.error(f"Error crítico: {e}")





