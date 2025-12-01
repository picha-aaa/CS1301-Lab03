import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai


load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)


def summarize_asteroids_for_prompt(df: pd.DataFrame, max_rows: int) -> str:
    lines = []
    for _, row in df.head(max_rows).iterrows():
        line = (
            f"- {row['name']} | "
            f"date: {row['date']} | "
            f"risk_score: {row['risk_score']:.1f} | "
            f"miss_lunar: {row['miss_distance_lunar']:.2f} LD | "
            f"diameter: {row['avg_diameter_km']:.3f} km | "
            f"hazardous: {row['is_potentially_hazardous']}"
        )
        lines.append(line)

    if not lines:
        return "No asteroids match the current filters."

    return "\n".join(lines)

def call_gemini_chat(asteroid_summary: str, chat_history: str, user_message: str) -> str:
    system_instructions = """
    You are NeoAstroBot, a helpful assistant that explains near-Earth asteroids.
    Use ONLY the asteroid data provided to you.
    Do NOT invent specific impact predictions or guaranteed collisions.
    If the risk appears low, reassure the user calmly and avoid sensational language.
    If a question cannot be answered from the data, say so politely.
    """

    prompt = f"""{system_instructions}

    ASTEROID DATA (from NASA NeoWs and a custom risk score 0–100):
    {asteroid_summary}

    CONVERSATION SO FAR:
    {chat_history}

    USER QUESTION:
    {user_message}

    NeoAstroBot, please respond in a clear paragraph or short list suitable for a general audience.
    """

    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Gemini API error: {e}")
        return ""


st.set_page_config(page_title="NeoAstroBot – Asteroid Chatbot (Phase 4)", page_icon="🛰️")
st.title("🛰️ NeoAstroBot – Asteroid Chatbot (Phase 4)")
st.caption(
    "Chat with a Gemini assistant about near-Earth asteroids "
    "using the NASA NeoWs data loaded on the Asteroid Risk Meter page."
)

df_full = st.session_state.get("neo_df", None)
start_date = st.session_state.get("neo_start_date", None)
end_date = st.session_state.get("neo_end_date", None)

if df_full is None or isinstance(df_full, pd.DataFrame) and df_full.empty:
    st.error(
        "No asteroid data is loaded yet.\n\n"
        "Please go to the **Asteroid Risk Meter** page and click **Fetch Asteroids 🚀** first."
    )
    st.stop()

if start_date and end_date:
    st.write(f"Using asteroid data from **{start_date}** to **{end_date}**.")

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role": "assistant",
            "content": "Hi! I’m NeoAstroBot. Adjust the filters above, then ask me anything about these asteroids.",
        }
    ]

st.subheader("1️⃣ Filter Asteroid Data (affects what the chatbot knows)")

col1, col2 = st.columns(2)
with col1:
    risk_filter = st.selectbox(
        "Risk filter",
        [
            "All asteroids",
            "Moderate+ risk (≥ 40)",
            "High+ risk (≥ 60)",
            "Potentially hazardous only",
        ],
    )
with col2:
    max_asteroids = st.slider(
        "Max asteroids to include in context", min_value=5, max_value=50, value=25, step=5
    )

df = df_full.copy()

if risk_filter == "Moderate+ risk (≥ 40)":
    df = df[df["risk_score"] >= 40]
elif risk_filter == "High+ risk (≥ 60)":
    df = df[df["risk_score"] >= 60]
elif risk_filter == "Potentially hazardous only":
    df = df[df["is_potentially_hazardous"] == True]

if df.empty:
    st.warning("No asteroids match the current filters. Try a different filter.")
else:
    with st.expander("Preview filtered asteroid data"):
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
            width='stretch'
        )

st.markdown("---")

st.subheader("2️⃣ Chat with NeoAstroBot")

for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_prompt = st.chat_input("Type your question about these asteroids here.....")

if user_prompt:
    st.session_state["messages"].append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.write(user_prompt)

    if df.empty:
        bot_reply = (
            "Right now no asteroids match your filters. "
            "Try reducing the risk filter or increasing the max asteroids, then ask again."
        )
    else:
        asteroid_summary = summarize_asteroids_for_prompt(
            df.sort_values("risk_score", ascending=False), max_asteroids
        )

        history_text = ""
        for m in st.session_state["messages"]:
            role = "USER" if m["role"] == "user" else "ASSISTANT"
            history_text += f"{role}: {m['content']}\n"

        bot_reply = call_gemini_chat(asteroid_summary, history_text, user_prompt)
        if not bot_reply:
            bot_reply = "I had a trouble generating a response. Please try again in a later."

    with st.chat_message("assistant"):
        st.write(bot_reply)

    st.session_state["messages"].append({"role": "assistant", "content": bot_reply})
