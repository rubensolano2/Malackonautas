# app_streamlit_sqlite.py
# ------------------------------------------------------------
# Explorador de Datos Intuitivo • Streamlit + SQLite
# - Carga automática de BD SQLite o importación de CSV directo
# - Interfaz simplificada y amigable
# - Exploración visual con filtros inteligentes
# - Gráficos interactivos automáticos
# - Exportación fácil de resultados
# ------------------------------------------------------------

import os
import io
import time
from typing import Optional, List, Tuple

import streamlit as st
import pandas as pd
import altair as alt
import sqlite3

# ======================
# Configuración
# ======================
st.set_page_config(
    page_title="Explorador de Datos",
    page_icon="📊",
    layout="wide"
)

# ======================
# Estilos mejorados
# ======================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
* { font-family: 'Inter', sans-serif; }
.main { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; }
.block-container { max-width: 1400px; background: white; border-radius: 20px; padding: 2rem; box-shadow: 0 20px 60px rgba(0,0,0,0.3); }

.header { 
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
    border-radius: 15px; 
    padding: 2rem; 
    margin-bottom: 2rem;
    color: white;
    text-align: center;
}
.header h1 { color: white; font-size: 2.5rem; font-weight: 700; margin: 0; }
.header p { color: rgba(255,255,255,0.9); font-size: 1.1rem; margin-top: 0.5rem; }

.metric-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 12px;
    padding: 1.5rem;
    color: white;
    text-align: center;
    margin: 0.5rem 0;
}
.metric-card h3 { font-size: 2rem; margin: 0; font-weight: 700; color: white; }
.metric-card p { font-size: 0.9rem; margin: 0.5rem 0 0 0; opacity: 0.9; color: white; }

.stButton>button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.75rem 2rem !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
}
.stButton>button:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
}

.success-box {
    background: #d4edda;
    border-left: 4px solid #28a745;
    padding: 1rem;
    border-radius: 8px;
    margin: 1rem 0;
    color: #000;
}
.success-box h2, .success-box p, .success-box li, .success-box ol, .success-box strong {
    color: #000 !important;
}

.info-box {
    background: #d1ecf1;
    border-left: 4px solid #17a2b8;
    padding: 1rem;
    border-radius: 8px;
    margin: 1rem 0;
    color: #000;
}
.info-box h2, .info-box p, .info-box li, .info-box ol, .info-box strong {
    color: #000 !important;
}

/* Asegurar que todo el texto sea negro */
p, span, div, li, label, h1, h2, h3, h4, h5, h6 {
    color: #000 !important;
}

/* Excepto en header y metric cards */
.header *, .metric-card * {
    color: white !important;
}

/* DataFrames y tablas */
.dataframe, .stDataFrame {
    color: #000 !important;
}
.dataframe td, .dataframe th {
    color: #000 !important;
}

/* Inputs y selectores */
.stSelectbox label, .stMultiselect label, .stTextInput label, .stNumberInput label, .stSlider label {
    color: #000 !important;
    font-weight: 600 !important;
}
</style>
""", unsafe_allow_html=True)

# ======================
# Funciones de utilidad
# ======================

@st.cache_resource
def get_sqlite_connection(db_path: str):
    """Conexión a SQLite con caché"""
    if not os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        conn.close()
    conn = sqlite3.connect(db_path, check_same_thread=False)
    return conn

@st.cache_data(ttl=300)
def run_query(db_path: str, sql: str) -> pd.DataFrame:
    """Ejecuta query y parsea tipos automáticamente"""
    conn = get_sqlite_connection(db_path)
    df = pd.read_sql_query(sql, conn)
    
    # Parseo inteligente de tipos
    for col in df.columns:
        if df[col].dtype == 'object':
            try:
                df[col] = pd.to_datetime(df[col])
            except:
                try:
                    df[col] = pd.to_numeric(df[col])
                except:
                    pass
    return df

@st.cache_data(ttl=300)
def list_tables(db_path: str) -> List[str]:
    """Lista todas las tablas"""
    sql = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    df = run_query(db_path, sql)
    return df['name'].tolist() if not df.empty else []

def import_csv_to_db(csv_file, db_path: str, table_name: str):
    """Importa CSV a SQLite"""
    try:
        df = pd.read_csv(csv_file, encoding='utf-8')
    except:
        df = pd.read_csv(csv_file, encoding='latin-1')
    
    conn = get_sqlite_connection(db_path)
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    return df

def download_data(df: pd.DataFrame, format: str) -> bytes:
    """Genera archivo descargable"""
    if format == 'csv':
        return df.to_csv(index=False).encode('utf-8')
    elif format == 'excel':
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Datos')
        return output.getvalue()
    elif format == 'parquet':
        output = io.BytesIO()
        df.to_parquet(output, index=False)
        return output.getvalue()

# ======================
# Header
# ======================
st.markdown("""
<div class="header">
    <h1>📊 Explorador Inteligente de Datos</h1>
    <p>Analiza tus datos sin programar • Visualizaciones automáticas • Exportación instantánea</p>
</div>
""", unsafe_allow_html=True)

# ======================
# Inicialización
# ======================
if 'db_path' not in st.session_state:
    st.session_state.db_path = 'datos.db'
if 'current_table' not in st.session_state:
    st.session_state.current_table = None

db_path = st.session_state.db_path

# ======================
# Sidebar: Carga de datos
# ======================
with st.sidebar:
    st.markdown("### 📁 Cargar Datos")
    
    tab1, tab2 = st.tabs(["📄 Desde CSV", "🗄️ Base de Datos"])
    
    with tab1:
        st.markdown("**Importar archivo CSV**")
        uploaded_file = st.file_uploader("Selecciona tu CSV", type=['csv'], help="Arrastra o selecciona tu archivo")
        
        if uploaded_file:
            table_name = st.text_input("Nombre de la tabla", value="datos_importados")
            
            if st.button("🚀 Importar CSV", use_container_width=True):
                with st.spinner("Importando datos..."):
                    try:
                        df = import_csv_to_db(uploaded_file, db_path, table_name)
                        st.session_state.current_table = table_name
                        list_tables.clear()
                        st.success(f"✅ {len(df)} filas importadas correctamente")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
    
    with tab2:
        st.markdown("**Conectar a BD SQLite**")
        db_input = st.text_input("Ruta de la BD", value=db_path)
        if st.button("🔌 Conectar", use_container_width=True):
            if os.path.exists(db_input):
                st.session_state.db_path = db_input
                st.success("✅ Conectado")
                st.rerun()
            else:
                st.warning("⚠️ Archivo no encontrado")
    
    st.markdown("---")
    
    # Lista de tablas disponibles
    tables = list_tables(db_path)
    if tables:
        st.markdown("### 📋 Tablas Disponibles")
        selected = st.radio("Selecciona una tabla:", tables, index=0)
        if selected != st.session_state.current_table:
            st.session_state.current_table = selected
            st.rerun()

# ======================
# Contenido Principal
# ======================

if st.session_state.current_table:
    table = st.session_state.current_table
    
    # Cargar datos
    df = run_query(db_path, f'SELECT * FROM "{table}" LIMIT 10000')
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{len(df):,}</h3>
            <p>Filas</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{len(df.columns)}</h3>
            <p>Columnas</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        numeric_cols = df.select_dtypes(include=['number']).columns
        st.markdown(f"""
        <div class="metric-card">
            <h3>{len(numeric_cols)}</h3>
            <p>Numéricas</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        missing = df.isnull().sum().sum()
        st.markdown(f"""
        <div class="metric-card">
            <h3>{missing:,}</h3>
            <p>Valores Nulos</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Tabs para diferentes secciones
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Vista de Datos", "🔍 Filtros y Análisis", "📈 Visualizaciones", "💾 Exportar"])
    
    # TAB 1: Vista de datos
    with tab1:
        st.markdown("### 📋 Vista General de los Datos")
        
        # Selector de columnas
        all_cols = df.columns.tolist()
        selected_cols = st.multiselect(
            "Selecciona columnas a mostrar:",
            options=all_cols,
            default=all_cols[:10] if len(all_cols) > 10 else all_cols
        )
        
        if selected_cols:
            display_df = df[selected_cols]
        else:
            display_df = df
        
        # Paginación
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            rows_per_page = st.selectbox("Filas por página:", [25, 50, 100, 250], index=1)
        with col2:
            total_pages = max(1, (len(display_df) - 1) // rows_per_page + 1)
            page = st.number_input("Página:", min_value=1, max_value=total_pages, value=1)
        with col3:
            st.metric("Total páginas", total_pages)
        
        start_idx = (page - 1) * rows_per_page
        end_idx = start_idx + rows_per_page
        
        # Mostrar información de registros
        st.info(f"📊 Mostrando registros {start_idx + 1} a {min(end_idx, len(display_df))} de {len(display_df)}")
        
        # DataFrame con mejor formato
        st.dataframe(
            display_df.iloc[start_idx:end_idx],
            use_container_width=True,
            height=400
        )
        
        # Estadísticas rápidas
        with st.expander("📊 Estadísticas Descriptivas"):
            st.markdown("**Resumen estadístico de todas las columnas:**")
            stats_df = display_df.describe(include='all').transpose()
            st.dataframe(stats_df, use_container_width=True, height=400)
    
    # TAB 2: Filtros
    with tab2:
        st.markdown("### 🔍 Filtros Inteligentes")
        
        col1, col2 = st.columns(2)
        
        with col1:
            filter_col = st.selectbox("Columna a filtrar:", ["--Selecciona--"] + df.columns.tolist())
        
        filtered_df = df.copy()
        
        if filter_col != "--Selecciona--":
            with col2:
                col_data = df[filter_col]
                
                # Filtro según tipo de dato
                if pd.api.types.is_numeric_dtype(col_data):
                    min_val = float(col_data.min())
                    max_val = float(col_data.max())
                    range_vals = st.slider(
                        "Rango de valores:",
                        min_val, max_val, (min_val, max_val)
                    )
                    filtered_df = df[(df[filter_col] >= range_vals[0]) & (df[filter_col] <= range_vals[1])]
                
                elif pd.api.types.is_datetime64_any_dtype(col_data):
                    date_range = st.date_input(
                        "Rango de fechas:",
                        value=(col_data.min(), col_data.max())
                    )
                    if len(date_range) == 2:
                        filtered_df = df[(df[filter_col] >= pd.Timestamp(date_range[0])) & 
                                        (df[filter_col] <= pd.Timestamp(date_range[1]))]
                    else:
                        filtered_df = df
                
                else:
                    unique_vals = col_data.dropna().unique()
                    if len(unique_vals) <= 20:
                        selected_vals = st.multiselect(
                            "Selecciona valores:",
                            options=unique_vals.tolist(),
                            default=unique_vals.tolist()
                        )
                        if selected_vals:
                            filtered_df = df[df[filter_col].isin(selected_vals)]
                    else:
                        search_term = st.text_input("Buscar texto:")
                        if search_term:
                            filtered_df = df[df[filter_col].astype(str).str.contains(search_term, case=False, na=False)]
                        else:
                            filtered_df = df
            
            st.success(f"✅ Resultados: {len(filtered_df):,} de {len(df):,} filas")
            st.dataframe(filtered_df.head(100), use_container_width=True, height=350)
            
            # Análisis por grupos
            st.markdown("---")
            st.markdown("### 📊 Análisis por Grupos")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                categorical_cols = [c for c in filtered_df.columns if filtered_df[c].dtype == 'object' or len(filtered_df[c].unique()) < 50]
                group_col = st.selectbox("Agrupar por:", ["--No agrupar--"] + categorical_cols)
            
            if group_col != "--No agrupar--":
                with col2:
                    numeric_cols_filter = [c for c in filtered_df.columns if pd.api.types.is_numeric_dtype(filtered_df[c])]
                    if numeric_cols_filter:
                        agg_col = st.selectbox("Columna a agregar:", numeric_cols_filter)
                    else:
                        st.warning("No hay columnas numéricas para agregar")
                        agg_col = None
                with col3:
                    agg_func = st.selectbox("Función:", ["sum", "mean", "count", "min", "max"])
                
                if st.button("🔄 Calcular") and agg_col:
                    grouped = filtered_df.groupby(group_col)[agg_col].agg(agg_func).reset_index()
                    grouped.columns = [group_col, f"{agg_func}_{agg_col}"]
                    grouped = grouped.sort_values(f"{agg_func}_{agg_col}", ascending=False)
                    
                    st.success(f"✅ Grupos calculados: {len(grouped)}")
                    st.dataframe(grouped, use_container_width=True, height=300)
                    
                    # Gráfico automático
                    st.markdown("**📊 Visualización:**")
                    chart = alt.Chart(grouped.head(20)).mark_bar(color='#667eea').encode(
                        x=alt.X(group_col, sort='-y'),
                        y=f"{agg_func}_{agg_col}:Q",
                        tooltip=[group_col, f"{agg_func}_{agg_col}"]
                    ).properties(height=400)
                    st.altair_chart(chart, use_container_width=True)
    
    # TAB 3: Visualizaciones
    with tab3:
        st.markdown("### 📈 Visualizaciones Interactivas")
        
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        viz_type = st.selectbox(
            "Tipo de visualización:",
            ["Gráfico de Barras", "Histograma", "Dispersión", "Línea de Tiempo", "Caja"]
        )
        
        if viz_type == "Gráfico de Barras" and categorical_cols and numeric_cols:
            col1, col2 = st.columns(2)
            with col1:
                x_col = st.selectbox("Categoría (X):", categorical_cols)
            with col2:
                y_col = st.selectbox("Valor (Y):", numeric_cols)
            
            chart_data = df.groupby(x_col)[y_col].mean().reset_index().head(20)
            chart = alt.Chart(chart_data).mark_bar(color='#667eea').encode(
                x=alt.X(x_col, sort='-y'),
                y=y_col,
                tooltip=[x_col, y_col]
            ).properties(height=500)
            st.altair_chart(chart, use_container_width=True)
        
        elif viz_type == "Histograma" and numeric_cols:
            col = st.selectbox("Columna:", numeric_cols)
            bins = st.slider("Número de bins:", 10, 100, 30)
            
            chart = alt.Chart(df).mark_bar(color='#764ba2').encode(
                x=alt.X(col, bin=alt.Bin(maxbins=bins)),
                y='count()',
                tooltip=['count()']
            ).properties(height=500)
            st.altair_chart(chart, use_container_width=True)
        
        elif viz_type == "Dispersión" and len(numeric_cols) >= 2:
            col1, col2, col3 = st.columns(3)
            with col1:
                x_col = st.selectbox("Eje X:", numeric_cols)
            with col2:
                y_col = st.selectbox("Eje Y:", [c for c in numeric_cols if c != x_col])
            with col3:
                color_col = st.selectbox("Color:", ["--Ninguno--"] + categorical_cols)
            
            chart = alt.Chart(df.sample(min(1000, len(df)))).mark_circle(size=60).encode(
                x=x_col,
                y=y_col,
                tooltip=[x_col, y_col] + ([color_col] if color_col != "--Ninguno--" else [])
            )
            
            if color_col != "--Ninguno--":
                chart = chart.encode(color=color_col)
            
            chart = chart.properties(height=500).interactive()
            st.altair_chart(chart, use_container_width=True)
    
    # TAB 4: Exportar
    with tab4:
        st.markdown("### 💾 Exportar Resultados")
        
        st.info("📥 Descarga tus datos en diferentes formatos")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            csv_data = download_data(df, 'csv')
            st.download_button(
                label="📄 Descargar CSV",
                data=csv_data,
                file_name=f"{table}_export.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            excel_data = download_data(df, 'excel')
            st.download_button(
                label="📊 Descargar Excel",
                data=excel_data,
                file_name=f"{table}_export.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        with col3:
            parquet_data = download_data(df, 'parquet')
            st.download_button(
                label="🗜️ Descargar Parquet",
                data=parquet_data,
                file_name=f"{table}_export.parquet",
                mime="application/octet-stream",
                use_container_width=True
            )

else:
    # Pantalla de bienvenida
    st.markdown("""
    <div class="info-box">
        <h2>👋 ¡Bienvenido al Explorador de Datos!</h2>
        <p><strong>Para empezar:</strong></p>
        <ol>
            <li>📁 Carga un archivo CSV desde el panel lateral</li>
            <li>🗄️ O conecta una base de datos SQLite existente</li>
            <li>📊 Explora, filtra y visualiza tus datos sin programar</li>
        </ol>
        <p style="margin-top: 1rem;">✨ <strong>Todo es intuitivo y automático</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🎯 Características principales:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **📊 Exploración Visual**
        - Vista de datos paginada
        - Estadísticas automáticas
        - Detección de tipos
        """)
    
    with col2:
        st.markdown("""
        **🔍 Filtros Inteligentes**
        - Filtros por rango
        - Búsqueda de texto
        - Agrupaciones dinámicas
        """)
    
    with col3:
        st.markdown("""
        **📈 Visualizaciones**
        - Gráficos interactivos
        - Múltiples tipos
        - Exportación fácil
        """)

st.markdown("---")
st.markdown("""
<p style="text-align: center; color: #666; font-size: 0.9rem;">
    🚀 Explorador de Datos v2.0 • Hecho con Streamlit
</p>
""", unsafe_allow_html=True)