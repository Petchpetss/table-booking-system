import streamlit as st
import pandas as pd
from datetime import date
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ==============================
# GOOGLE SHEET CONNECTION (Cloud Safe)
# ==============================
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds_dict = dict(st.secrets["gcp_service_account"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

sheet = client.open("TableBookingData").sheet1

# ==============================
# LOAD DATA
# ==============================
data = sheet.get_all_records()
df = pd.DataFrame(data)

if df.empty:
    df = pd.DataFrame(columns=["Group", "Time Slot", "Table"])

# ==============================
# CONFIG
# ==============================
OPEN_DATE = date(2026, 2, 15)
MAX_TABLES = 20
MAX_BOOKING_PER_GROUP = 2
today = date.today()

if today < OPEN_DATE:
    st.warning("🚫 Booking system is not open yet.")
    st.stop()

group_list = (
    [f"A{i}" for i in range(1, 21)] +
    [f"B{i}" for i in range(1, 9)]
)

booking_options = [
    "Thursday, Feb 26 | 08:30 - 12:30",
    "Friday, Feb 27 | 08:30 - 12:30",
    "Friday, Feb 27 | 13:30 - 17:30"
]

# ==============================
# FUNCTIONS
# ==============================
def save_to_sheet(dataframe):
    sheet.clear()
    sheet.append_row(["Group", "Time Slot", "Table"])
    for _, row in dataframe.iterrows():
        sheet.append_row(row.tolist())

def get_booked_tables(slot):
    return df[df["Time Slot"] == slot]["Table"].tolist()

def count_group_booking(group):
    return len(df[df["Group"] == group])

# ==============================
# UI
# ==============================
st.title("📅 Table Booking System (Cloud Version)")

# BOOKING SECTION
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
            save_to_sheet(df)

            st.success("🎉 Booking Successful!")
            st.rerun()

# SHOW DATA
st.header("📋 All Bookings")
st.dataframe(df, use_container_width=True)

# SUMMARY
st.subheader("📊 Booking Summary per Group")
summary = df.groupby("Group").size().reset_index(name="Total Bookings")
st.dataframe(summary, use_container_width=True)
