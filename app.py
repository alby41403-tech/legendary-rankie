import pandas as pd
import streamlit as st

# Configure the Streamlit page
st.set_page_config(
    page_title="Nursing Rank List",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom Royal Theme CSS (Black, White, and Red)
st.markdown(
    """
    <style>
    .stApp {
        background-color: #FFFFFF;
        color: #111111;
    }
    .main-header {
        font-size: 2.5rem;
        font-weight: 800;
        color: #000000;
        text-align: center;
        margin-bottom: 2rem;
        border-bottom: 3px solid #DC2626;
        padding-bottom: 1rem;
    }
    .stButton>button {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
        padding: 0.75rem 1.5rem !important;
        border: 2px solid #DC2626 !important;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #DC2626 !important;
        color: #FFFFFF !important;
        border-color: #000000 !important;
    }
    .legend-box {
        background-color: #FEF2F2;
        border-left: 4px solid #DC2626;
        padding: 10px;
        margin-bottom: 15px;
        font-size: 0.9rem;
        color: #7F1D1D;
        border-radius: 4px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

if "selected_view" not in st.session_state:
    st.session_state.selected_view = None

st.markdown(
    '<div class="main-header">🩺 Nursing Rank List</div>', unsafe_allow_html=True
)

CSV_URL = "https://raw.githubusercontent.com/alby41403-tech/legendary-rankie/refs/heads/main/j_msyjho6h2bi8surb3b.csv"


@st.cache_data
def load_and_process_data(url):
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    mark_cols = ["Biology", "Physics", "Chemistry"]
    for col in mark_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df["Converted_Bio"] = (df["Biology"] / 120.0) * 100
    df["Converted_Phy"] = (df["Physics"] / 120.0) * 100
    df["Converted_Chem"] = (df["Chemistry"] / 120.0) * 100

    df["Calculated_Index_Mark"] = (
        df["Converted_Bio"] + df["Converted_Phy"] + df["Converted_Chem"]
    ).round(2)
    df = df.sort_values(
        by="Calculated_Index_Mark", ascending=False
    ).reset_index(drop=True)
    df["S. No"] = range(1, len(df) + 1)
    return df


with st.spinner("Loading and processing national rank list records..."):
    df = load_and_process_data(CSV_URL)

if df is not None:
    status_column_name = None
    for col in df.columns:
        if "status" in col.lower():
            status_column_name = col
            break

    if not status_column_name:
        df["Status"] = "Accepted"

    if st.session_state.selected_view is None:
        st.markdown(
            "### Please select a category below to view the respective applicant list:"
        )
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📋 Accepted / Pending List"):
                st.session_state.selected_view = "Accepted_Pending"
                st.rerun()
        with col2:
            if st.button("❌ Rejected List"):
                st.session_state.selected_view = "Rejected"
                st.rerun()
    else:
        if st.button("⬅ Back to Categories"):
            st.session_state.selected_view = None
            st.rerun()

        if st.session_state.selected_view == "Accepted_Pending":
            st.markdown(
                "## 📋 Accepted & Pending Applicants Rank List (Sorted by Index Mark)"
            )
            st.markdown(
                """
                <div class="legend-box">
                    <strong>🔴 Color Legend Notice:</strong> Rows highlighted in <span style="color: #DC2626; font-weight: bold;">Soft Red</span> indicate applicants whose status is currently <strong>Pending</strong>. Standard rows are fully accepted.
                </div>
            """,
                unsafe_allow_html=True,
            )
            view_df = df[
                df["Status"].astype(str).str.contains("Accept|Pend", case=False, na=False)
            ]
        else:
            st.markdown("## ❌ Rejected Applicants List")
            view_df = df[
                df["Status"].astype(str).str.contains("Reject", case=False, na=False)
            ]

        st.markdown("---")
        search_query = st.text_input(
            "🔍 Enter Application Number to look up specific standing:"
        )

        if search_query:
            filtered_search = view_df[
                view_df["Application No"].astype(str).str.contains(search_query, case=False, na=False)
            ]
            if not filtered_search.empty:
                st.success(
                    f"Found {len(filtered_search)} matching record(s) for Application No: {search_query}"
                )
                display_df = filtered_search
            else:
                st.warning(
                    "No matching records found under this category for the given Application Number."
                )
                display_df = view_df
        else:
            display_df = view_df

        st.markdown(f"**Total records displayed:** {len(display_df)}")


        def highlight_pending(row):
            if "pend" in str(row.get("Status", "")).lower():
                return ["background-color: #FEE2E2"] * len(row)
            return [""] * len(row)


        if not display_df.empty:
            columns_to_show = [
                col
                for col in [
                    "S. No",
                    "Application No",
                    "Name",
                    "Board",
                    "Biology",
                    "Physics",
                    "Chemistry",
                    "Calculated_Index_Mark",
                ]
                if col in display_df.columns
            ]
            styled_table = display_df[columns_to_show].style.apply(
                highlight_pending, axis=1
            )
            st.dataframe(styled_table, use_container_width=True, hide_index=True)
        else:
            st.info("No records available in this view.")
            
          
