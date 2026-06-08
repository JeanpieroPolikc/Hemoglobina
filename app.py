import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import os

from scipy.stats import kstest
from scipy.stats import norm

# =====================================================
# 1. CONFIGURACIÓN E INTERFAZ VISUAL (CSS)
# =====================================================

st.set_page_config(
    page_title="Investigación Hemoglobina - HRHDE 2026",
    page_icon="🩸",
    layout="wide"
)

# Estilo web enfocado en consistencia y lectura rápida de laboratorios
st.markdown("""
    <style>
        .stApp { background-color: #fcfdfe; }
        .main-title {
            color: #1e3a8a;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-weight: 800;
            text-align: center;
            margin-bottom: 0px;
        }
        .subtitle {
            color: #475569;
            text-align: center;
            font-size: 1.2rem;
            margin-bottom: 25px;
            font-weight: 400;
        }
        button[data-baseweb="tab"] {
            font-size: 1.05rem !important;
            font-weight: 600 !important;
            padding: 10px 20px !important;
        }
        [data-testid="stMetricValue"] {
            color: #b91c1c !important;
            font-weight: 800;
        }
        .stButton>button {
            background-color: #1e3a8a !important;
            color: white !important;
            border-radius: 8px !important;
            width: 100%;
            height: 3em;
            font-weight: bold;
        }
        .info-card {
            background-color: #ffffff;
            padding: 18px;
            border-radius: 12px;
            border-left: 6px solid #1e3a8a;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            margin-bottom: 20px;
        }
        h4 {
            color: #1e3a8a !important;
            font-weight: 700 !important;
            margin-top: 20px !important;
        }
    </style>
""", unsafe_allow_html=True)

# MAPEO DE PALETA DE COLORES FIJOS (Para consistencia visual absoluta)
COLOR_MAP = {"Masculino": "#1e3a8a", "Femenino": "#db2777"}

# =====================================================
# 2. MANEJO DE DATOS E HISTÓRICOS
# =====================================================

if not os.path.exists("datos_investigacion.xlsx"):
    pd.DataFrame(columns=["Edad", "Sexo", "Hemoglobina"]).to_excel("datos_investigacion.xlsx", index=False)

df = pd.read_excel("datos_investigacion.xlsx")

if len(df) > 0:
    df["Sexo"] = df["Sexo"].astype(str).str.strip().replace({
        "M":"Masculino", "F":"Femenino", "m":"Masculino", "f":"Femenino",
        "masculino":"Masculino", "femenino":"Femenino"
    })

def categorizar_edad(edad):
    if 5 <= edad <= 11: return "Niños (5–11 años)"
    elif 12 <= edad <= 29: return "Adolescentes/Jóvenes (12–29 años)"
    elif 30 <= edad <= 59: return "Adultos (30–59 años)"
    elif edad >= 60: return "Adultos Mayores (60 años a más)"

if len(df) > 0:
    df["Grupo_Edad"] = df["Edad"].apply(categorizar_edad)

grupos_edad_fijos = [
    "Niños (5–11 años)", 
    "Adolescentes/Jóvenes (12–29 años)", 
    "Adultos (30–59 años)", 
    "Adultos Mayores (60 años a más)",
    "Otros (No incluidos)"
]

# =====================================================
# 3. ENCABEZADO HOSPITALARIO
# =====================================================

st.markdown('<h1 class="main-title">Hospital Regional Honorio Delgado Espinoza</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Sistema Clínico de Estandarización de Valores Referenciales de Hemoglobina (Arequipa, 2026)</p>', unsafe_allow_html=True)

# =====================================================
# 4. SISTEMA DE PESTAÑAS (TABS)
# =====================================================

tabs = st.tabs([
    "📥 Registro Clínico", 
    "📊 Estadística Descriptiva", 
    "📐 Intervalos de Referencia", 
    "🔬 Validación (Normalidad)", 
    "📈 Campanas y Gráficos Analíticos",
    "🗃️ Base de Datos"
])

# --- TAB 1: REGISTRO ---
with tabs[0]:
    st.markdown("### 📥 Registro de Nuevas Muestras Clínicas")
    with st.form("registro_form"):
        col1, col2, col3 = st.columns(3)
        with col1: edad_in = st.number_input("Edad del Paciente (Años):", 5, 115, value=25)
        with col2: sexo_in = st.selectbox("Sexo Biológico:", ["Masculino", "Femenino"])
        with col3: hb_in = st.number_input("Dosaje de Hemoglobina (g/dL):", 0.0, 35.0, step=0.1, value=13.5)
        
        submit = st.form_submit_button("💾 GUARDAR REGISTRO EN EXCEL")
        if submit:
            nuevo = pd.DataFrame({"Edad": [edad_in], "Sexo": [sexo_in], "Hemoglobina": [hb_in]})
            df = pd.concat([df, nuevo], ignore_index=True)
            df.to_excel("datos_investigacion.xlsx", index=False)
            st.success("✅ Paciente añadido al histórico correctamente.")
            st.rerun()

# --- TAB 2: ESTADÍSTICA DESCRIPTIVA ---
with tabs[1]:
    st.markdown("### 📊 Perfil Clínico de la Población de Estudio")
    if len(df) > 0:
        m1, m2, m3 = st.columns(3)
        m1.metric("Población Evaluada (N)", len(df))
        m2.metric("Promedio General Hb", f"{df['Hemoglobina'].mean():.2f} g/dL")
        m3.metric("Mediana de Edad", f"{df['Edad'].median():.1f} años")

        st.markdown("#### Distribución Descriptiva por Sexo")
        res_sexo = []
        for s in ["Masculino", "Femenino"]:
            sub = df[df["Sexo"] == s]
            if len(sub) > 0:
                m, sd = sub["Hemoglobina"].mean(), sub["Hemoglobina"].std()
                res_sexo.append({
                    "Sexo": s, "Casos (n)": len(sub),
                    "Mínimo": f"{sub['Hemoglobina'].min():.2f}", "Máximo": f"{sub['Hemoglobina'].max():.2f}",
                    "Media (x̄)": f"{m:.2f}", "DE (SD)": f"{(sd if len(sub)>1 else 0.0):.2f}",
                    "CV (%)": f"{( (sd/m*100) if len(sub)>1 else 0.0):.2f}"
                })
        st.table(pd.DataFrame(res_sexo))
    else:
        st.info("No hay datos en el sistema. Ingrese registros en la pestaña 1.")

# --- TAB 3: INTERVALOS DE REFERENCIA (AMBOS DESGLOSES COMPLETOS) ---
with tabs[2]:
    st.markdown("### 📐 Cálculo Paramétrico de Intervalos Biológicos de Referencia")
    st.markdown("""
        <div class="info-card">
            <strong>Criterio Estadístico Aplicado (CLSI):</strong> Límites calculados al 95% de confianza central de la distribución gaussiana.<br>
            <code>Ecuación: Límite Inferior (LI) = x̄ - 1.96(SD)</code> &nbsp;|&nbsp; <code>Límite Superior (LS) = x̄ + 1.96(SD)</code>
        </div>
    """, unsafe_allow_html=True)
    
    # SECCIÓN 1: SEXO
    st.markdown("#### A. Valores de Referencia según Criterio de Sexo (Población Total)")
    tabla_sexo = []
    for s in ["Masculino", "Femenino"]:
        sub = df[df["Sexo"] == s] if len(df) > 0 else []
        n = len(sub)
        if n >= 2:
            m, sd = sub["Hemoglobina"].mean(), sub["Hemoglobina"].std()
            tabla_sexo.append({
                "Variable (Sexo)": s, "N": n, "Mínimo": f"{sub['Hemoglobina'].min():.2f}", "Máximo": f"{sub['Hemoglobina'].max():.2f}",
                "Media (x̄)": f"{m:.2f}", "DE (SD)": f"{sd:.2f}", "CV (%)": f"{((sd/m)*100):.2f}",
                "LI (Percentil 2.5)": f"{(m - 1.96*sd):.2f}", "LS (Percentil 97.5)": f"{(m + 1.96*sd):.2f}"
            })
        else:
            tabla_sexo.append({"Variable (Sexo)": s, "N": n, "Mínimo": "0.00", "Máximo": "0.00", "Media (x̄)": "0.00", "DE (SD)": "0.00", "CV (%)": "0.00", "LI": "Muestra insuficiente", "LS": "Muestra insuficiente"})
    st.dataframe(pd.DataFrame(tabla_sexo), use_container_width=True)

    # SECCIÓN 2: EDAD
    st.markdown("#### B. Valores de Referencia según Estratificación por Grupo Etario")
    tabla_edad = []
    for g in grupos_edad_fijos:
        sub = df[df["Grupo_Edad"] == g] if len(df) > 0 else []
        n = len(sub)
        if n >= 2:
            m, sd = sub["Hemoglobina"].mean(), sub["Hemoglobina"].std()
            tabla_edad.append({
                "Variable (Grupo Etario)": g, "N": n, "Mínimo": f"{sub['Hemoglobina'].min():.2f}", "Máximo": f"{sub['Hemoglobina'].max():.2f}",
                "Media (x̄)": f"{m:.2f}", "DE (SD)": f"{sd:.2f}", "CV (%)": f"{((sd/m)*100):.2f}",
                "LI (Percentil 2.5)": f"{(m - 1.96*sd):.2f}", "LS (Percentil 97.5)": f"{(m + 1.96*sd):.2f}"
            })
        else:
            tabla_edad.append({"Variable (Grupo Etario)": g, "N": n, "Mínimo": "0.00", "Máximo": "0.00", "Media (x̄)": "0.00", "DE (SD)": "0.00", "CV (%)": "0.00", "LI": "Muestra insuficiente", "LS": "Muestra insuficiente"})
    st.dataframe(pd.DataFrame(tabla_edad), use_container_width=True)

# --- TAB 4: VALIDACIÓN ---
with tabs[3]:
    st.markdown("### 🔬 Controles de Normalidad Muestral")
    if len(df) >= 3:
        for s in ["Masculino", "Femenino"]:
            data = df[df["Sexo"]==s]["Hemoglobina"]
            if len(data) >= 3:
                z = (data - data.mean()) / (data.std() if data.std() > 0 else 1)
                stat, p = kstest(z, 'norm')
                st.write(f"Análisis Normalidad {s} → **p-valor:** `{p:.4f}`")
                if p > 0.05: st.success(f"✔️ Segmento {s} sigue una distribución normal.")
                else: st.error(f"❌ Segmento {s} requiere ampliar tamaño muestral.")
    else:
        st.info("Datos analíticos reducidos para ejecutar Kolmogorov-Smirnov.")

# --- TAB 5: GRÁFICOS TERMINADOS PROFESIONALMENTE (SEXO Y EDAD) ---
with tabs[4]:
    st.markdown("### 📈 Modelado Gráfico y Curvas de Ajuste Clínico")
    
    if len(df) >= 2:
        # 1. CAMPANAS DE GAUSS POR SEXO
        st.markdown("#### 1. Campanas de Gauss Normalizadas por Variable Sexo")
        c_sex1, c_sex2 = st.columns(2)
        
        with c_sex1:
            m_f = df[df["Sexo"] == "Femenino"]["Hemoglobina"]
            if len(m_f) >= 2:
                media, sd = m_f.mean(), m_f.std()
                li, ls = media - 1.96*sd, media + 1.96*sd
                x = np.linspace(media - 3.5*sd, media + 3.5*sd, 200)
                
                fig, ax = plt.subplots(figsize=(6, 3.8))
                ax.hist(m_f, bins=6, density=True, alpha=0.2, color="#db2777")
                ax.plot(x, norm.pdf(x, media, sd), linewidth=2.5, color="#db2777", label="Campana de Gauss")
                ax.axvline(media, linestyle="-", color="#475569", label=f"Media: {media:.2f}")
                ax.axvline(li, linestyle="--", color="#b91c1c", label=f"LI: {li:.2f}")
                ax.axvline(ls, linestyle="--", color="#b91c1c", label=f"LS: {ls:.2f}")
                ax.fill_between(x, norm.pdf(x, media, sd), where=((x >= li) & (x <= ls)), alpha=0.06, color="#db2777")
                ax.set_title(f"Distribución Femenina (n={len(m_f)}) | SD: {sd:.2f} | CV: {((sd/media)*100):.2f}%", fontsize=9, weight="bold")
                ax.set_xlabel("Hemoglobina (g/dL)")
                ax.legend(fontsize=8, loc="upper right")
                st.pyplot(fig)
            else: st.info("Insuficientes datos femeninos.")
            
        with c_sex2:
            m_m = df[df["Sexo"] == "Masculino"]["Hemoglobina"]
            if len(m_m) >= 2:
                media, sd = m_m.mean(), m_m.std()
                li, ls = media - 1.96*sd, media + 1.96*sd
                x = np.linspace(media - 3.5*sd, media + 3.5*sd, 200)
                
                fig, ax = plt.subplots(figsize=(6, 3.8))
                ax.hist(m_m, bins=6, density=True, alpha=0.2, color="#1e3a8a")
                ax.plot(x, norm.pdf(x, media, sd), linewidth=2.5, color="#1e3a8a", label="Campana de Gauss")
                ax.axvline(media, linestyle="-", color="#475569", label=f"Media: {media:.2f}")
                ax.axvline(li, linestyle="--", color="#1e3a8a", label=f"LI: {li:.2f}")
                ax.axvline(ls, linestyle="--", color="#1e3a8a", label=f"LS: {ls:.2f}")
                ax.fill_between(x, norm.pdf(x, media, sd), where=((x >= li) & (x <= ls)), alpha=0.06, color="#1e3a8a")
                ax.set_title(f"Distribución Masculina (n={len(m_m)}) | SD: {sd:.2f} | CV: {((sd/media)*100):.2f}%", fontsize=9, weight="bold")
                ax.set_xlabel("Hemoglobina (g/dL)")
                ax.legend(fontsize=8, loc="upper right")
                st.pyplot(fig)
            else: st.info("Insuficientes datos masculinos.")

        # 2. CAMPANAS DE GAUSS POR RANGOS DE EDAD
        st.markdown("#### 2. Campanas de Gauss según Estratificación por Edad")
        c_ed1, c_ed2 = st.columns(2)
        
        for idx, g in enumerate(grupos_edad_fijos[:4]):
            sub_g = df[df["Grupo_Edad"] == g]["Hemoglobina"]
            col_destino = c_ed1 if idx % 2 == 0 else c_ed2
            
            with col_destino:
                if len(sub_g) >= 2:
                    media, sd = sub_g.mean(), sub_g.std()
                    li, ls = media - 1.96*sd, media + 1.96*sd
                    x = np.linspace(media - 3.5*sd, media + 3.5*sd, 200)
                    
                    fig, ax = plt.subplots(figsize=(6, 3.2))
                    ax.hist(sub_g, bins=5, density=True, alpha=0.15, color="#0f766e")
                    ax.plot(x, norm.pdf(x, media, sd), linewidth=2, color="#0f766e")
                    ax.axvline(media, linestyle="-", color="#64748b", label=f"Media: {media:.2f}")
                    ax.axvline(li, linestyle="--", color="#0f766e", label=f"LI: {li:.2f}")
                    ax.axvline(ls, linestyle="--", color="#0f766e", label=f"LS: {ls:.2f}")
                    ax.set_title(f"{g} (n={len(sub_g)}) | SD: {sd:.2f}", fontsize=9, weight="bold")
                    ax.set_xlabel("Hemoglobina (g/dL)")
                    ax.legend(fontsize=7)
                    st.pyplot(fig)
                else:
                    st.caption(f"ℹ️ *{g}:* Registros insuficientes para modelar curva normal ajustada.")

        # 3. ACABADO PROFESIONAL DE GRÁFICOS PLOTLY (BARRAS Y DISPERSIÓN DE TESIS)
        st.markdown("#### 3. Análisis Comparativo Estructural (Estadísticos Clínicos)")
        col_p1, col_p2 = st.columns(2)
        
        with col_p1:
            st.markdown("**Comparativa de Medias de Hb por Edad y Sexo**")
            df_bar = df.groupby(["Grupo_Edad", "Sexo"])["Hemoglobina"].mean().reset_index()
            
            # Gráfico de barras con control estricto de la paleta institucional
            fig_bar = px.bar(
                df_bar, x="Grupo_Edad", y="Hemoglobina", color="Sexo", 
                barmode="group", text_auto=".2f",
                color_discrete_map=COLOR_MAP,
                category_orders={"Grupo_Edad": grupos_edad_fijos}
            )
            fig_bar.update_layout(
                xaxis_title="Segmentos Etarios", yaxis_title="Media de Hemoglobina (g/dL)",
                legend_title="Sexo", margin=dict(l=20, r=20, t=10, b=20),
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)"
            )
            fig_bar.update_xaxes(showgrid=True, gridcolor="#e2e8f0")
            fig_bar.update_yaxes(showgrid=True, gridcolor="#e2e8f0")
            st.plotly_chart(fig_bar, use_container_width=True)
            
        with col_p2:
            st.markdown("**Variabilidad Individual General (Dispersión de Muestras)**")
            
            # Gráfico de dispersión puro por puntos (Evita líneas quebradas erróneas en las tendencias)
            fig_scatter = px.scatter(
                df, x="Edad", y="Hemoglobina", color="Sexo",
                color_discrete_map=COLOR_MAP,
                hover_data=["Grupo_Edad"]
            )
            fig_scatter.update_traces(marker=dict(size=10, opacity=0.85, line=dict(width=1, color="White")))
            fig_scatter.update_layout(
                xaxis_title="Edad Cronológica (Años)", yaxis_title="Hemoglobina Medida (g/dL)",
                legend_title="Sexo", margin=dict(l=20, r=20, t=10, b=20),
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)"
            )
            fig_scatter.update_xaxes(showgrid=True, gridcolor="#e2e8f0")
            fig_scatter.update_yaxes(showgrid=True, gridcolor="#e2e8f0")
            st.plotly_chart(fig_scatter, use_container_width=True)
            
    else:
        st.info("Almacene al menos dos muestras en el sistema para renderizar la pestaña de gráficos.")

# --- TAB 6: BASE DE DATOS ---
with tabs[5]:
    st.markdown("### 🗃️ Base de Datos Histórica (Auditoría Excel)")
    st.dataframe(df, use_container_width=True)
    if st.button("🗑️ ELIMINAR ÚLTIMO REGISTRO CAPTURADO"):
        if len(df) > 0:
            df = df.drop(df.index[-1])
            df.to_excel("datos_investigacion.xlsx", index=False)
            st.success("Último paciente removido del archivo de almacenamiento.")
            st.rerun()