import streamlit as st
import pandas as pd
from supabase import create_client, Client

# --- CONFIGURACIÓN SEGURA ---
# Ahora leemos desde st.secrets en lugar de tener las llaves expuestas
url_sb = st.secrets["SUPABASE_URL"]
key_sb = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url_sb, key_sb)

# El resto del código de la app se mantiene igual...

st.set_page_config(page_title="Portal AP", layout="wide")

st.title("📑 Panel de Cuentas por Pagar")
st.markdown("---")

# --- CARGA DE DATOS ---
response = supabase.table("facturas_pagar").select("*").execute()
df = pd.DataFrame(response.data)

if not df.empty:
    # Mostramos métricas rápidas arriba
    col1, col2 = st.columns(2)
    pendientes = df[df['estado'] == 'Pendiente']
    col1.metric("Facturas Pendientes", len(pendientes))
    col2.metric("Total por Pagar", f"${pendientes['monto'].sum():,.0f}")

    st.subheader("Listado de Documentos")
    # Limpiamos la visualización de la tabla
    st.dataframe(df[['id', 'proveedor', 'rut_proveedor', 'monto', 'fecha_emision', 'estado']], use_container_width=True)
    
    # Acción de pago
    with st.sidebar:
        st.header("Acciones")
        id_pago = st.number_input("ID de Factura a Pagar", min_value=int(df['id'].min()), step=1)
        if st.button("Marcar como Pagada"):
            supabase.table("facturas_pagar").update({"estado": "Pagada"}).eq("id", id_pago).execute()
            st.success(f"Factura {id_pago} pagada.")
            st.rerun()
else:
    st.info("No hay datos registrados aún.")

  

