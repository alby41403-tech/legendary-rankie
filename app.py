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
    [data-testid="column"] {
        width: 100% !important;
        flex: 100% !important;
        min-width: 100% !important;
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
    .stats-box {
        background-color: #F9FAFB;
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        padding: 12px 18px;
        margin-bottom: 15px;
        text-align: center;
        font-size: 0.95rem;
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

EXPECTED_TARGETS = {
    "Biology": "bio",
    "Physics": "phy",
    "Chemistry": "chem",
    "Application No": "app",
    "Name": "name",
    "Board": "board",
    "Status": "status",
}


def parse_and_normalize_mark(val, col_name, row_idx, healing_actions):
    """
    Attempts to interpret a raw mark value as a percentage (0-100).
    Handles plain numbers, percentages already given, and 'secured/max'
    style values that got concatenated into one number (e.g. 85120 ->
    85 out of 120). Any assumption made is logged so it's auditable
    rather than silently guessed.
    """
    raw = val
    s_val = str(val).strip()
    cleaned = "".join(c for c in s_val if c.isdigit() or c == ".")

    if not cleaned:
        healing_actions.append(
            f"Row {row_idx} · {col_name}: empty/unreadable value '{raw}' -> set to 0"
        )
        return 0.0

    try:
        num = float(cleaned)
    except ValueError:
        healing_actions.append(
            f"Row {row_idx} · {col_name}: could not parse '{raw}' -> set to 0"
        )
        return 0.0

    # Already looks like a clean percentage
    if 0 <= num <= 100:
        return round(num, 2)

    # Looks like it might be secured+max concatenated (e.g. 85120, 4550)
    str_num = str(int(num)) if num.is_integer() else str(num)
    digits_only = str_num.replace(".", "")

    if len(digits_only) in (4, 5, 6):
        split_point = len(digits_only) // 2
        secured_str = digits_only[:split_point]
        max_str = digits_only[split_point:]
        try:
            secured = float(secured_str)
            maximum = float(max_str)
            if maximum > 0 and secured <= maximum:
                result = round((secured / maximum) * 100.0, 2)
                healing_actions.append(
                    f"Row {row_idx} · {col_name}: interpreted '{raw}' as "
                    f"{secured}/{maximum} -> {result}%"
                )
                return result
        except ValueError:
            pass

    # Fallback: assume out of 120 (common for combined science papers)
    if num > 100:
        result = round((num / 120.0) * 100.0, 2)
        healing_actions.append(
            f"Row {row_idx} · {col_name}: value '{raw}' > 100, assumed out of "
            f"120 -> {result}%"
        )
        return result

    return round(num, 2)


@st.cache_data(ttl=300)
def self_healing_data_pipeline(url):
    healing_actions = []
    try:
        df = pd.read_csv(url)
    except Exception as e:
        healing_actions.append(f"Critical load failure: {e}")
        df = pd.DataFrame(
            columns=[
                "Application No",
                "Name",
                "Board",
                "Biology",
                "Physics",
                "Chemistry",
                "Status",
            ]
        )
        return df, healing_actions, True  # True = load failed

    df.columns = df.columns.str.strip()

    col_map = {}
    for col in df.columns:
        c_lower = col.lower()
        for target, keyword in EXPECTED_TARGETS.items():
            if keyword in c_lower and target not in col_map.values():
                col_map[col] = target

    if col_map:
        df = df.rename(columns=col_map)

    for target in EXPECTED_TARGETS:
        if target not in df.columns:
            if target in ["Biology", "Physics", "Chemistry"]:
                df[target] = 0.0
            elif target == "Status":
                df[target] = "Accepted"
            else:
                df[target] = "N/A"
            healing_actions.append(f"Column '{target}' was missing -> added with default values")

    for col in ["Biology", "Physics", "Chemistry"]:
        df[col] = [
            parse_and_normalize_mark(v, col, i, healing_actions)
            for i, v in enumerate(df[col], start=1)
        ]
        df[col] = df[col].fillna(0).round(2)

    df["Calculated_Index_Mark"] = (
        df["Physics"] + df["Chemistry"] + df["Biology"]
    ).round(2)

    df = df.sort_values(by="Calculated_Index_Mark", ascending=False).reset_index(drop=True)

    # Tied marks share the same rank (standard for admission rank lists)
    df["S. No"] = df["Calculated_Index_Mark"].rank(method="min", ascending=False).astype(int)

    return df, healing_actions, False


with st.spinner("Loading records..."):
    df, logs, load_failed = self_healing_data_pipeline(CSV_URL)

if load_failed:
    st.error(
        "⚠️ Could not load the applicant data from the source file. "
        "Please check the data source or try again shortly."
    )

if logs:
    with st.expander("🛡️ Data Correction Log", expanded=False):
        st.caption(
            "Every automatic assumption made while cleaning the raw data is listed below."
        )
        for log in logs:
            st.markdown(f"- 🔧 {log}")

if df is not None and not df.empty:
    if st.session_state.selected_view is None:
        st.markdown(
            '<div style="text-align: center; font-weight: 600; margin-bottom: 15px;">'
            "Please select a category below to view the respective applicant list:</div>",
            unsafe_allow_html=True,
        )

        col1 = st.columns(1)[0]
        with col1:
            if st.button("📋 Accepted / Pending List"):
                st.session_state.selected_view = "Accepted_Pending"
                st.rerun()

            st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)

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
                    <strong>🔴 Color Legend Notice:</strong> Entire rows highlighted in
                    <span style="color: #DC2626; font-weight: bold;">Soft Red</span> indicate
                    applicants whose status is currently <strong>Pending</strong>.
                </div>
            """,
                unsafe_allow_html=True,
            )
            view_df = df[~df["Status"].astype(str).str.contains("Reject", case=False, na=False)]
        else:
            st.markdown("## ❌ Rejected Applicants List")
            view_df = df[df["Status"].astype(str).str.contains("Reject", case=False, na=False)]

        # Quick stats
        if not view_df.empty:
            st.markdown(
                f"""
                <div class="stats-box">
                    <strong>{len(view_df)}</strong> applicants &nbsp;|&nbsp;
                    Highest: <strong>{view_df['Calculated_Index_Mark'].max():.2f}</strong> &nbsp;|&nbsp;
                    Lowest: <strong>{view_df['Calculated_Index_Mark'].min():.2f}</strong> &nbsp;|&nbsp;
                    Average: <strong>{view_df['Calculated_Index_Mark'].mean():.2f}</strong>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("---")
        search_query = st.text_input(
            label="",
            placeholder="🔍 Search by application number or name",
        )

        if search_query:
            mask = view_df["Application No"].astype(str).str.contains(
                search_query, case=False, na=False
            ) | view_df["Name"].astype(str).str.contains(search_query, case=False, na=False)
            filtered_search = view_df[mask]
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

            def highlight_pending_row(row):
                status_val = str(row.get("Status", "")).lower()
                if "pend" in status_val:
                    return ["background-color: #FEE2E2; color: #111111;"] * len(row)
                return [""] * len(row)

            # Keep Status available for styling, drop it from the visible columns
            style_source = display_df[columns_to_show + ["Status"]]

            try:
                styled_table = style_source.style.apply(highlight_pending_row, axis=1).hide(
                    axis="columns", subset=["Status"]
                )
                st.dataframe(styled_table, use_container_width=True, hide_index=True)
            except Exception:
                st.dataframe(display_df[columns_to_show], use_container_width=True, hide_index=True)

            st.download_button(
                label="⬇️ Download this list as CSV",
                data=display_df[columns_to_show].to_csv(index=False).encode("utf-8"),
                file_name=f"{st.session_state.selected_view or 'rank_list'}.csv",
                mime="text/csv",
            )
        else:
            st.info("No records available in this view.")
else:
    st.info("No applicant records are currently available.")
