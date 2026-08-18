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
        padding: 0.75rem 1rem !important;
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

    col_map = {}
    for col in df.columns:
        c_lower = col.lower()
        if "bio" in c_lower and "Biology" not in col_map.values():
            col_map[col] = "Biology"
        elif "phy" in c_lower and "Physics" not in col_map.values():
            col_map[col] = "Physics"
        elif "chem" in c_lower and "Chemistry" not in col_map.values():
            col_map[col] = "Chemistry"
        elif ("app" in c_lower or "application" in c_lower) and "Application No" not in col_map.values():
            col_map[col] = "Application No"
        elif "name" in c_lower and "Name" not in col_map.values():
            col_map[col] = "Name"
        elif "board" in c_lower and "Board" not in col_map.values():
            col_map[col] = "Board"

    df = df.rename(columns=col_map)

    def parse_and_normalize_mark(val):
        s_val = str(val).strip()
        cleaned = "".join([c for c in s_val if c.isdigit() or c == '.'])
        if not cleaned:
            return 0.0
        
        try:
            num = float(cleaned)
        except:
            return 0.0

        str_num = str(int(num)) if num.is_integer() else str(num)
        
        if len(str_num) == 5:
            secured = float(str_num[:2])
            maximum = float(str_num[2:])
            if maximum > 0:
                return (secured / maximum) * 100.0
        elif len(str_num) == 6:
            secured = float(str_num[:3])
            maximum = float(str_num[3:])
            if maximum > 0:
                return (secured / maximum) * 100.0
        elif len(str_num) == 4:
            secured = float(str_num[:2])
            maximum = float(str_num[2:])
            if maximum > 0:
                return (secured / maximum) * 100.0

        if num > 100:
            return (num / 120.0) * 100.0
        return num

    for col in ["Biology", "Physics", "Chemistry"]:
        if col not in df.columns:
            df[col] = 0.0
        else:
            df[col] = df[col].apply(parse_and_normalize_mark).fillna(0).round(2)

    df["Calculated_Index_Mark"] = (
        df["Physics"] + df["Chemistry"] + df["Biology"]
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
            '<div style="text-align: center; font-weight: 600; margin-bottom: 15px;">Please select a category below to view the respective applicant list:</div>',
            unsafe_allow_html=True,
        )
        
        # Side-by-side horizontal option columns
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
            desired_columns = [
                "S. No",
                "Application No",
                "Name",
                "Board",
                "Biology",
                "Physics",
                "Chemistry",
                "Calculated_Index_Mark",
            ]
            columns_to_show = [col for col in desired_columns if col in display_df.columns]
            
            # Highlight pending rows in soft red
            def highlight_pending(row_data):
                idx = row_data.name
                if idx in view_df.index:
                    status_val = str(view_df.loc[idx, "Status"]).lower()
                    if "pend" in status_val:
                        return ["background-color: #FEE2E2"] * len(row_data)
                return [""] * len(row_data)

            try:
                styled_table = display_df[columns_to_show].style.apply(highlight_pending, axis=1)
                st.dataframe(styled_table, use_container_width=True, hide_index=True)
            except Exception:
                st.dataframe(display_df[columns_to_show], use_container_width=True, hide_index=True)
        else:
            st.info("No records available in this view.")
            
