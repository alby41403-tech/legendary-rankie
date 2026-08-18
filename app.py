import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Nursing Rank List",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed",
)

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

    # Carefully rename only unmapped columns by position or safe keywords to prevent duplicates
    new_cols = []
    seen = set()
    for col in df.columns:
        c_lower = col.lower()
        target = col
        if "bio" in c_lower and "Biology" not in seen:
            target = "Biology"
        elif "phy" in c_lower and "Physics" not in seen:
            target = "Physics"
        elif "chem" in c_lower and "Chemistry" not in seen:
            target = "Chemistry"
        elif ("app" in c_lower or "application" in c_lower) and "Application No" not in seen:
            target = "Application No"
        elif "name" in c_lower and "Name" not in seen:
            target = "Name"
        elif "board" in c_lower and "Board" not in seen:
            target = "Board"
        
        # Ensure uniqueness
        base_target = target
        counter = 1
        while target in seen:
            target = f"{base_target}_{counter}"
            counter += 1
        seen.add(target)
        new_cols.append(target)

    df.columns = new_cols

    for col in ["Biology", "Physics", "Chemistry"]:
        if col not in df.columns:
            df[col] = 0.0
        else:
            df[col] = pd.to_numeric(
                df[col].astype(str).str.replace(r"[^\d.]", "", regex=True),
                errors="coerce",
            ).fillna(0)

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
    if "Status" not in df.columns:
        found_status = False
        for col in df.columns:
            if "status" in col.lower():
                df["Status"] = df[col]
                found_status = True
                break
        if not found_status:
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
                ~df["Status"].astype(str).str.contains("Reject", case=False, na=False)
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
            st.dataframe(display_df[columns_to_show], use_container_width=True, hide_index=True)
        else:
            st.info("No records available in this view.")
            
            
