import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk
import json

# Fayllarni yuklash
tadbirkorlar = pd.read_csv("tadbirkorlar_royxati.csv")
baholash = pd.read_csv("baholash_korsatkichlari.csv")
mezonlar = pd.read_csv("mezonlar.csv")
tekshiruvlar = pd.read_csv("tekshiruvlar.csv")

# Viloyat koordinatalari
viloyat_koordinatalari = {
    "Toshkent": (41.3111, 69.2797),
    "Andijon": (40.7821, 72.3442),
    "Farg'ona": (40.3894, 71.7876),
    "Namangan": (41.0058, 71.6436),
    "Buxoro": (39.7747, 64.4286),
    "Navoiy": (40.1039, 65.3689),
    "Samarqand": (39.6270, 66.9749),
    "Qashqadaryo": (38.8333, 66.2500),
    "Surxondaryo": (37.9400, 67.5700),
    "Jizzax": (40.1250, 67.8800),
    "Sirdaryo": (40.8400, 68.6600),
    "Xorazm": (41.5500, 60.6333),
    "Qoraqalpog‘iston": (43.7683, 59.0021),
}

tekshiruvlar['Latitude'] = tekshiruvlar['Viloyat'].map(lambda x: viloyat_koordinatalari.get(x, (None, None))[0])
tekshiruvlar['Longitude'] = tekshiruvlar['Viloyat'].map(lambda x: viloyat_koordinatalari.get(x, (None, None))[1])

st.set_page_config(page_title="Xavf Tahlil Dashboard", layout="wide")
st.title("Xavf Tahlil Dashboard")

# --- Sidebar filtrlar ---
st.sidebar.header("Filtrlar")
selected_region = st.sidebar.selectbox("Viloyat", ["Barchasi"] + sorted(tadbirkorlar["Viloyat"].dropna().unique().tolist()))
selected_tashkilot = st.sidebar.selectbox("Tashkilot nomi", ["Barchasi"] + sorted(tadbirkorlar["Tashkilot_nomi"].dropna().unique().tolist()))

# --- Filtrlash ---
filtered_tekshiruvlar = tekshiruvlar.copy()
if selected_region != "Barchasi":
    filtered_tekshiruvlar = filtered_tekshiruvlar[filtered_tekshiruvlar["Viloyat"] == selected_region]
if selected_tashkilot != "Barchasi":
    filtered_tekshiruvlar = filtered_tekshiruvlar[filtered_tekshiruvlar["Tashkilot_nomi"] == selected_tashkilot]

# --- Vizualizatsiyalar ---
st.subheader("Tekshiruvlar statistikasi")
col1, col2 = st.columns(2)

with col1:
    fig = px.histogram(
        filtered_tekshiruvlar,
        x="Xavf_darajasi",
        color="Xavf_darajasi",
        title="Xavf darajalari taqsimoti",
        text_auto=True,
    )
    fig.update_layout(height=400, title_x=0.5)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig2 = px.pie(
        filtered_tekshiruvlar,
        names="Tekshiruvchi_organ",
        title="Tekshiruvchi organlar nisbati",
        hole=0.4
    )
    fig2.update_traces(textposition="inside", textinfo="percent+label")
    fig2.update_layout(height=400, title_x=0.5)
    st.plotly_chart(fig2, use_container_width=True)

# --- Viloyat bo‘yicha statistikasi ---
st.subheader("Viloyatlar bo‘yicha tekshiruvlar soni")
region_counts = filtered_tekshiruvlar["Viloyat"].value_counts().reset_index()
region_counts.columns = ["Viloyat", "Tekshiruvlar_soni"]

fig_region = px.bar(
    region_counts,
    x="Viloyat",
    y="Tekshiruvlar_soni",
    text_auto=True,
    color="Tekshiruvlar_soni",
    title="Viloyatlar kesimida tekshiruvlar statistikasi"
)
fig_region.update_layout(height=400, title_x=0.5)
st.plotly_chart(fig_region, use_container_width=True)

# --- Mezonlar holati ---
st.subheader("Mezonlar holati")
mezonlar_counts = mezonlar["Holat"].value_counts().reset_index(name="Soni")
mezonlar_counts.columns = ["Holat", "Soni"]

fig3 = px.bar(
    mezonlar_counts,
    x="Holat",
    y="Soni",
    labels={"Holat": "Holat", "Soni": "Soni"},
    title="Mezonlar holati soni",
    text_auto=True,
    color="Holat",
)
fig3.update_layout(height=400, title_x=0.5)
st.plotly_chart(fig3, use_container_width=True)

# --- Tadbirkorlar xavf darajasi ---
st.subheader("Tadbirkorlar xavf darajasi")
tadbirkorlar_count = tadbirkorlar["Xavf_darajasi"].value_counts().reset_index(name='count')
tadbirkorlar_count.columns = ['Xavf_darajasi', 'count']

fig4 = px.bar(
    tadbirkorlar_count,
    x='Xavf_darajasi',
    y='count',
    labels={'Xavf_darajasi': 'Xavf darajasi', 'count': 'Tadbirkorlar soni'},
    color='Xavf_darajasi',
    text_auto=True,
    title="Tadbirkorlar xavf darajasi bo'yicha taqsimoti",
)
fig4.update_layout(height=400, title_x=0.5)
st.plotly_chart(fig4, use_container_width=True)

# --- Xarita (tekshiruv joylari) ---
if st.checkbox("Ko'rsatish: Tekshiruvlar xaritada"):
    geo_df = tekshiruvlar.dropna(subset=['Latitude', 'Longitude'])
    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v9',
        initial_view_state=pdk.ViewState(
            latitude=geo_df["Latitude"].mean(),
            longitude=geo_df["Longitude"].mean(),
            zoom=6,
            pitch=0,
        ),
        layers=[
            pdk.Layer(
                "ScatterplotLayer",
                data=geo_df,
                get_position='[Longitude, Latitude]',
                get_color='[200, 30, 0, 160]',
                get_radius=5000,
            ),
        ],
    ))

# --- AI bo‘limi uchun joy ---
st.markdown("---")
st.subheader("AI & Skoring bo'limi")
st.info("Bu joy kelajakda AI model asosida xavf skoring, tavsiya va prediktsiya uchun kengaytiriladi.")

expected = [
    "Toshkent viloyati", "Toshkent sh.", "Andijon viloyati", "Fargʻona viloyati", "Namangan viloyati",
    "Buxoro viloyati", "Samarqand viloyati", "Sirdaryo viloyati", "Jizzax viloyati",
    "Qashqadaryo viloyati", "Surxondaryo viloyati", "Navoiy viloyati", "Xorazm viloyati",
    "Qoraqalpogʻiston Respublikasi"
]


