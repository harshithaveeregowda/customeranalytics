import streamlit as st
import pandas as pd
from databricks import sql

st.set_page_config(page_title="Client AI Classification", layout="wide")

@st.cache_data(ttl=600)
def classify_clients():
    conn = sql.connect(
        server_hostname=st.secrets["databricks"]["DATABRICKS_HOST"],
        http_path=st.secrets["databricks"]["DATABRICKS_HTTP_PATH"],
        access_token=st.secrets["databricks"]["DATABRICKS_TOKEN"]
    )

    query = """
    SELECT
      name_account,
      industry_account,
      billingcountry_account,
      ai_generate_text(
        'Classify this client: '
        || 'Name: ' || name_account || ', '
        || 'Industry: ' || industry_account || ', '
        || 'Country: ' || billingcountry_account || '. '
        || 'Classify as: High Potential, At Risk, or Low Engagement.',
        'databricks-dbrx-instruct'
      ) AS classification
    FROM clientdetails
    WHERE name_account IS NOT NULL AND industry_account IS NOT NULL
    LIMIT 50
    """

    return pd.read_sql(query, conn)

def main():
    st.title("🤖 LLM Client Classification (Databricks Native)")

    with st.spinner("Running LLM classification using Databricks..."):
        df = classify_clients()

    st.success("Classification complete!")
    st.dataframe(df, use_container_width=True)

    st.markdown("### 📊 Industry-wise Classification Breakdown")
    grouped = df.groupby(['industry_account', 'classification']).size().reset_index(name="Count")
    pivot_df = grouped.pivot(index="industry_account", columns="classification", values="Count").fillna(0)
    st.bar_chart(pivot_df)

if __name__ == "__main__":
    main()
