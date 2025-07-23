import streamlit as st
import openai

openai.api_key = st.secrets["openai"]["api_key"]

response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Say hello"}]
)

st.write(response.choices[0].message["content"])


def classify_row(name, industry, country):
    prompt = f"""
    Classify the following client as one of: High Potential, At Risk, Low Engagement.
    Name: {name}, Industry: {industry}, Country: {country}.
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",  # or "gpt-3.5-turbo"
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    return response["choices"][0]["message"]["content"].strip()
