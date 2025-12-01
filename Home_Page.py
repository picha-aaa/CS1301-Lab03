import streamlit as st

# Title of App
st.title("Web Development Lab03")

st.set_page_config(
    page_title="Homepage",  
    page_icon="🏠",       
)


# Assignment Data 
# TODO: Fill out your team number, section, and team members

st.header("CS 1301")
st.subheader("Team 88, Web Development - Section D")
st.subheader("Picha Jetsadapattarakul")

st.image("Images/img1.jpg", width='stretch')

# Introduction
# TODO: Write a quick description for all of your pages in this lab below, in the form:
# 1.**Home Page**: Overview of the project with navigation to all asteroid analysis tools.
# 2.**Risk Meter**: Use NASA’s NeoWs API to calculates a risk score and interactive risk score chart.
# 3.**Risk Explainer**: Generates a clear, audience-oriented explanation of an asteroid’s risk using gemini-2.5-flash, based on the same NeoWs data and risk score from Phase 2. 
# 4.**NeoAstroBot**: An interactive chatbot powered by gemini-2.5-flash that answers user questions about near-Earth asteroids using filtered NeoWs data, risk scores, and conversational memory.

st.write("""
Welcome to my Streamlit Web Development Lab03 app! You can navigate between the pages using the sidebar to the left. The following pages are:

1.**Home Page**: Overview of the project with navigation to all asteroid analysis tools.\n
2.**Risk Meter**: Use NASA’s NeoWs API to calculates a risk score and interactive risk score chart.\n
3.**Risk Explainer**: Generates a clear, audience-oriented explanation of an asteroid’s risk using gemini-2.5-flash, based on the same NeoWs data and risk score. \n
4.**NeoAstroBot**: An interactive chatbot powered by gemini-2.5-flash that answers user questions about near-Earth asteroids using filtered NeoWs data, risk scores, and conversational memory.\n

""")

st.subheader("How to Use This App")

st.markdown("""
**Note:** You musts load asteroid data on the **Risk Meter** page first before using any other page.

1. Go to **Risk Meter** → choose a date and date range → click **Fetch Asteroids** to load NASA data.  
2. Go to **Risk Explainer** → pick an asteroid → generate a Gemini explanation.  
3. Go to **NeoAstroBot** → adjust filters → chat and ask questions about the loaded asteroids.  
""")


