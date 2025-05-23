import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import plotly.express as px
import plotly.graph_objects as go
import base64
from email.mime.text import MIMEText

# Gmail API imports with error handling
try:
    from googleapiclient.discovery import build
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    import pickle
    import os.path
    GMAIL_API_AVAILABLE = True
except ImportError:
    GMAIL_API_AVAILABLE = False
    st.error("Gmail API dependencies not installed. Please install required packages.")

# Page configuration
st.set_page_config(
    page_title="VelocityCarDeals CRM",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional styling (keeping your original CSS)
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
    
    /* Add your remaining CSS styles here */
    </style>
""", unsafe_allow_html=True)

# Initialize session states with error handling
def initialize_session_state():
    try:
        if "contact_data" not in st.session_state:
            st.session_state.contact_data = pd.DataFrame(
                columns=["Name", "Phone", "Type", "Associated VIN"]
            )
        if "crm_data" not in st.session_state:
            st.session_state.crm_data = pd.DataFrame(
                columns=[
                    "VIN", "Make", "Model", "Year", "Purchase Date",
                    "Purchase Price ($)", "Sold Date", "Sold Price ($)",
                    "Profit ($)", "Status"
                ]
            )
        if "follow_up_log" not in st.session_state:
            st.session_state.follow_up_log = pd.DataFrame(
                columns=[
                    "Dealership", "Phone", "Email", "Message Sent",
                    "Date Sent", "Needs Follow-Up"
                ]
            )
    except Exception as e:
        st.error(f"Error initializing session state: {str(e)}")
        st.stop()

# Gmail API integration function
def send_email_gmail(recipient, subject, body_text):
    if not GMAIL_API_AVAILABLE:
        st.error("Gmail API not available. Please install required packages.")
        return None
    
    try:
        SCOPES = ['https://www.googleapis.com/auth/gmail.send']
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
        
        raw_message = {'raw': base64.urlsafe_b64encode(
            message.as_bytes()).decode()}
        send_message = (service.users().messages().send(
            userId="me", body=raw_message).execute())
        return send_message
    
    except Exception as e:
        st.error(f"Error sending email: {str(e)}")
        return None

# Initialize the application
initialize_session_state()
# Main application logic
def main():
    st.title("🏢 VelocityCarDeals - Professional CRM System")

    # Sidebar navigation
    st.sidebar.title("🚗 Navigation")
    page = st.sidebar.selectbox("Choose a section:", [
        "Dashboard", "Add Car", "Market Research", "Transactions",
        "Follow-up Tracker", "Contacts", "Dealer Tools", "Analytics", "Settings"
    ])

    # Theme toggle
    mode = st.sidebar.radio("🌗 Theme Mode", ["Professional Light", "Executive Dark"])
    apply_theme(mode)

    # Page routing
    if page == "Dashboard":
        show_dashboard()
    elif page == "Add Car":
        show_add_car()
    elif page == "Market Research":
        show_market_research()
    elif page == "Transactions":
        show_transactions()
    elif page == "Follow-up Tracker":
        show_follow_up_tracker()
    elif page == "Contacts":
        show_contacts()
    elif page == "Dealer Tools":
        show_dealer_tools()
    elif page == "Analytics":
        show_analytics()
    elif page == "Settings":
        show_settings()

    # Show current inventory at bottom of every page
    if not st.session_state.crm_data.empty:
        st.subheader("📋 Current Inventory")
        st.dataframe(st.session_state.crm_data, use_container_width=True)

def apply_theme(mode):
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

def show_dashboard():
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

def show_add_car():
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
            try:
                new_row = pd.DataFrame([[vin, make, model, year, None, None, None, None, None, "Watch"]], 
                                     columns=st.session_state.crm_data.columns)
                st.session_state.crm_data = pd.concat([st.session_state.crm_data, new_row], ignore_index=True)
                
                if contact_name and contact_phone:
                    new_contact = pd.DataFrame([[contact_name, contact_phone, "Seller", vin]], 
                                             columns=st.session_state.contact_data.columns)
                    st.session_state.contact_data = pd.concat([st.session_state.contact_data, new_contact], ignore_index=True)
                
                st.success("Car added to watchlist!")
            except Exception as e:
                st.error(f"Error adding car: {str(e)}")

def show_market_research():
    st.subheader("🔍 Market Research & Lead Generation")
    
    col1, col2 = st.columns(2)
    with col1:
        search_make = st.text_input("Make")
        search_model = st.text_input("Model")
    with col2:
        search_year = st.number_input("Year", min_value=1980, max_value=2030, step=1)
        max_price = st.number_input("Max Price ($)", min_value=0, step=1000)
    
    if st.button("🔍 Search Market") and search_make and search_model:
        show_market_data(search_year, search_make, search_model, max_price)

def show_transactions():
    st.subheader("💵 Transaction Management")
    
    tab1, tab2, tab3 = st.tabs(["Mark as Purchased", "Mark as Sold", "Delete Entry"])
    
    with tab1:
        handle_purchase_tab()
    with tab2:
        handle_sold_tab()
    with tab3:
        handle_delete_tab()

def show_follow_up_tracker():
    st.subheader("📬 Follow-up Log & Tracker")
    handle_follow_up_system()

def show_contacts():
    st.subheader("📞 Contact Management")
    handle_contact_management()

def show_dealer_tools():
    st.subheader("🛠️ Professional Dealer Tools")
    
    tab1, tab2, tab3 = st.tabs(["Offer Sheet Generator", "AI Pitch Assistant", "MMR Calculator"])
    
    with tab1:
        handle_offer_sheet()
    with tab2:
        handle_ai_pitch()
    with tab3:
        handle_mmr_calculator()

def show_analytics():
    st.subheader("📈 Business Analytics")
    if not st.session_state.crm_data.empty:
        show_profit_analysis()
        show_status_distribution()
    else:
        st.info("No data available for analytics. Add some cars to see insights!")

def show_settings():
    st.subheader("⚙️ Settings & Data Management")
    handle_settings()

# Helper functions for specific features
def handle_purchase_tab():
    if not st.session_state.crm_data.empty:
        watch_cars = st.session_state.crm_data[st.session_state.crm_data["Status"] == "Watch"]["VIN"].tolist()
        if watch_cars:
            purchase_vin = st.selectbox("Select VIN to mark as purchased", watch_cars)
            purchase_date = st.date_input("Purchase Date")
            purchase_price = st.number_input("Purchase Price ($)", min_value=0.0, step=100.0)
            if st.button("Update Purchase Info"):
                update_purchase_info(purchase_vin, purchase_date, purchase_price)
        else:
            st.info("No cars in watchlist to mark as purchased.")

def handle_sold_tab():
    if not st.session_state.crm_data.empty:
        purchased_cars = st.session_state.crm_data[st.session_state.crm_data["Status"] == "Purchased"]["VIN"].tolist()
        if purchased_cars:
            sold_vin = st.selectbox("Select VIN to mark as sold", purchased_cars)
            sold_date = st.date_input("Sold Date")
            sold_price = st.number_input("Sold Price ($)", min_value=0.0, step=100.0)
            if st.button("Update Sold Info"):
                update_sold_info(sold_vin, sold_date, sold_price)
        else:
            st.info("No purchased cars to mark as sold.")

def handle_delete_tab():
    if not st.session_state.crm_data.empty:
        vin_to_delete = st.selectbox("Select VIN to delete", st.session_state.crm_data["VIN"])
        if st.button("Delete Selected Car", type="secondary"):
            delete_car(vin_to_delete)

# Run the application
if __name__ == "__main__":
    main()
