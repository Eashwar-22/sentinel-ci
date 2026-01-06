import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os

# Page Configuration
st.set_page_config(
    page_title="The Gatekeeper Dashboard",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ The Gatekeeper: AI Code Review Stats")
st.markdown("### The Wall of Shame (and Fame)")

# Load review logs
LOG_FILE = "review_logs.jsonl"

def load_data():
    if not os.path.exists(LOG_FILE):
        return None
    
    data = []
    with open(LOG_FILE, 'r') as f:
        for line in f:
            try:
                data.append(json.loads(line))
            except:
                continue
    return pd.DataFrame(data)

df = load_data()

# Handle missing or empty data
if df is None or df.empty:
    st.warning("⚠️ No review logs found yet. Creating dummy data for demo...")
    # Generate dummy data for demonstration
    dummy_data = [
        {"status": "REJECT", "roast": "This code smells like burnt toast.", "issues": ["Print statement found"], "timestamp": "2023-10-01"},
        {"status": "APPROVE", "roast": "Surprisingly adequate.", "issues": [], "timestamp": "2023-10-02"},
        {"status": "REJECT", "roast": "Did a cat walk on your keyboard?", "issues": ["Missing docstring", "Hardcoded password"], "timestamp": "2023-10-03"},
        {"status": "REJECT", "roast": "I have seen better code in a fortune cookie.", "issues": ["Print statement found"], "timestamp": "2023-10-04"},
        {"status": "APPROVE", "roast": "Not terrible.", "issues": [], "timestamp": "2023-10-05"}
    ]
    df = pd.DataFrame(dummy_data)

# Dashboard Visualizations

col1, col2 = st.columns(2)

with col1:
    st.subheader("Pass vs. Fail Rate")
    # Simple count of Approve vs Reject
    fig_pie = px.pie(df, names='status', title='Rejection Ratio', color='status',
                     color_discrete_map={'APPROVE':'#00CC96', 'REJECT':'#EF553B'})
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    st.subheader("Top Crimes (Violations)")
    
    # We need to flatten the 'issues' list to count them
    # Handle cases where 'issues' might be missing or empty
    all_issues = []
    for items in df.get('issues', []):
        if isinstance(items, list):
            all_issues.extend(items)
        elif isinstance(items, str): # Handle legacy string format
            all_issues.append(items)
            
    if all_issues:
        issues_df = pd.DataFrame(all_issues, columns=['Crime'])
        crime_counts = issues_df['Crime'].value_counts().reset_index()
        crime_counts.columns = ['Crime', 'Count']
        
        fig_bar = px.bar(crime_counts, x='Count', y='Crime', orientation='h', title='Most Common Offenses')
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("No crimes recorded yet. Everyone is being good!")

# Roast History
st.markdown("---")
st.subheader("🔥 The Hall of Shame (Recent Roasts)")

# Show last 5 roasts
log_display = df[['timestamp', 'status', 'roast']].tail(5).sort_values(by='timestamp', ascending=False)

for index, row in log_display.iterrows():
    color = "red" if row['status'] == "REJECT" else "green"
    with st.expander(f"{row['status']} - {row['roast'][:50]}..."):
        st.markdown(f"**Verdict:** :{color}[{row['status']}]")
        st.markdown(f"**The Roast:** *\"{row['roast']}\"*")
        st.caption(f"Time: {row.get('timestamp', 'Unknown')}")
