from __future__ import annotations

import pandas as pd
import streamlit as st

from .data_loader import load_radlex
from .matcher import batch_match
from .models import AdjudicationStatus
from .reporter import build_report, results_to_dataframe

st.set_page_config(
    page_title="RadLex Order Harmonizer",
    layout="wide",
)

st.title("RadLex Order Harmonizer")
st.markdown(
    "Map local radiology procedure names to standardized RadLex Playbook identifiers."
)


@st.cache_data
def get_radlex_entries():
    with st.spinner("Downloading RadLex Playbook..."):
        return load_radlex()


entries = get_radlex_entries()
st.sidebar.success(f"Loaded {len(entries)} RadLex entries")

uploaded_file = st.sidebar.file_uploader(
    "Upload CSV with local procedure names",
    type=["csv"],
)

name_column = st.sidebar.text_input("Name column", "local_name")
max_candidates = st.sidebar.slider("Max candidates", 1, 10, 5)
min_score = st.sidebar.slider("Min score", 0.0, 1.0, 0.3)

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    if name_column not in df.columns:
        st.error(f"Column '{name_column}' not found. Available: {list(df.columns)}")
        st.stop()

    local_names = df[name_column].dropna().astype(str).tolist()

    if st.sidebar.button("Run Matching"):
        with st.spinner(f"Matching {len(local_names)} names..."):
            results = batch_match(local_names, entries, max_candidates, min_score)
            results_df = results_to_dataframe(results)

        st.session_state["results"] = results
        st.session_state["results_df"] = results_df

if "results_df" in st.session_state:
    results_df = st.session_state["results_df"]
    results = st.session_state["results"]

    report = build_report(results)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total", report.total)
    col2.metric("Mapped", report.mapped)
    col3.metric("Pending", report.pending)
    col4.metric("Coverage", f"{report.coverage:.1%}")

    st.subheader("Match Results")
    edited_df = st.data_editor(
        results_df,
        column_config={
            "adjudication": st.column_config.SelectboxColumn(
                "Adjudication",
                options=[s.value for s in AdjudicationStatus],
                required=True,
            ),
            "audit_notes": st.column_config.TextColumn("Audit Notes"),
        },
        hide_index=True,
        use_container_width=True,
    )

    if st.button("Export Adjudicated Results"):
        csv_data = edited_df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name="adjudicated_results.csv",
            mime="text/csv",
        )

    st.subheader("Distribution by Strategy")
    strategy_counts = edited_df["selected_strategy"].value_counts()
    st.bar_chart(strategy_counts)

    st.subheader("Score Distribution")
    st.scatter_chart(edited_df, x=edited_df.index, y="selected_score")
