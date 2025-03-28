import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

st.title("🏇 Horse Race Predictor (Streamlit Cloud Version)")
st.write("Paste a race URL from [At The Races](https://www.attheraces.com/racecards)")

race_url = st.text_input("Race URL", value="https://www.attheraces.com/racecard/Southwell/28-March-2025/1640")
go = st.button("Get Predictions")

def scrape_racecard(url):
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.text, "html.parser")

    runners = []
    rows = soup.select(".RC-runnerRow")
    for row in rows:
        try:
            horse_name = row.select_one(".RC-runnerName").text.strip()
            jockey_name = row.select_one(".RC-jockey").text.strip()

            # Get form from span tags containing digits
            form_section = row.select_one(".RC-formFigures")
            form_digits = re.findall(r"\d+", form_section.text.strip()) if form_section else []
            form = "".join(form_digits[-6:]) if form_digits else "N/A"

            runners.append({
                "Horse": horse_name,
                "Jockey": jockey_name,
                "Form": form
            })
        except:
            continue

    return runners

if go and race_url:
    st.info("Fetching race info...")
    try:
        runner_data = scrape_racecard(race_url)
        if not runner_data:
            st.error("No runners found. Try a different URL.")
        else:
            df = pd.DataFrame(runner_data)
            df["Form Score"] = df["Form"].apply(lambda x: sum([int(ch) for ch in x if ch.isdigit()]) if x != "N/A" else 0)
            df = df.sort_values(by="Form Score")
            st.success("Race loaded!")
            st.dataframe(df.reset_index(drop=True))
    except Exception as e:
        st.exception(e)
