import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk

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

# Update coordinates in tekshiruvlar
tekshiruvlar['Latitude'] = tekshiruvlar['Viloyat'].map(lambda x: viloyat_koordinatalari.get(x, (None, None))[0])
tekshiruvlar['Longitude'] = tekshiruvlar['Viloyat'].map(lambda x: viloyat_koordinatalari.get(x, (None, None))[1])

# Streamlit page configuration
st.set_page_config(page_title="Xavf Tahlil Dashboard", layout="wide")
st.title("Xavf Tahlil Dashboard")

# Sidebar filters
st.sidebar.header("Filtrlar")
selected_region = st.sidebar.selectbox("Viloyat", ["Barchasi"] + sorted(tadbirkorlar["Viloyat"].dropna().unique().tolist()))
selected_tashkilot = st.sidebar.selectbox("Tashkilot nomi", ["Barchasi"] + sorted(tadbirkorlar["Tashkilot_nomi"].dropna().unique().tolist()))

# Filter data
filtered_tekshiruvlar = tekshiruvlar.copy()
if selected_region != "Barchasi":
    filtered_tekshiruvlar = filtered_tekshiruvlar[filtered_tekshiruvlar["Viloyat"] == selected_region]
if selected_tashkilot != "Barchasi":
    filtered_tekshiruvlar = filtered_tekshiruvlar[filtered_tekshiruvlar["Tashkilot_nomi"] == selected_tashkilot]

# Visualization: Overall Risk Distribution
st.subheader("Tadbirkorlarning Umumiy Xavf Darajasi")
tadbirkorlar_count = tadbirkorlar["Xavf_darajasi"].value_counts().reset_index()
tadbirkorlar_count.columns = ['Xavf_darajasi', 'count']
fig_risk = px.bar(
    tadbirkorlar_count,
    x='Xavf_darajasi',
    y='count',
    labels={'Xavf_darajasi': 'Xavf darajasi', 'count': 'Tadbirkorlar soni'},
    color='Xavf_darajasi',
    text_auto=True,
    title="Tadbirkorlar xavf darajasi bo'yicha taqsimoti",
    color_discrete_map={'Yuqori': '#ef4444', 'O‘rta': '#f59e0b', 'Past': '#10b981'}
)
fig_risk.update_layout(height=400, title_x=0.5)
st.plotly_chart(fig_risk, use_container_width=True)

# Visualization: Risk Levels by Region
st.subheader("Hududlar bo'yicha Xavf Darajasi")
region_risk = tadbirkorlar.groupby(['Viloyat', 'Xavf_darajasi']).size().unstack(fill_value=0).reset_index()
region_risk_melted = region_risk.melt(id_vars='Viloyat', value_vars=['Yuqori', 'O‘rta', 'Past'], 
                                      var_name='Xavf_darajasi', value_name='Soni')
fig_region_risk = px.bar(
    region_risk_melted,
    x='Viloyat',
    y='Soni',
    color='Xavf_darajasi',
    barmode='stack',
    title="Viloyatlar kesimida xavf darajalari",
    text_auto=True,
    color_discrete_map={'Yuqori': '#ef4444', 'O‘rta': '#f59e0b', 'Past': '#10b981'}
)
fig_region_risk.update_layout(height=400, title_x=0.5, xaxis_tickangle=-45)
st.plotly_chart(fig_region_risk, use_container_width=True)

# Metric: Total Notifications
st.subheader("Jami Habarnomalar")
total_notifications = len(filtered_tekshiruvlar)
st.metric("Umumiy tekshiruvlar soni", total_notifications)

# Note: Inspection Timeliness
st.subheader("Tekshiruvlarning O'z Vaqtida Bajarilishi")
st.info("Ma'lumotlarda tekshiruvlarning berilgan va bajarilgan vaqtlari haqida ma'lumot yo'q. "
        "Agar bu ma'lumotlar mavjud bo'lsa, tekshiruv vaqtlari o'rtasidagi farqni tahlil qilish mumkin.")

# Visualization: Most Used Criteria
st.subheader("Eng Ko'p Ishlatilgan Mezonlar")
mezon_scores = mezonlar[mezonlar['Holat'].isin(['Active', 'Confirmed'])][['Mezon_nomi', 'Score']].sort_values(by='Score', ascending=False).head(5)
fig_mezo = px.bar(
    mezon_scores,
    x='Mezon_nomi',
    y='Score',
    text_auto=True,
    title="Eng ko'p ishlatilgan mezonlar (bal bo'yicha)",
    color='Score',
    color_continuous_scale='Blues'
)
fig_mezo.update_layout(height=400, title_x=0.5)
st.plotly_chart(fig_mezo, use_container_width=True)

# Original Visualizations: Inspection Statistics
st.subheader("Tekshiruvlar Statistikasi")
col1, col2 = st.columns(2)

with col1:
    fig = px.histogram(
        filtered_tekshiruvlar,
        x="Xavf_darajasi",
        color="Xavf_darajasi",
        title="Xavf darajalari taqsimoti",
        text_auto=True,
        color_discrete_map={'Yuqori': '#ef4444', 'O‘rta': '#f59e0b', 'Past': '#10b981'}
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

# Original Visualization: Inspections by Region
st.subheader("Viloyatlar bo‘yicha tekshiruvlar soni")
region_counts = filtered_tekshiruvlar["Viloyat"].value_counts().reset_index()
region_counts.columns = ["Viloyat", "Tekshiruvlar_soni"]
fig_region = px.bar(
    region_counts,
    x="Viloyat",
    y="Tekshiruvlar_soni",
    text_auto=True,
    color="Tekshiruvlar_soni",
    title="Viloyatlar kesimida tekshiruvlar statistikasi",
    color_continuous_scale='Blues'
)
fig_region.update_layout(height=400, title_x=0.5, xaxis_tickangle=-45)
st.plotly_chart(fig_region, use_container_width=True)

# Original Visualization: Criteria Status
st.subheader("Mezonlar Holati")
mezonlar_counts = mezonlar["Holat"].value_counts().reset_index()
mezonlar_counts.columns = ["Holat", "Soni"]
fig3 = px.bar(
    mezonlar_counts,
    x="Holat",
    y="Soni",
    labels={"Holat": "Holat", "Soni": "Soni"},
    title="Mezonlar holati soni",
    text_auto=True,
    color="Holat"
)
fig3.update_layout(height=400, title_x=0.5)
st.plotly_chart(fig3, use_container_width=True)

# Map Visualization
if st.checkbox("Ko'rsatish: Tekshiruvlar xaritada"):
    geo_df = filtered_tekshiruvlar.dropna(subset=['Latitude', 'Longitude'])
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

# Interesting Fact
st.markdown("---")
st.subheader("Qiziqarli Fakt")
sirdaryo_high_risk = tadbirkorlar[tadbirkorlar['Viloyat'] == 'Sirdaryo']['Xavf_darajasi'].value_counts().get('Yuqori', 0)
st.write(f"Sirdaryo viloyatida yuqori xavf darajasiga ega tadbirkorlar soni ({sirdaryo_high_risk}) "
         "boshqa viloyatlarga nisbatan yuqori, bu esa ushbu hududda qo'shimcha e'tibor talab qilishi mumkin.")

# AI Section Placeholder
st.markdown("---")
st.subheader("AI & Skoring bo'limi")
st.info("Bu joy kelajakda AI model asosida xavf skoring, tavsiya va prediktsiya uchun kengaytiriladi.")
