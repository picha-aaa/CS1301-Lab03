import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)


def build_gemini_prompt(row, audience, location):
    loc_text = location.strip() if location else "Earth in general"

    name = row["name"]
    date_str = row["date"]
    avg_diameter_km = row["avg_diameter_km"]
    miss_lunar = row["miss_distance_lunar"]
    miss_km = row["miss_distance_km"]
    velocity = row["relative_velocity_km_s"]
    hazardous = row["is_potentially_hazardous"]
    risk_score = row["risk_score"]

    if risk_score < 20:
        risk_label = "Very Low"
    elif risk_score < 40:
        risk_label = "Low"
    elif risk_score < 60:
        risk_label = "Moderate"
    elif risk_score < 80:
        risk_label = "High"
    else:
        risk_label = "Very High"

    prompt = f"""You are an expert NASA science communicator.
                Explain the real-world risk of this near-Earth asteroid to a {audience.lower()} audience
                in clear, accurate, and calm language.

                Asteroid data:
                - Name: {name}
                - Close approach date: {date_str}
                - Estimated diameter (km): {avg_diameter_km:.3f}
                - Miss distance (lunar distances): {miss_lunar:.3f}
                - Miss distance (km): {miss_km:.0f}
                - Relative velocity (km/s): {velocity:.2f}
                - Flagged as potentially hazardous by NASA NeoWs: {hazardous}
                - Computed risk score (0–100): {risk_score:.1f}
                - Risk label: {risk_label}

                Location of interest: {loc_text}

                In your explanation, please:
                1. Describe how close this really is using everyday comparisons (for example, compare to the distance to the Moon).
                2. Explain what the risk score and risk label actually mean for people on Earth.
                3. Clearly state whether there is any known impact threat right now based on this data.
                4. Avoid sensational language. Be calm, realistic, and reassuring if the risk is low.

                Length: about 100–150 words.
                """
    return prompt


def call_gemini(prompt):
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Gemini API error: {e}")
        return ""


st.set_page_config(
    page_title="Asteroid Risk Explainer (Phase 3)",
    page_icon="🧠",
)

st.title("🧠 Asteroid Risk Explainer (Phase 3)")
st.caption(
    "Uses the asteroid data and risk scores loaded on the **Asteroid Risk Meter** page "
    "to generate clear explanations with Gemini."
)

df = st.session_state.get("neo_df", None)
start_date = st.session_state.get("neo_start_date", None)
end_date = st.session_state.get("neo_end_date", None)

if df is None or isinstance(df, pd.DataFrame) and df.empty:
    st.error(
        "No asteroid data is loaded yet.\n\n"
        "Please go to the **Asteroid Risk Meter** page and click **Fetch Asteroids 🚀** first."
    )
    st.stop()

if start_date and end_date:
    st.write(f"Using asteroid data from **{start_date}** to **{end_date}**.")


with st.expander("Show asteroid table (preview)"):
    st.dataframe(
        df[
            [
                "name",
                "date",
                "avg_diameter_km",
                "miss_distance_lunar",
                "relative_velocity_km_s",
                "is_potentially_hazardous",
                "risk_score",
            ]
        ].sort_values("risk_score", ascending=False),
        width='stretch',
    )

st.subheader("1️⃣ Select asteroid and audience")

df_sorted = df.sort_values("risk_score", ascending=False).reset_index(drop=True)
option_labels = [
    f"{row['name']} — {row['date']} — Risk: {row['risk_score']:.1f}"
    for _, row in df_sorted.iterrows()
]

selected_label = st.selectbox(
    "Choose an asteroid to generate a risk explanation for:",
    options=option_labels,
)

selected_index = option_labels.index(selected_label)
selected_row = df_sorted.iloc[selected_index]

audience = st.selectbox(
    "Select audience style:",
    ["Kid friendly", "College student level", "Professional"],
)

user_location = st.text_input(
    "Optional: Location of interest (city/region) for context",
    placeholder="e.g., Atlanta, GA or leave blank for Earth in general",
)

st.subheader("2️⃣ Gemini-generated explanation")

if st.button("Generate Explanation with Gemini"):
    prompt = build_gemini_prompt(selected_row, audience, user_location)

    with st.spinner("Asking Gemini to explain this asteroid risk....."):
        explanation = call_gemini(prompt)

    if explanation:
        st.markdown("### Asteroid Risk Briefing")
        st.write(explanation)
