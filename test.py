import streamlit as st
import pandas as pd
from databricks import sql

st.set_page_config(page_title="Client Classification", layout="wide")

@st.cache_data(ttl=600)
def classify_clients():
    # Connect to Databricks SQL
    conn = sql.connect(
        server_hostname=st.secrets["DATABRICKS_HOST"],
        http_path=st.secrets["DATABRICKS_HTTP_PATH"],
        access_token=st.secrets["DATABRICKS_TOKEN"]
    )

    # SQL Query using ai_generate_text()
    query = """
    SELECT
      name_account,
      industry_account,
      billingcountry_account,
      ai_generate_text(
        'Classify the following client. '
        || 'Name: ' || name_account || ', '
        || 'Industry: ' || industry_account || ', '
        || 'Country: ' || billingcountry_account || '. '
        || 'Classify as one of: High Potential, At Risk, Low Engagement.',
        'databricks-dbrx-instruct'
      ) AS classification
    FROM clientdetails
    WHERE name_account IS NOT NULL AND industry_account IS NOT NULL
    LIMIT 25
    """

    return pd.read_sql(query, conn)

def main():
    st.title("🤖 LLM-Powered Client Classification")

    with st.spinner("Querying Databricks and classifying clients..."):
        df = classify_clients()

    st.success("Classification complete!")
    st.dataframe(df, use_container_width=True)

    st.markdown("### 📊 Industry-wise Classification")
    grouped = df.groupby(['industry_account', 'classification']).size().reset_index(name="Count")
    st.bar_chart(grouped.pivot(index="industry_account", columns="classification", values="Count").fillna(0))

if __name__ == "__main__":
    main()
