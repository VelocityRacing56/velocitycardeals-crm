# Enhanced Streamlit Car Flipping CRM App with MMR Calculator
import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="VelocityCarDeals CRM", layout="wide", initial_sidebar_state="expanded")

# Enhanced Professional Business Styling
st.markdown("""
    <style>
    /* Main app background - Professional gradient */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-attachment: fixed;
    }
    
    /* Content containers */
    .main .block-container {
        background-color: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        backdrop-filter: blur(10px);
    }
    
    /* Header styling */
    h1 {
        color: #2c3e50;
        text-align: center;
        font-size: 2.8em;
        font-weight: 700;
        margin-bottom: 1.5rem;
        text-shadow: none;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Subheader styling */
    .stSubheader {
        color: #34495e;
        font-weight: 600;
        font-size: 1.4em;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #3498db;
    }
    
    /* Form and input styling */
    .stTextInput > label, .stDateInput > label, .stNumberInput > label, 
    .stTextArea > label, .stSelectbox > label {
        font-weight: 600;
        color: #2c3e50;
        font-size: 0.95em;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(45deg, #3498db, #2980b9);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(45deg, #2980b9, #3498db);
        box-shadow: 0 6px 20px rgba(52, 152, 219, 0.4);
        transform: translateY(-2px);
    }
    
    /* DataFrame styling */
    .stDataFrame {
        background-color: rgba(255,255,255,0.98);
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border: 1px solid #e0e6ed;
    }
    
    /* Form container styling */
    .stForm {
        background-color: #f8f9fa;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid #e9ecef;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    /* Professional card styling for market data */
    .market-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border-left: 4px solid #3498db;
        transition: all 0.3s ease;
    }
    
    .market-card:hover {
        box-shadow: 0 8px 25px rgba(0,0,0,0.12);
        transform: translateY(-2px);
    }
    
    /* Professional metric styling */
    .metric-container {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

# Gmail API integration functions
import base64
from email.mime.text import MIMEText
try:
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
except ImportError:
    def send_email_gmail(recipient, subject, body_text):
        st.error("Gmail API dependencies not installed. Please install google-auth, google-api-python-client")
        return None

# Initialize session states
if "contact_data" not in st.session_state:
    st.session_state.contact_data = pd.DataFrame(columns=["Name", "Phone", "Type", "Associated VIN"])

if "crm_data" not in st.session_state:
    st.session_state.crm_data = pd.DataFrame(columns=[
        "VIN", "Make", "Model", "Year", "Purchase Date", "Purchase Price ($)",
        "Sold Date", "Sold Price ($)", "Profit ($)", "Status"
    ])

if "follow_up_log" not in st.session_state:
    st.session_state.follow_up_log = pd.DataFrame(columns=["Dealership", "Phone", "Email", "Message Sent", "Date Sent", "Needs Follow-Up"])

# Sidebar
st.sidebar.title("🚗 Navigation")
page = st.sidebar.selectbox("Choose a section:", [
    "Dashboard", "Add Car", "Market Research", "Transactions", "Follow-up Tracker", 
    "Contacts", "Dealer Tools", "Analytics", "Settings"
])

# Professional Light/Dark theme toggle
mode = st.sidebar.radio("🌗 Theme Mode", ["Professional Light", "Executive Dark"])
if mode == "Executive Dark":
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
    }
    .main .block-container {
        background-color: rgba(44, 62, 80, 0.95);
        color: white;
    }
    h1, h2, h3 { color: #ecf0f1; }
    .stSubheader { color: #bdc3c7; border-bottom: 2px solid #e67e22; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏢 VelocityCarDeals - Professional CRM System")

# Dashboard
if page == "Dashboard":
    st.subheader("📊 Business Dashboard")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_cars = len(st.session_state.crm_data)
    watching = len(st.session_state.crm_data[st.session_state.crm_data["Status"] == "Watch"])
    purchased = len(st.session_state.crm_data[st.session_state.crm_data["Status"] == "Purchased"])
    sold = len(st.session_state.crm_data[st.session_state.crm_data["Status"] == "Sold"])
    
    with col1:
        st.metric("Total Cars", total_cars)
    with col2:
        st.metric("Watching", watching)
    with col3:
        st.metric("Purchased", purchased)
    with col4:
        st.metric("Sold", sold)
    
    # Recent activity
    if not st.session_state.crm_data.empty:
        st.subheader("Recent Cars")
        st.dataframe(st.session_state.crm_data.tail(5))

# Add Car section
elif page == "Add Car":
    with st.form("add_car_form"):
        st.subheader("Add a Car to Watchlist")
        vin = st.text_input("VIN")
        make = st.text_input("Make")
        model = st.text_input("Model")
        year = st.number_input("Year", min_value=1980, max_value=2030, step=1)
        contact_name = st.text_input("Seller Name")
        contact_phone = st.text_input("Seller Phone Number")
        submitted = st.form_submit_button("Add to Watchlist")
        
        if submitted and vin:
            new_row = pd.DataFrame([[vin, make, model, year, None, None, None, None, None, "Watch"]], 
                                  columns=st.session_state.crm_data.columns)
            st.session_state.crm_data = pd.concat([st.session_state.crm_data, new_row], ignore_index=True)
            
            # Add contact info if provided
            if contact_name and contact_phone:
                new_contact = pd.DataFrame([[contact_name, contact_phone, "Seller", vin]], 
                                         columns=st.session_state.contact_data.columns)
                st.session_state.contact_data = pd.concat([st.session_state.contact_data, new_contact], ignore_index=True)
            
            st.success("Car added to watchlist!")

# Market Research section
elif page == "Market Research":
    st.subheader("🔍 Market Research & Lead Generation")
    
    col1, col2 = st.columns(2)
    with col1:
        search_make = st.text_input("Make")
        search_model = st.text_input("Model")
    with col2:
        search_year = st.number_input("Year", min_value=1980, max_value=2030, step=1)
        max_price = st.number_input("Max Price ($)", min_value=0, step=1000)
    
    if st.button("🔍 Search Market") and search_make and search_model:
        st.subheader("📊 Market Data for Similar Listings")
        st.markdown(f"Showing recent listings for **{search_year} {search_make} {search_model}**:")
        
        # Sample market data (in real app, this would connect to actual APIs)
        sample_market_data = pd.DataFrame({
            'Year': [search_year]*6,
            'Make': [search_make]*6,
            'Model': [search_model]*6,
            'Mileage': [85000, 102000, 96000, 88000, 92000, 110000],
            'Price ($)': [6200, 5800, 6000, 6350, 6100, 5700],
            'Location': [
                'California - Los Angeles', 'California - San Diego', 'California - Riverside',
                'USA - National Average', 'Arizona - Phoenix', 'Nevada - Las Vegas'
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
            with st.container():
                st.markdown(f"""
                <div class="market-card">
                    <h4 style="color: #2c3e50; margin-bottom: 0.5rem;">{row['Year']} {row['Make']} {row['Model']}</h4>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                        <span><strong>Mileage:</strong> {row['Mileage']:,} mi</span>
                        <span><strong>Price:</strong> <span style="color: #27ae60; font-weight: bold;">${row['Price ($)']:,}</span></span>
                    </div>
                    <div style="margin-bottom: 0.5rem;">
                        <strong>Location:</strong> {row['Location']}
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong>Dealer:</strong> {row['Dealership']}<br>
                            <strong>Phone:</strong> {row['Phone']}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns([1, 1, 1])
                with col1:
                    if st.button(f"📞 Call {row['Dealership']}", key=f"call_{i}"):
                        st.write(f"Dialing {row['Phone']}...")
                
                with col2:
                    if st.button(f"⭐ Save Contact", key=f"save_{i}"):
                        contact = pd.DataFrame([[row['Dealership'], row['Phone'], "Seller", ""]], 
                                             columns=st.session_state.contact_data.columns)
                        st.session_state.contact_data = pd.concat([st.session_state.contact_data, contact], ignore_index=True)
                        st.success(f"Contact for {row['Dealership']} saved!")

                with col3:
                    if st.button(f"📧 Email Template", key=f"email_btn_{i}"):
                        st.session_state[f"show_email_{i}"] = not st.session_state.get(f"show_email_{i}", False)

                # Email section
                if st.session_state.get(f"show_email_{i}", False):
                    email_message = (
                        f"Subject: Vehicle Sourcing Inquiry - {row['Year']} {row['Make']} {row['Model']}\n\n"
                        f"Dear {row['Dealership']} Team,\n\n"
                        f"I hope this message finds you well. My name is Anthony Rodas, and I represent VelocityCarDeals, "
                        f"a professional automotive sourcing company.\n\n"
                        f"I am currently seeking a {row['Year']} {row['Make']} {row['Model']} for one of our clients. "
                        f"I noticed you may have this vehicle available and would like to discuss potential acquisition.\n\n"
                        f"We are serious cash buyers with immediate funding available and can close quickly. "
                        f"If you have this vehicle or similar inventory, please contact me at your earliest convenience.\n\n"
                        f"Contact Information:\n"
                        f"Email: AnthonyRodas@velocitycarssale.com\n"
                        f"Phone: 949-796-2933\n\n"
                        f"Thank you for your time and consideration. I look forward to establishing a mutually beneficial business relationship.\n\n"
                        f"Best regards,\n"
                        f"Anthony Rodas\n"
                        f"Senior Acquisition Specialist\n"
                        f"VelocityCarDeals"
                    )

                    st.text_area("📧 Professional Email Template", value=email_message, height=200, key=f"email_template_{i}")
                
                st.markdown("---")

# Transactions section
elif page == "Transactions":
    st.subheader("💵 Transaction Management")
    
    tab1, tab2, tab3 = st.tabs(["Mark as Purchased", "Mark as Sold", "Delete Entry"])
    
    with tab1:
        if not st.session_state.crm_data.empty:
            watch_cars = st.session_state.crm_data[st.session_state.crm_data["Status"] == "Watch"]["VIN"].tolist()
            if watch_cars:
                purchase_vin = st.selectbox("Select VIN to mark as purchased", watch_cars)
                purchase_date = st.date_input("Purchase Date")
                purchase_price = st.number_input("Purchase Price ($)", min_value=0.0, step=100.0)
                if st.button("Update Purchase Info"):
                    idx = st.session_state.crm_data[st.session_state.crm_data["VIN"] == purchase_vin].index
                    if not idx.empty:
                        st.session_state.crm_data.loc[idx, "Purchase Date"] = pd.to_datetime(purchase_date)
                        st.session_state.crm_data.loc[idx, "Purchase Price ($)"] = purchase_price
                        st.session_state.crm_data.loc[idx, "Status"] = "Purchased"
                        st.success("Car marked as purchased!")
            else:
                st.info("No cars in watchlist to mark as purchased.")
    
    with tab2:
        if not st.session_state.crm_data.empty:
            purchased_cars = st.session_state.crm_data[st.session_state.crm_data["Status"] == "Purchased"]["VIN"].tolist()
            if purchased_cars:
                sold_vin = st.selectbox("Select VIN to mark as sold", purchased_cars)
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
            else:
                st.info("No purchased cars to mark as sold.")
    
    with tab3:
        if not st.session_state.crm_data.empty:
            vin_to_delete = st.selectbox("Select VIN to delete", st.session_state.crm_data["VIN"])
            if st.button("Delete Selected Car", type="secondary"):
                st.session_state.crm_data = st.session_state.crm_data[st.session_state.crm_data["VIN"] != vin_to_delete]
                st.success(f"Car with VIN {vin_to_delete} deleted.")

# Follow-up Tracker section
elif page == "Follow-up Tracker":
    st.subheader("📬 Follow-up Log & Tracker")
    
    with st.form("follow_up_entry"):
        follow_name = st.text_input("Dealership Name")
        follow_phone = st.text_input("Phone Number")
        follow_email = st.text_input("Email Address")
        follow_msg = st.text_area("Message Sent")
        follow_date = st.date_input("Date Sent")
        needs_follow = st.checkbox("Needs Follow-Up?", value=True)
        follow_submit = st.form_submit_button("Log Communication")
        
        if follow_submit:
            new_log = pd.DataFrame([[follow_name, follow_phone, follow_email, follow_msg, follow_date, needs_follow]], 
                                  columns=st.session_state.follow_up_log.columns)
            st.session_state.follow_up_log = pd.concat([st.session_state.follow_up_log, new_log], ignore_index=True)
            st.success("Follow-up logged!")

    if not st.session_state.follow_up_log.empty:
        st.subheader("🔍 View Follow-Ups")
        follow_up_only = st.checkbox("Show only contacts needing follow-up")
        if follow_up_only:
            filtered_log = st.session_state.follow_up_log[st.session_state.follow_up_log["Needs Follow-Up"] == True].copy()
            if not filtered_log.empty:
                filtered_log["Days Since Contact"] = (date.today() - pd.to_datetime(filtered_log["Date Sent"])).dt.days
                st.dataframe(filtered_log)
            else:
                st.info("No follow-ups needed!")
        else:
            st.dataframe(st.session_state.follow_up_log)

# Contacts section
elif page == "Contacts":
    st.subheader("📞 Contact Management")
    
    with st.form("add_contact"):
        st.write("Add a Contact (Buyer or Seller)")
        contact_name = st.text_input("Contact Name")
        contact_phone = st.text_input("Phone Number")
        contact_type = st.selectbox("Type", ["Seller", "Buyer"])
        associated_vin = st.text_input("Associated VIN (optional)")
        contact_submitted = st.form_submit_button("Add Contact")
        
        if contact_submitted and contact_name and contact_phone:
            new_contact = pd.DataFrame([[contact_name, contact_phone, contact_type, associated_vin]], 
                                      columns=st.session_state.contact_data.columns)
            st.session_state.contact_data = pd.concat([st.session_state.contact_data, new_contact], ignore_index=True)
            st.success("Contact added!")
    
    if not st.session_state.contact_data.empty:
        st.subheader("Contact List")
        st.dataframe(st.session_state.contact_data)

# Dealer Tools section
elif page == "Dealer Tools":
    st.subheader("🛠️ Professional Dealer Tools")
    
    tab1, tab2, tab3 = st.tabs(["Offer Sheet Generator", "AI Pitch Assistant", "MMR Calculator"])
    
    with tab1:
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
    
    with tab2:
        st.subheader("🤖 AI Assistant: Generate a Pitch to Find a Car")
        car_description = st.text_area("Describe the car you're trying to source (year, make, model, trim, budget, etc.):")
        if st.button("Generate Pitch"):
            if car_description:
                pitch = f"Hi, I'm looking for a vehicle with the following specs: {car_description}. If you have something that fits or close, let me know. Cash buyer, ready to move fast."
                st.markdown(f"**Generated Pitch:**\n\n{pitch}")
                st.download_button("📄 Download Pitch", data=pitch, file_name="Pitch.txt", mime="text/plain")
            else:
                st.warning("Please describe the car you're looking for.")
    
    with tab3:
        st.subheader("📊 MMR-Based Price Calculator")
        mmr_input = st.number_input("Enter MMR Value ($)", min_value=0.0, step=100.0)
        if mmr_input:
            low_offer = mmr_input * 0.85
            high_offer = mmr_input * 0.92
            st.markdown(f"**Target Buy Price Range (8–15% below MMR):** 💰 **${low_offer:,.2f} – ${high_offer:,.2f}**")

# Analytics section
elif page == "Analytics":
    st.subheader("📈 Business Analytics")
    
    if not st.session_state.crm_data.empty:
        # Monthly profit summary
        sold_data = st.session_state.crm_data[st.session_state.crm_data["Status"] == "Sold"].copy()
        if not sold_data.empty and not sold_data["Sold Date"].dropna().empty:
            sold_data["Sold Date"] = pd.to_datetime(sold_data["Sold Date"], errors='coerce')
            sold_data["Month"] = sold_data["Sold Date"].dt.to_period("M")
            summary = sold_data.dropna(subset=["Profit ($)"]).groupby("Month")["Profit ($)"].sum()
            
            if not summary.empty:
                st.subheader("📊 Monthly Profit Summary")
                fig = px.bar(x=summary.index.astype(str), y=summary.values, 
                           labels={'x': 'Month', 'y': 'Profit ($)'}, 
                           title="Monthly Profit Trend")
                st.plotly_chart(fig, use_container_width=True)
        
        # Status distribution
        status_counts = st.session_state.crm_data["Status"].value_counts()
        if not status_counts.empty:
            st.subheader("📋 Inventory Status Distribution")
            fig = px.pie(values=status_counts.values, names=status_counts.index, 
                        title="Car Status Distribution")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available for analytics. Add some cars to see insights!")

# Settings section
elif page == "Settings":
    st.subheader("⚙️ Settings & Data Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📤 Export Data")
        if st.download_button("Download CRM CSV Report", 
                             data=st.session_state.crm_data.to_csv(index=False).encode("utf-8"), 
                             file_name="CarFlipCRM_Report.csv", 
                             mime="text/csv"):
            st.success("CSV report downloaded!")
        
        if st.download_button("Download Contacts CSV", 
                             data=st.session_state.contact_data.to_csv(index=False).encode("utf-8"), 
                             file_name="Contacts_Report.csv", 
                             mime="text/csv"):
            st.success("Contacts CSV downloaded!")
    
    with col2:
        st.subheader("🗑️ Clear Data")
        if st.button("Clear All CRM Data", type="secondary"):
            st.session_state.crm_data = pd.DataFrame(columns=[
                "VIN", "Make", "Model", "Year", "Purchase Date", "Purchase Price ($)",
                "Sold Date", "Sold Price ($)", "Profit ($)", "Status"
            ])
            st.success("CRM data cleared!")
        
        if st.button("Clear All Contacts", type="secondary"):
            st.session_state.contact_data = pd.DataFrame(columns=["Name", "Phone", "Type", "Associated VIN"])
            st.success("Contacts data cleared!")

# Current inventory display at bottom of every page
if not st.session_state.crm_data.empty:
    st.subheader("📋 Current Inventory")
    st.dataframe(st.session_state.crm_data, use_container_width=True)
