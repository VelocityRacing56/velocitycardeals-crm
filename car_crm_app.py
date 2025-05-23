# Streamlit Car Flipping CRM App with MMR Calculator
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Car Flipping CRM", layout="wide")

# Set background styling
st.markdown("""
    <style>
    .stApp {
        background-image: url('https://images.unsplash.com/photo-1592194996308-7b43878e84a6?ixlib=rb-4.0.3&auto=format&fit=crop&w=1950&q=80');
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    .css-18e3th9 {
        background-color: rgba(255, 255, 255, 0.85) !important;
        border-radius: 10px;
        padding: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize contact list if not already present
if "contact_data" not in st.session_state:
    st.session_state.contact_data = pd.DataFrame(columns=["Name", "Phone", "Type", "Associated VIN"])


# Initialize session state if not already present
if "crm_data" not in st.session_state:
    st.session_state.crm_data = pd.DataFrame(columns=[
        "VIN", "Make", "Model", "Year", "Purchase Date", "Purchase Price ($)",
        "Sold Date", "Sold Price ($)", "Profit ($)", "Status"
    ])

st.markdown("""
    <style>
    h1 {
        color: #ff1e1e;
        text-align: center;
        font-size: 3em;
        font-weight: bold;
        text-shadow: 1px 1px 2px #000;
    }
    .stSubheader, .stTextInput > label, .stDateInput > label, .stNumberInput > label, .stTextArea > label, .stSelectbox > label {
        font-weight: 600;
    }
    .stDataFrame {
        background-color: rgba(255,255,255,0.95);
        border-radius: 10px;
        padding: 10px;
    }
    </style>
""", unsafe_allow_html=True)

from PIL import Image

logo = Image.open("logo.png")  # Make sure logo.png is in the same directory as your app
st.sidebar.image(logo, width=200)

# Light/Dark theme toggle
mode = st.sidebar.radio("🌗 Theme Mode", ["Light", "Dark"])
if mode == "Dark":
    st.markdown("""
    <style>
    body {
        background-color: #1e1e1e;
        color: white;
    }
    .stApp {
        background-color: #1e1e1e;
        color: white;
    }
    .stDataFrame {
        background-color: rgba(30,30,30,0.95);
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
    .stDataFrame {
        background-color: rgba(255,255,255,0.95);
        color: black;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🚗 Car Flipping CRM")

# Form to add new car
with st.form("add_car_form"):
    st.subheader("Add a Car to Watchlist")
    vin = st.text_input("VIN")
    make = st.text_input("Make")
    model = st.text_input("Model")
    year = st.number_input("Year", min_value=1980, max_value=2030, step=1)
    submitted = st.form_submit_button("Add to Watchlist")
    if submitted and vin:
        new_row = pd.DataFrame([[vin, make, model, year, None, None, None, None, None, "Watch"]], columns=st.session_state.crm_data.columns)
        # Prompt for contact info associated with this watchlist entry
        contact_name = st.text_input("Seller Name")
        contact_phone = st.text_input("Seller Phone Number")
        if contact_name and contact_phone:
            new_contact = pd.DataFrame([[contact_name, contact_phone, "Seller", vin]], columns=st.session_state.contact_data.columns)
            st.session_state.contact_data = pd.concat([st.session_state.contact_data, new_contact], ignore_index=True)
        st.session_state.crm_data = pd.concat([st.session_state.crm_data, new_row], ignore_index=True)
        st.success("Car added to watchlist!")

        # Simulated API call for similar market listings
        st.subheader("📊 Market Data for Similar Listings")
        if make and model:
            # NOTE: Replace with actual API call if available (e.g., Edmunds, CarGurus)
            st.markdown(f"Showing recent listings for **{year} {make} {model}**:")
            sample_market_data = pd.DataFrame({
                'Year': [year]*6,
                'Make': [make]*6,
                'Model': [model]*6,
                'Mileage': [85000, 102000, 96000, 88000, 92000, 110000],
                'Price ($)': [6200, 5800, 6000, 6350, 6100, 5700],
                'Location': [
                    'California - Los Angeles',
                    'California - San Diego',
                    'California - Riverside',
                    'USA - National Average',
                    'Midwest - Phoenix',
                    'Midwest - Las Vegas'
                ],
                'Dealership': [
                    'Auto Town LA', 'Pacific Auto Center', 'Riverside Auto Sales',
                    'National AutoMart', 'Desert Cars Phoenix', 'Vegas Value Motors'
                ],
                'Phone': [
                    '213-555-0123', '619-555-0198', '951-555-0456',
                    '800-555-2300', '602-555-8765', '702-555-3456'
                ]
            })
            for i, row in sample_market_data.iterrows():
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"**{row['Year']} {row['Make']} {row['Model']}**")
                    st.markdown(f"Trim: Unknown | Mileage: {row['Mileage']:,} | Price: ${row['Price ($)']:,} | Location: {row['Location']}")
                    st.markdown(f"Dealership: {row['Dealership']} | Phone: {row['Phone']}")
                with col2:
                    if st.button(f"📞 Call {row['Dealership']}", key=f"call_{i}"):
                        st.write(f"Dialing {row['Phone']}...")
                    if st.button(f"⭐ Save Contact", key=f"save_{i}"):
                        contact = pd.DataFrame([[row['Dealership'], row['Phone'], "Seller", ""]], columns=st.session_state.contact_data.columns)
                        st.session_state.contact_data = pd.concat([st.session_state.contact_data, contact], ignore_index=True)
                        st.success(f"Contact for {row['Dealership']} saved!")

                    # Add email and SMS message generation
# ✅ Gmail API integration
import base64
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os.path
import pickle

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def send_email_gmail(recipient, subject, body_text):
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    message = MIMEText(body_text)
    message['to'] = recipient
    message['from'] = 'theofficialadrodas56@gmail.com'
    message['subject'] = subject
    raw_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
    send_message = (service.users().messages().send(userId="me", body=raw_message).execute())
    return send_message
# To enable email sending, integrate Gmail API:
# 1. Enable Gmail API at https://console.cloud.google.com/
# 2. Set up OAuth2 credentials for a desktop/web app
# 3. Use `google-auth`, `google-api-python-client` to send email from AnthonyRodas@velocitycarssale.com

# ✅ Google Voice call placeholder
# To initiate a call, you could simulate with a link or instruct the user:
# Use: https://voice.google.com/u/0/calls?a=nc,{phone_number}
# You may also instruct the user to copy/paste the number into Google Voice manually.
                        email_message = f"Subject: Vehicle Sourcing Inquiry

Hello {row['Dealership']},

My name is Anthony Rodas from VelocityBrokerDeals. I'm interested in the {row['Year']} {row['Make']} {row['Model']} listed at your dealership.

Please call or email me back at AnthonyRodas@velocitycarssale.com or 949-796-2933.

Best,
Anthony Rodas
VelocityBrokerDeals"
                    sms_message = f"Hi, this is Anthony Rodas from VelocityBrokerDeals. I'm interested in your {row['Year']} {row['Make']} {row['Model']}. Please call/text 949-796-2933."

                    st.text_area("📧 Email Template", value=email_message, height=180)
                    if st.button(f"📨 Send Email to {row['Dealership']}", key=f"email_{i}"):
                        recipient_email = st.text_input(f"Enter email for {row['Dealership']}", key=f"email_input_{i}")
                        if recipient_email:
                            try:
                                send_email_gmail(recipient_email, "Vehicle Sourcing Inquiry", email_message)
                                st.success("Email sent successfully!")
                            except Exception as e:
                                st.error(f"Failed to send email: {e}")
                        try:
                            send_email_gmail(row['Phone'] + "@example.com", "Vehicle Sourcing Inquiry", email_message)
                            st.success("Email sent successfully!")
                        except Exception as e:
                            st.error(f"Failed to send email: {e}")
                    st.text_area("📱 SMS Template", value=sms_message, height=80)
                    st.markdown(f"[📞 Call Now](https://voice.google.com/u/0/calls?a=nc,{row['Phone'].replace('-', '')})")
                    st.markdown(f"📧 Saved message for {row['Dealership']} with phone {row['Phone']}.")
                        contact = pd.DataFrame([[row['Dealership'], row['Phone'], "Seller", ""]], columns=st.session_state.contact_data.columns)
                        st.session_state.contact_data = pd.concat([st.session_state.contact_data, contact], ignore_index=True)
                        st.success(f"Contact for {row['Dealership']} saved!")
        else:
            st.info("Enter Make and Model to fetch market data.")

# Section to mark as purchased
st.subheader("💵 Mark a Car as Purchased")
purchase_vin = st.selectbox("Select VIN to mark as purchased", st.session_state.crm_data[st.session_state.crm_data["Status"] == "Watch"]["VIN"])
purchase_date = st.date_input("Purchase Date")
purchase_price = st.number_input("Purchase Price ($)", min_value=0.0, step=100.0)
if st.button("Update Purchase Info"):
    idx = st.session_state.crm_data[st.session_state.crm_data["VIN"] == purchase_vin].index
    if not idx.empty:
        st.session_state.crm_data.loc[idx, "Purchase Date"] = pd.to_datetime(purchase_date)
        st.session_state.crm_data.loc[idx, "Purchase Price ($)"] = purchase_price
        st.session_state.crm_data.loc[idx, "Status"] = "Purchased"
        st.success("Car marked as purchased!")

# Section to mark as sold
st.subheader("💰 Mark a Car as Sold")
sold_vin = st.selectbox("Select VIN to mark as sold", st.session_state.crm_data[st.session_state.crm_data["Status"] == "Purchased"]["VIN"])
sold_date = st.date_input("Sold Date")
sold_price = st.number_input("Sold Price ($)", min_value=0.0, step=100.0)
if st.button("Update Sold Info"):
    idx = st.session_state.crm_data[st.session_state.crm_data["VIN"] == sold_vin].index
    if not idx.empty:
        st.session_state.crm_data.loc[idx, "Sold Date"] = pd.to_datetime(sold_date)
        st.session_state.crm_data.loc[idx, "Sold Price ($)"] = sold_price
        purchase_price = st.session_state.crm_data.loc[idx, "Purchase Price ($)"].values[0]
        if pd.notna(purchase_price):
            profit = sold_price - float(purchase_price)
            st.session_state.crm_data.loc[idx, "Profit ($)"] = profit
            st.session_state.crm_data.loc[idx, "Status"] = "Sold"
            st.success("Car marked as sold!")

# Dealer Offer Builder
st.subheader("📦 Create Dealer Offer Sheet")
with st.form("create_offer"):
    st.write("Enter Car Details to Generate an Offer")
    offer_vin = st.text_input("VIN")
    stock_number = st.text_input("Stock Number")
    offer_mileage = st.number_input("Mileage", min_value=0)
    offer_make = st.text_input("Make")
    offer_model = st.text_input("Model")
    offer_trim = st.text_input("Trim")
    offer_price = st.number_input("Offer Price ($)", min_value=0.0, step=100.0)
    notes = st.text_area("Notes")
    offer_submit = st.form_submit_button("Generate Offer")
    if offer_submit and offer_vin and offer_make and offer_model:
        offer_output = f"""
        ### 🔖 Dealer Offer Sheet
        - **VIN**: {offer_vin}  
        - **Stock #:** {stock_number}  
        - **Make / Model / Trim:** {offer_make} {offer_model} {offer_trim}  
        - **Mileage:** {offer_mileage:,} miles  
        - **Offer Price:** 💵 ${offer_price:,.2f}  
        - **Notes:** {notes}
        """
        st.markdown(offer_output)
        st.download_button(
            label="📄 Download Offer Sheet",
            data=offer_output,
            file_name=f"OfferSheet_{offer_vin}.txt",
            mime="text/plain"
        )

# Delete car entry from CRM table
st.subheader("🗑️ Delete a Car from CRM")
if not st.session_state.crm_data.empty:
    vin_to_delete = st.selectbox("Select VIN to delete", st.session_state.crm_data["VIN"])
    if st.button("Delete Selected Car"):
        st.session_state.crm_data = st.session_state.crm_data[st.session_state.crm_data["VIN"] != vin_to_delete]
        st.success(f"Car with VIN {vin_to_delete} deleted.")

# Display CRM table
st.subheader("📋 Current CRM Table")
st.dataframe(st.session_state.crm_data)

# Monthly profit summary
st.subheader("📈 Monthly Profit Summary")
if not st.session_state.crm_data["Sold Date"].dropna().empty:
    df = st.session_state.crm_data.copy()
    df["Sold Date"] = pd.to_datetime(df["Sold Date"], errors='coerce')
    df["Month"] = df["Sold Date"].dt.to_period("M")
    summary = df.dropna(subset=["Profit ($)"]).groupby("Month")["Profit ($)"].sum()
    st.bar_chart(summary)

# Email and Contact Follow-up Tracker
st.subheader("📬 Follow-up Log & Tracker")
if "follow_up_log" not in st.session_state:
    st.session_state.follow_up_log = pd.DataFrame(columns=["Dealership", "Phone", "Email", "Message Sent", "Date Sent", "Needs Follow-Up"])

with st.form("follow_up_entry"):
    follow_name = st.text_input("Dealership Name")
    follow_phone = st.text_input("Phone Number")
    follow_email = st.text_input("Email Address")
    follow_msg = st.text_area("Message Sent")
    follow_date = st.date_input("Date Sent")
    needs_follow = st.checkbox("Needs Follow-Up?", value=True)
    follow_submit = st.form_submit_button("Log Communication")
    if follow_submit:
        new_log = pd.DataFrame([[follow_name, follow_phone, follow_email, follow_msg, follow_date, needs_follow]], columns=st.session_state.follow_up_log.columns)
        st.session_state.follow_up_log = pd.concat([st.session_state.follow_up_log, new_log], ignore_index=True)
        st.success("Follow-up logged!")

if not st.session_state.follow_up_log.empty:
    from datetime import date

# Highlight rows needing follow-up
styled_follow_up = st.session_state.follow_up_log.copy()
styled_follow_up["RowColor"] = styled_follow_up["Needs Follow-Up"].apply(lambda x: "background-color: #fff3cd" if x else "")

# Render styled dataframe
st.dataframe(
    styled_follow_up.drop(columns=["RowColor"]),
    use_container_width=True
)
    st.subheader("🔍 View Follow-Ups Needed")
    follow_up_only = st.checkbox("Show only contacts needing follow-up")
    if follow_up_only:
        filtered_log = st.session_state.follow_up_log[st.session_state.follow_up_log["Needs Follow-Up"] == True]
        filtered_log["Days Since Contact"] = (date.today() - filtered_log["Date Sent"]).dt.days
st.dataframe(filtered_log)

# Contact management section
st.subheader("📞 Contacts")
with st.form("add_contact"):
    st.write("Add a Contact (Buyer or Seller)")
    contact_name = st.text_input("Contact Name")
    contact_phone = st.text_input("Phone Number")
    contact_type = st.selectbox("Type", ["Seller", "Buyer"])
    associated_vin = st.text_input("Associated VIN (optional)")
    contact_submitted = st.form_submit_button("Add Contact")
    if contact_submitted and contact_name and contact_phone:
        new_contact = pd.DataFrame([[contact_name, contact_phone, contact_type, associated_vin]], columns=st.session_state.contact_data.columns)
        st.session_state.contact_data = pd.concat([st.session_state.contact_data, new_contact], ignore_index=True)
        st.success("Contact added!")

st.dataframe(st.session_state.contact_data)

# Export to Excel
st.subheader("📤 Export CRM to Excel")
if st.download_button("Download Excel Report", data=st.session_state.crm_data.to_csv(index=False).encode("utf-8"), file_name="CarFlipCRM_Report.csv", mime="text/csv"):
    st.success("Excel report downloaded!")

# AI Assistant for Pitch Generation
st.subheader("🤖 AI Assistant: Generate a Pitch to Find a Car")
car_description = st.text_area("Describe the car you're trying to source (year, make, model, trim, budget, etc.):")
if st.button("Generate Pitch"):
    if car_description:
        pitch = f"Hi, I'm looking for a vehicle with the following specs: {car_description}. If you have something that fits or close, let me know. Cash buyer, ready to move fast."
        st.markdown(f"**Generated Pitch:**\n\n{pitch}")

        st.download_button("📄 Download Pitch", data=pitch, file_name="Pitch.txt", mime="text/plain")
    else:
        st.warning("Please describe the car you're looking for.")

# MMR Calculator
st.subheader("📊 MMR-Based Price Calculator")
mmr_input = st.number_input("Enter MMR Value ($)", min_value=0.0, step=100.0)
if mmr_input:
    low_offer = mmr_input * 0.85
    high_offer = mmr_input * 0.92
    st.markdown(f"**Target Buy Price Range (8–15% below MMR):** 💰 **${low_offer:,.2f} – ${high_offer:,.2f}**")
