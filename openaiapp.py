import openai

openai.api_key = st.secrets["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"]

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
