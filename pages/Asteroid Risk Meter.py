import streamlit as st
import requests
import pandas as pd
from datetime import date, timedelta
import os
from dotenv import load_dotenv


load_dotenv()
NASA_API_KEY = os.getenv("API_KEY")

def fetch_neow_data(start: date, end: date):
    url = "https://api.nasa.gov/neo/rest/v1/feed"
    
    param = {
        "start_date": start,
        "end_date": end,
        "api_key": NASA_API_KEY,
    }
    
    resp = requests.get(url, params=param)
    return resp.json()

def build_neow_dataframe(raw_json):
    record = []

    neo_by_date = raw_json.get("near_earth_objects", {})
    
    for day, neos in neo_by_date.items():
        for neo in neos:
            
            name = neo.get("name", "Unknown")
            danger = neo.get("is_potentially_hazardous_asteroid", False)

            ca_data = neo.get("close_approach_data", [])
            ca = ca_data[0]
            
            est_dia = neo["estimated_diameter"]["kilometers"]
            dia_min_km = float(est_dia["estimated_diameter_min"])
            dia_max_km = float(est_dia["estimated_diameter_max"])
            avg_dia_km = (dia_min_km + dia_max_km) / 2

            record.append(
                {
                    "name": name,
                    "date": day,
                    "avg_diameter_km": avg_dia_km,
                    "dia_min_km": dia_min_km,
                    "dia_max_km": dia_max_km,
                    "miss_distance_km": float(ca["miss_distance"]["kilometers"]),
                    "miss_distance_lunar": float(ca["miss_distance"]["lunar"]),
                    "relative_velocity_km_s": float(ca["relative_velocity"]["kilometers_per_second"]),
                    "is_potentially_hazardous": danger,
                }
            )

    return pd.DataFrame(record)


def compute_risk_score(row):
    #Criteria  size = 40%, distance = 30%, velocity = 20%, hazardous = 10%
    
    size = row["avg_diameter_km"]
    dist_lunar = row["miss_distance_lunar"]
    velo = row["relative_velocity_km_s"]
    hazardous = row["is_potentially_hazardous"]
    
    size_comp = min(size * 40, 40)
    
    dist_comp = max(0, (10 - dist_lunar) * 3)

    #20 point at 20 km/s, 0 points at 5km/s
    
    if velo > 20:
        velo_comp = 20
    elif velo > 5: 
        #convert the range from 0-15 to 0-20. multiply with 20/15
        velo_comp = (velo - 5) * (20 / 15) 
    else:
        velo_comp = 0

    if hazardous == True:
        hazard_bonus = 10
    else:
        hazard_bonus = 0

    risk_raw = size_comp + dist_comp + velo_comp + hazard_bonus
    return max(0, min(100, risk_raw))


def risk_level_text(avg_score):
    if avg_score < 20:
        return "Very low risk. All good."
    elif avg_score < 40:
        return "Low risk. NASA is relaxed."
    elif avg_score < 60:
        return "Moderate risk, but nothing serious."
    elif avg_score < 80:
        return "High risk. Worth paying attention."
    else:
        return "Very high risk — but no need to panic."





st.set_page_config(
    page_title="Asteroid Risk Meter", 
    page_icon="☄️")

st.title("☄️ Asteroid Risk Meter")

st.caption("-Uses NASA NeoWs asteroid data, but the risk score calculation might not make sense.\n")
st.caption("-Link for those who want to use this API: https://api.nasa.gov/")

with st.container():
    st.subheader("1️⃣ Choose date range")
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start date", value=date.today())
    with col2:
        day_range = st.slider("Number of days (max 7)", min_value=1, max_value=7, value=3)

end_date = start_date + timedelta(days=day_range - 1)

st.write(f"Fetching asteroid data from **{start_date}** to **{end_date}**")

if st.button("Fetch Asteroids 🚀"):
    with st.spinner("Pulling data from NASA..."):
        try:
            raw_data = fetch_neow_data(start_date, end_date)
            df = build_neow_dataframe(raw_data)
        except Exception as e:
            st.error(f"Error fetching data: {e}")
            st.stop()

    df["risk_score"] = df.apply(compute_risk_score, axis=1)

    st.subheader("2️⃣ Doomsday Summary")
    avg_risk = df["risk_score"].mean()
    max_risk = df["risk_score"].max()

    col1, col2 = st.columns(2)
    col1.metric("Average Risk Score", f"{avg_risk:.1f} / 100")
    col2.metric("Max Risk Score", f"{max_risk:.1f} / 100")

    st.info(risk_level_text(avg_risk))

    with st.container():
        st.subheader("3️⃣ Asteroid Data Table")
        with st.expander("Show asteroid table"):
            st.dataframe(
                df[[
                    
                "name", "date","avg_diameter_km","miss_distance_lunar",
                "relative_velocity_km_s","is_potentially_hazardous","risk_score",
                
                ]].sort_values("risk_score", ascending=False),width="stretch")

    st.subheader("4️⃣ Graph: Risk Score per Asteroid")
    chart_df = df.copy()
    chart_df["label"] = chart_df["name"].str.slice(0, 20) + " (" + chart_df["date"] + ")"
    chart_df = chart_df.sort_values("risk_score", ascending=False)
    chart_df = chart_df.set_index("label")[["risk_score"]]

    st.bar_chart(chart_df)
