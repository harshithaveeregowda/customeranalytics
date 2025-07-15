from io import BytesIO

import streamlit as st
import pandas as pd
from fuzzywuzzy import fuzz

st.set_page_config(layout="wide")

# Inject CSS to left-align the tabs
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] {
        justify-content: flex-start;
    }
    </style>
    """, unsafe_allow_html=True)

# ----------------- Sidebar Uploaders -----------------
st.sidebar.header("📁 Upload Excel Files")

account_file = st.sidebar.file_uploader("Materna-cbs Export", type=["xlsx", "xls"], key="Account")
market_file = st.sidebar.file_uploader("Market Accounts Export", type=["xlsx", "xls"], key="Market")

# ✅ Ensure both files are uploaded before proceeding
if account_file is not None and market_file is not None:
    market_df = pd.read_excel(market_file, sheet_name="Analytics_CH Tech & Hook", skiprows=9)
    # Rename first column (index 0)
    market_df.rename(columns={market_df.columns[0]: "ClientName"}, inplace=True)

    market_df = market_df[["ClientName","Sales Stage 1 to 6","Tech Stack (WiP --> Installed Base)","Specific Recommended Hook (THW, 02.07.2025)","Former Contacts (CMC)","Former Contacts (IFM)"]]

    account_df = pd.read_excel(account_file, sheet_name="Account")
    contact_df = pd.read_excel(account_file, sheet_name="Contact")
    opp_df = pd.read_excel(account_file, sheet_name="Opportunity")

    account_df = account_df[["Id", "Name", "Industry", "Industry_Cluster_cbs__c", "Description", "Type","IsDeleted","BillingCountryCode","Website", "LastModifiedDate", "AccountSource", "SAP_ERP_Systeme__c", "Regionale_Sicht__c", "cbs_CommProjectAssistant__c","Konkurrenz__c"]]
    contact_df = contact_df[["Id", "Description", "AccountId", "Name","LastName","FirstName", "Title", "Email", "Phone", "Bewertung__c", "Zust_ndigkeit__c", "Funktion__c"]]
    opp_df = opp_df[["Id", "AccountId", "Name", "Description","StageName","Amount","CurrencyIsoCode", "TotalOpportunityQuantity", "Probability","CloseDate", "Type","LeadSource","IsClosed","IsWon","Win_Loss_Begr_ndung__c","Win_Loss_Bemerkungen__c","Portfolio_Thema__c","Bearbeiter_ist_Shared_User_aus_Gruppe__c","Bearbeiter_Name__c","Projektbeginn__c","Projektende__c","cbs_Landesgesellschaft__c","Projekttyp__c","Position_Vertriebstrichter__c","Letzte_Position_im_Trichter_gepr_ft__c","LastStageChangeDate","cbs_Bid_Manager__c"]]

    #acc_map_df = account_df.merge(contact_df, left_on="Id", right_on="AccountId", how="left").merge(opp_df, left_on="AccountId", right_on="AccountId", how="left")
    #st.write(acc_map_df)

    # Optional: strip whitespace to help with matching
    market_df["ClientName"] = market_df["ClientName"].str.strip()
    account_df["Name"] = account_df["Name"].str.strip()

    mapping_df = pd.read_csv("mapping.csv")
    # Check mapping column names
    # Strip and normalize whitespace in mapping
    mapping_df['Original'] = mapping_df['Original'].astype(str).str.strip().str.replace(r'\s+', ' ', regex=True)
    mapping_df['Standardized'] = mapping_df['Standardized'].astype(str).str.strip().str.replace(r'\s+', ' ', regex=True)

    # Create mapping dictionary
    mapping_dict = dict(zip(mapping_df['Original'], mapping_df['Standardized']))

    # Clean ClientName column in market_df before applying mapping
    market_df['ClientName'] = market_df['ClientName'].astype(str).str.strip().str.replace(r'\s+', ' ', regex=True)

    # Apply mapping
    market_df['ClientName'] = market_df['ClientName'].replace(mapping_dict)

    # Function to find substring match
    def find_match(client_name):
        for acc_name in account_df["Name"].dropna():
            if client_name.lower() in acc_name.lower() or acc_name.lower() in client_name.lower():
                return acc_name
        return None


    # Add a column to market_df with the matched account name
    market_df["MatchedAccountName"] = market_df["ClientName"].apply(find_match)

    # Merge market_df with account_df using the matched name
    merged_df = pd.merge(
        market_df,
        account_df,
        how="left",
        left_on="MatchedAccountName",
        right_on="Name"
    )

    # Optional: Drop the temporary matched column
    merged_df = merged_df.drop(columns=["MatchedAccountName"])

    # Optional: Reorder columns to bring 'ClientName' and 'Name' to the front
    cols = list(merged_df.columns)
    for col in reversed(["ClientName", "Name"]):  # Reverse to preserve order
        if col in cols:
            cols.insert(0, cols.pop(cols.index(col)))
    merged_df = merged_df[cols]


    # Join df with account_df on AccountId = Id
    joined_df = pd.merge(
        merged_df,
        contact_df,
        left_on='Id',
        right_on='AccountId',
        how='left'
    )
    # Select only required columns
    joined_df = joined_df.drop(columns=['Id_y'])

    # Join df with account_df on AccountId = Id
    joined_df = pd.merge(
        joined_df,
        opp_df,
        left_on='AccountId',
        right_on='AccountId',
        how='left'
    )
    # Select only required columns
    #joined_df = joined_df.drop(columns=['Id_y'])

    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Opportunities", "CH-CBS-2025", "Swiss-Opportunity","More CH opp"])
    with tab1:
        # Streamlit display
        st.subheader("Opportunities for 2025")
        st.dataframe(joined_df, use_container_width=True)
    # --- Tab 2: Column selection
    with tab2:
        st.subheader("Choose Columns to View")
        columns_to_show = st.multiselect("Select columns to display:", joined_df.columns.tolist(), default=joined_df.columns.tolist())
        filtered_df_2 = joined_df[columns_to_show]
        st.dataframe(filtered_df_2, use_container_width=True)
    with tab3:
        st.subheader("Opportunities for 2025")
        joined_df = joined_df[["Name_x", "Website","Industry","Description_x","TotalOpportunityQuantity","CloseDate", "Type_x"]]
        st.dataframe(joined_df, use_container_width=True)
    with tab4:
        # ---------- Clean Whitespace ----------
        market_df["ClientName"] = market_df["ClientName"].astype(str).str.strip().str.replace(r'\s+', ' ', regex=True)
        account_df["Name"] = account_df["Name"].astype(str).str.strip().str.replace(r'\s+', ' ', regex=True)

        # ---------- Mapping ----------
        mapping_df = pd.read_csv("mapping.csv")
        mapping_df['Original'] = mapping_df['Original'].astype(str).str.strip().str.replace(r'\s+', ' ', regex=True)
        mapping_df['Standardized'] = mapping_df['Standardized'].astype(str).str.strip().str.replace(r'\s+', ' ',
                                                                                                    regex=True)
        mapping_dict = dict(zip(mapping_df['Original'], mapping_df['Standardized']))
        market_df['ClientName'] = market_df['ClientName'].replace(mapping_dict)

        st.success("✅ Mapping applied to ClientName successfully!")
        # ---------- Fuzzy Matching Prep ----------
        account_df["Name_cleaned"] = account_df["Name"].astype(str).str.strip().str.replace(r'\s+', ' ', regex=True)
        # ---------- Fuzzy Match Function ----------
        def find_best_account_name(client_name):
            best_score = 0
            best_match = None
            for account_name in account_df["Name_cleaned"]:
                score = fuzz.partial_ratio(client_name.lower(), account_name.lower())
                if score > best_score:
                    best_score = score
                    best_match = account_name
            return best_match

        # ---------- Apply Matching ----------
        market_df["MatchedAccountName"] = market_df["ClientName"].apply(find_best_account_name)
        # ---------- Merge ----------
        merged_df = pd.merge(
            market_df,
            account_df,
            how="left",
            left_on="MatchedAccountName",
            right_on="Name_cleaned"
        )

        # Clean up columns
        merged_df.drop(columns=["MatchedAccountName", "Name_cleaned"], inplace=True)

        st.success("✅ Fuzzy matching and merging completed.")

        # Join df with account_df on AccountId = Id
        joined_df = pd.merge(
            merged_df,
            opp_df,
            left_on='Id',
            right_on='AccountId',
            how='left'
        )
        # Select only required columns
        joined_df = joined_df.drop(columns=['Id_y'])

        # Join df with account_df on AccountId = Id
        joined_df = pd.merge(
            joined_df,
            contact_df,
            left_on='AccountId',
            right_on='AccountId',
            how='left'
        )

        #st.write(joined_df.columns)
        # Define desired order


        st.subheader("🔗 Final Customer Data with Opportunities")
        st.dataframe(joined_df, use_container_width=True)


        # Function to convert DataFrame to Excel in memory
        def to_excel(df):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Sheet1')
            processed_data = output.getvalue()
            return processed_data


        # Convert to Excel
        excel_data = to_excel(joined_df)

        # Download button
        st.download_button(
            label="📥 Download Excel File",
            data=excel_data,
            file_name="2025_ch_opp.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    st.warning("Please upload both the Account and Opportunity Excel files.")
