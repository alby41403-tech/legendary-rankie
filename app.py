import pandas as pd
import streamlit as st
import traceback

st.set_page_config(
    page_title="Self-Healing Nursing Rank List",
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
    div.stButton > button {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
        padding: 0.75rem 1rem !important;
        border: 2px solid #DC2626 !important;
        width: 100% !important;
    }
    div.stButton > button:hover {
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
    .healing-banner {
        background-color: #F0FDF4;
        border: 1px solid #22C55E;
        color: #166534;
        padding: 10px;
        border-radius: 6px;
        margin-bottom: 15px;
        font-size: 0.85rem;
    }
    </style>
""",
    unsafe_allow_html=True,
)

if "selected_view" not in st.session_state:
    st.session_state.selected_view = None

st.markdown(
    '<div class="main-header">🩺 Self-Healing Nursing Rank List</div>', unsafe_allow_html=True
)

CSV_URL = "https://raw.githubusercontent.com/alby41403-tech/legendary-rankie/refs/heads/main/j_msyjho6h2bi8surb3b.csv"

# Autonomous Self-Healing Pipeline Engine
@st.cache_data
def self_healing_data_pipeline(url):
    healing_actions = []
    try:
        df = pd.read_csv(url)
    except Exception as e:
        healing_actions.append(f"Critical load failure from source: {e}. Falling back to default synthetic schema.")
        # Fallback schema self-healing wrapper
        df = pd.DataFrame(columns=["Application No", "Name", "Board", "Biology", "Physics", "Chemistry", "Status"])

    # Clean column spacing
    df.columns = df.columns.str.strip()

    # Self-healing mapping for structural schema deviations
    col_map = {}
    expected_targets = {"Biology": "bio", "Physics": "phy", "Chemistry": "chem", "Application No": "app", "Name": "name", "Board": "board", "Status": "status"}
    
    for col in df.columns:
        c_lower = col.lower()
        for target, keyword in expected_targets.items():
            if keyword in c_lower and target not in col_map.values():
                col_map[col] = target

    if col_map:
        df = df.rename(columns=col_map)

    # Auto-patch missing core columns dynamically
    for target in ["Application No", "Name", "Board", "Biology", "Physics", "Chemistry", "Status"]:
        if target not in df.columns:
            healing_actions.append(f"Auto-patched missing structural column: '{target}' initialized with safe defaults.")
            if target in ["Biology", "Physics", "Chemistry"]:
                df[target] = 0.0
            elif target == "Status":
                df[target] = "Accepted"
            else:
                df[target] = "N/A"

    # Self-healing parser for messy or concatenated mark records
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
        df[col] = df[col].apply(parse_and_normalize_mark).fillna(0).round(2)

    df["Calculated_Index_Mark"] = (
        df["Physics"] + df["Chemistry"] + df["Biology"]
    ).round(2)
    
    df = df.sort_values(
        by="Calculated_Index_Mark", ascending=False
    ).reset_index(drop=True)
    
    df["S. No"] = range(1, len(df) + 1)
    return df, healing_actions

with st.spinner("Executing autonomous self-healing data pipeline..."):
    df, logs = self_healing_data_pipeline(CSV_URL)

# Display real-time self-healing audit logs for hackathon transparency
if logs:
    with st.expander("🛡️ Autonomous Self-Healing Audit Trail (Active Patches)", expanded=False):
        for log in logs:
            st.markdown(f"- 🔧 {log}")

if df is not None:
    if st.session_state.selected_view is None:
        st.markdown(
            '<div style="text-align: center; font-weight: 600; margin-bottom: 15px;">Please select a category below to view the respective applicant list:</div>',
            unsafe_allow_html=True,
        )
        
        col1, col2 = st.columns(2, gap="medium")
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
            st.markdown("## 📋 Accepted & Pending Applicants Rank List")
            st.markdown(
                """
                <div class="legend-box">
                    <strong>🔴 Color Legend Notice:</strong> Rows highlighted in <span style="color: #DC2626; font-weight: bold;">Soft Red</span> indicate applicants whose status is currently <strong>Pending</strong>.
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
                st.success(f"Found {len(filtered_search)} matching record(s).")
                display_df = filtered_search
            else:
                st.warning("No matching records found under this category.")
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
            
