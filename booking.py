import streamlit as st
from datetime import date
import pandas as pd
import os

# ==============================
# CONFIG
# ==============================
OPEN_DATE = date(2026, 2, 15)
MAX_TABLES = 20
MAX_BOOKING_PER_GROUP = 2
EXCEL_FILE = "bookings.xlsx"

today = date.today()

st.title("📅 Table Booking System")

if today < OPEN_DATE:
    st.warning("🚫 Booking system is not open yet.")
    st.stop()

# ==============================
# LOAD DATA FROM EXCEL
# ==============================
if os.path.exists(EXCEL_FILE):
    df = pd.read_excel(EXCEL_FILE)
else:
    df = pd.DataFrame(columns=["Group", "Time Slot", "Table"])

# ==============================
# GROUPS
# ==============================
group_list = (
    [f"A{i}" for i in range(1, 21)] +
    [f"B{i}" for i in range(1, 9)]
)

# ==============================
# TIME SLOTS
# ==============================
booking_options = [
    "Thursday, Feb 26 | 08:30 - 12:30",
    "Friday, Feb 27 | 08:30 - 12:30",
    "Friday, Feb 27 | 13:30 - 17:30"
]

# ==============================
# HELPER FUNCTIONS
# ==============================
def save_to_excel(dataframe):
    dataframe.to_excel(EXCEL_FILE, index=False)

def get_booked_tables(slot):
    return df[df["Time Slot"] == slot]["Table"].tolist()

def count_group_booking(group):
    return len(df[df["Group"] == group])

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
            new_row = pd.DataFrame([{
                "Group": group,
                "Time Slot": selected_slot,
                "Table": table_number
            }])

            df = pd.concat([df, new_row], ignore_index=True)
            save_to_excel(df)

            st.success(f"🎉 Booking successful! {group} reserved Table {table_number}")
            st.rerun()

# ==============================
# CANCEL SECTION
# ==============================
st.header("❌ Cancel Booking")

if not df.empty:

    cancel_group = st.selectbox(
        "Select Group to Cancel",
        sorted(df["Group"].unique())
    )

    group_bookings = df[df["Group"] == cancel_group]

    cancel_option = st.selectbox(
        "Select Booking to Cancel",
        group_bookings.apply(
            lambda x: f'{x["Time Slot"]} | Table {x["Table"]}', axis=1
        )
    )

    if st.button("Cancel Selected Booking"):
        slot, table = cancel_option.split(" | Table ")
        df = df[~(
            (df["Group"] == cancel_group) &
            (df["Time Slot"] == slot) &
            (df["Table"] == int(table))
        )]

        save_to_excel(df)
        st.success("✅ Booking cancelled successfully!")
        st.rerun()

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

if not df.empty:
    st.dataframe(df, use_container_width=True)

    st.subheader("📊 Booking Summary per Group")
    summary = df.groupby("Group").size().reset_index(name="Total Bookings")
    st.dataframe(summary, use_container_width=True)

    # DOWNLOAD BUTTON
    st.download_button(
        label="⬇️ Download Booking Excel",
        data=open(EXCEL_FILE, "rb"),
        file_name="bookings.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

else:
    st.info("No bookings yet.")
