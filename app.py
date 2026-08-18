import pandas as pd
import streamlit as st

# Configure the Streamlit page (must be the first Streamlit command)
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
    /* Global Styles */
    .stApp {
        background-color: #FFFFFF;
        color: #111111;
    }
    
    /* Header Styling */
    .main-header {
        font-size: 2.5rem;
        font-weight: 800;
        color: #000000;
        text-align: center;
        margin-bottom: 2rem;
        border-bottom: 3px solid #DC2626;
        padding-bottom: 1rem;
    }

    /* Interactive Category Buttons / Cards Styling */
    .stButton>button {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
        padding: 0.75rem 1.5rem !important;
        border: 2px solid #DC2626 !important;
        width: 100%;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #DC2626 !important;
        color: #FFFFFF !important;
        border-color: #000000 !important;
    }

    /* Legend Notice Box */
    .legend-box {
        background-color: #FEF2F2;
        border-left: 4px solid #DC2626;
        padding: 10px;
        margin-bottom: 15px;
        font-size: 0.9rem;
        color: #7F1D1D;
        border-radius: 4px;
    }

    /* Pending Row Highlight Style Helper */
    .pending-row {
        background-color: #FEE2E2 !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Session state initialization to handle page navigation
if "selected_view" not in st.session_state:
    st.session_state.selected_view = None

# Main Title with Stethoscope Emoji
st.markdown(
    '<div class="main-header">🩺 Nursing Rank List</div>', unsafe_allow_html=True
)

# Load and process data from GitHub Raw URL
CSV_URL = "https://raw.githubusercontent.com/alby41403-tech/legendary-rankie/refs/heads/main/j_msyjho6h2bi8surb3b.csv"


@st.cache_data
data_load_state = st.text(
    "Loading and processing national rank list records..."
)


def load_and_process_data(url):
    try:
        df = pd.read_csv(url)

        # Standardize column naming just in case of spaces/cases
        df.columns = df.columns.str.strip()

        # Convert marks columns to numeric safely
        mark_cols = ["Biology", "Physics", "Chemistry"]
        for col in mark_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        # Calculate True Index Mark out of 300:
        # Convert Physics, Chemistry, Biology from out of 120 down to out of 100, then sum them.
        df["Converted_Bio"] = (df["Biology"] / 120.0) * 100
        df["Converted_Phy"] = (df["Physics"] / 120.0) * 100
        df["Converted_Chem"] = (df["Chemistry"] / 120.0) * 100

        df["Calculated_Index_Mark"] = (
            df["Converted_Bio"] + df["Converted_Phy"] + df["Converted_Chem"]
        ).round(2)

        # Sort entire dataset in descending order based on the new Calculated Index Mark
        df = df.sort_values(
            by="Calculated_Index_Mark", ascending=False
        ).reset_index(drop=True)

        # Assign correct sequential Serial Numbers from 1 to 7,000+
        df["S. No"] = range(1, len(df) + 1)

        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None


df = load_and_process_data(CSV_URL)
data_load_state.empty()

if df is not None:
    # Check if a status column exists, otherwise simulate/default it for separation logic
    # (If your CSV includes a status column like 'Status', update the identifier below)
    status_column_name = None
    for col in df.columns:
        if "status" in col.lower():
            status_column_name = col
            break

    # If no status column exists in CSV, we map a placeholder status column for demonstration purposes
    if not status_column_name:
        # Example condition: Let's assume rows with index mark evaluation or a dummy condition splits accepted/pending vs rejected,
        # or we check if there's a specific column. We'll default to checking or setting a mock column if missing.
        df["Status"] = "Accepted"  # Default fallback if column missing

    # Home View: Two main interactive blocks
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
        # Back button to return home
        if st.button("⬅ Back to Categories"):
            st.session_state.selected_view = None
            st.rerun()

        # Determine dataset partition based on selection
        if st.session_state.selected_view == "Accepted_Pending":
            st.markdown(
                "## 📋 Accepted & Pending Applicants Rank List (Sorted by Index Mark)"
            )

            # Legend notice box explaining red highlight for pending status
            st.markdown(
                """
                <div class="legend-box">
                    <strong>🔴 Color Legend Notice:</strong> Rows highlighted in <span style="color: #DC2626; font-weight: bold;">Soft Red</span> indicate applicants whose status is currently <strong>Pending</strong>. Standard rows are fully accepted.
                </div>
            """,
                unsafe_allow_html=True,
            )

            # Filter for accepted or pending records
            view_df = df[
                df["Status"].astype(str).str.contains("Accept|Pend", case=False, na=False)
            ]

        else:
            st.markdown("## ❌ Rejected Applicants List")
            # Filter for rejected records
            view_df = df[
                df["Status"].astype(str).str.contains("Reject", case=False, na=False)
            ]

        # Search Bar Box at the top for Application Number lookup
        st.markdown("---")
        search_query = st.text_input(
            "🔍 Enter Application Number to look up specific standing:"
        )

        if search_query:
            # Filter data frame matching the application number column
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

        # Display Total Count Metrics
        st.markdown(f"**Total records displayed:** {len(display_df)}")

        # Render Data Table Responsively
        # To highlight pending rows in red, we can use a custom styling function if rendered via pandas styler,
        # or render dataframe neatly. Let's use Pandas Styler for row highlighting if status contains 'Pending'.
        def highlight_pending(row):
            if "pend" in str(row.get("Status", "")).lower():
                return ["background-color: #FEE2E2"] * len(row)
            return [""] * len(row)

        if not display_df.empty:
            # Drop temporary technical helper columns before display if needed, keeping exact requested names
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

            styled_table = display_df[columns_to_space := columns_to_show].style.apply(
                highlight_pending, axis=1
            )
            st.dataframe(styled_table, use_container_width=True, hide_index=True)
        else:
            st.info("No records available in this view.")
          
