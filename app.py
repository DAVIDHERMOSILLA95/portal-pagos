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
        
        # DEFINICIÓN DE COLUMNAS
        columnas_visibles = ['folio', 'proveedor', 'rut_proveedor', 'monto', 'fecha_emision', 'estado']
        
        # Mostramos la tabla (quitamos el 'id' de la vista para no confundir)
        st.dataframe(df[columnas_visibles].sort_values(by='fecha_emision', ascending=False), use_container_width=True)
        
        # Panel lateral de acciones mejorado
        with st.sidebar:
            st.header("Gestión de Pagos")
            
            # Filtramos solo los folios que están pendientes para que sea más fácil elegir
            lista_folios_pendientes = pendientes['folio'].unique().tolist()
            
            if lista_folios_pendientes:
                folio_seleccionado = st.selectbox("Selecciona Folio para pagar", lista_folios_pendientes)
                
                if st.button("Marcar como Pagada"):
                    # Actualizamos en la base de datos buscando por la columna 'folio'
                    supabase.table("facturas_pagar").update({"estado": "Pagada"}).eq("folio", folio_seleccionado).execute()
                    st.success(f"Factura Folio {folio_seleccionado} marcada como pagada.")
                    st.rerun()
            else:
                st.write("No hay folios pendientes de pago.")
                
    else:
        st.info("No hay facturas en la base de datos.")

except Exception as e:
    st.error(f"Error crítico: {e}")





