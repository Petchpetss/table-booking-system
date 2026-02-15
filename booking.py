import streamlit as st
from datetime import date
import pandas as pd

# ==============================
# SAFE RERUN FUNCTION (Compatible All Versions)
# ==============================
def safe_rerun():
    if hasattr(st, "rerun"):
        st.rerun()
    elif hasattr(st, "experimental_rerun"):
        st.experimental_rerun()
    else:
        pass  # fallback: do nothing


# ==============================
# Configuration
# ==============================
OPEN_DATE = date(2026, 2, 15)
MAX_TABLES = 20
MAX_BOOKING_PER_GROUP = 2
today = date.today()

st.title("📅 Table Booking System")

if today < OPEN_DATE:
    st.warning("🚫 Booking system is not open yet.")
    st.stop()

# ==============================
# Session State
# ==============================
if "bookings" not in st.session_state:
    st.session_state.bookings = []

# ==============================
# Groups
# ==============================
group_list = (
    [f"A{i}" for i in range(1, 21)] +
    [f"B{i}" for i in range(1, 9)]
)

# ==============================
# Time Slots
# ==============================
booking_options = [
    "Thursday, Feb 26 | 08:30 - 12:30",
    "Friday, Feb 27 | 08:30 - 12:30",
    "Friday, Feb 27 | 13:30 - 17:30"
]

# ==============================
# Helper Functions
# ==============================
def get_booked_tables(slot):
    return [b["Table"] for b in st.session_state.bookings if b["Time Slot"] == slot]

def count_group_booking(group):
    return len([b for b in st.session_state.bookings if b["Group"] == group])

# ==============================
# BOOKING SECTION
# ==============================
st.header("📝 Make a Booking")

with st.form("booking_form"):
    group = st.selectbox("Select Group", group_list)
    selected_slot = st.selectbox("Select Time Slot", booking_options)

    booked_tables = get_booked_tables(selected_slot)
    available_tables = [i for i in range(1, MAX_TABLES+1) if i not in booked_tables]

    table_number = st.selectbox("Select Table", available_tables)

    submit = st.form_submit_button("Confirm Booking")

    if submit:
        if count_group_booking(group) >= MAX_BOOKING_PER_GROUP:
            st.error("❌ This group has already booked 2 time slots.")
        elif table_number in booked_tables:
            st.error("❌ This table is already booked.")
        else:
            st.session_state.bookings.append({
                "Group": group,
                "Time Slot": selected_slot,
                "Table": table_number
            })
            st.success(f"🎉 Booking successful! {group} reserved Table {table_number}")
            safe_rerun()

# ==============================
# CANCEL SECTION
# ==============================
st.header("❌ Cancel Booking")

if st.session_state.bookings:

    cancel_group = st.selectbox(
        "Select Group to Cancel",
        sorted(set([b["Group"] for b in st.session_state.bookings]))
    )

    group_bookings = [
        b for b in st.session_state.bookings
        if b["Group"] == cancel_group
    ]

    cancel_option = st.selectbox(
        "Select Booking to Cancel",
        [f'{b["Time Slot"]} | Table {b["Table"]}' for b in group_bookings]
    )

    if st.button("Cancel Selected Booking"):
        for b in group_bookings:
            label = f'{b["Time Slot"]} | Table {b["Table"]}'
            if label == cancel_option:
                st.session_state.bookings.remove(b)
                st.success("✅ Booking cancelled successfully!")
                safe_rerun()

else:
    st.info("No bookings available to cancel.")

# ==============================
# TABLE LAYOUT
# ==============================
st.header("🪑 Table Layout")

view_slot = st.selectbox("View tables for time slot", booking_options)

booked_tables = get_booked_tables(view_slot)

cols = st.columns(5)
for i in range(1, MAX_TABLES+1):
    col = cols[(i-1) % 5]
    if i in booked_tables:
        col.markdown(f"🔴 Table {i}")
    else:
        col.markdown(f"🟢 Table {i}")

# ==============================
# ALL BOOKINGS
# ==============================
st.header("📋 All Bookings")

if st.session_state.bookings:
    df = pd.DataFrame(st.session_state.bookings)
    st.dataframe(df, use_container_width=True)

    st.subheader("📊 Booking Summary per Group")
    summary = df.groupby("Group").size().reset_index(name="Total Bookings")
    st.dataframe(summary, use_container_width=True)

else:
    st.info("No bookings yet.")

