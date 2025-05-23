import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import base64
from email.mime.text import MIMEText

# Plotly imports with error handling
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

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

# Page configuration
st.set_page_config(
    page_title="VelocityCarDeals CRM",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional styling
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
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    /* Subheaders */
    .stSubheader {
        color: #2c3e50;
        border-bottom: 2px solid #3498db;
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
    }
    
    /* Forms */
    .stForm {
        background-color: rgba(52, 152, 219, 0.1);
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #3498db;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(52, 152, 219, 0.4);
    }
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
        st.error("Gmail API not available. Please install required packages: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
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
                if not os.path.exists('credentials.json'):
                    st.error("credentials.json file not found. Please download it from Google Cloud Console.")
                    return None
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

# Main application logic
def main():
    st.title("🏢 VelocityCarDeals - Professional CRM System")

    # Show Plotly warning if not available
    if not PLOTLY_AVAILABLE:
        st.warning("Plotly not available. Install with: pip install plotly")

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
    watching = len(st.session_state.crm_data[st.session_state.crm_data["Status"] == "Watch"]) if total_cars > 0 else 0
    purchased = len(st.session_state.crm_data[st.session_state.crm_data["Status"] == "Purchased"]) if total_cars > 0 else 0
    sold = len(st.session_state.crm_data[st.session_state.crm_data["Status"] == "Sold"]) if total_cars > 0 else 0
    
    with col1:
        st.metric("Total Cars", total_cars)
    with col2:
        st.metric("Watching", watching)
    with col3:
        st.metric("Purchased", purchased)
    with col4:
        st.metric("Sold", sold)

    # Calculate total profits
    if not st.session_state.crm_data.empty and "Profit ($)" in st.session_state.crm_data.columns:
        profit_data = st.session_state.crm_data["Profit ($)"].dropna()
        if not profit_data.empty:
            total_profit = profit_data.sum()
            st.metric("Total Profit", f"${total_profit:,.2f}")

    # Recent activity
    if not st.session_state.crm_data.empty:
        st.subheader("Recent Cars")
        st.dataframe(st.session_state.crm_data.tail(5), use_container_width=True)
    else:
        st.info("No cars in system yet. Add some cars to get started!")

def show_add_car():
    with st.form("add_car_form"):
        st.subheader("🚗 Add a Car to Watchlist")
        
        col1, col2 = st.columns(2)
        with col1:
            vin = st.text_input("VIN*", help="Vehicle Identification Number")
            make = st.text_input("Make*", help="e.g., Toyota, Honda, Ford")
            model = st.text_input("Model*", help="e.g., Camry, Civic, F-150")
        with col2:
            year = st.number_input("Year*", min_value=1980, max_value=2030, step=1, value=2020)
            contact_name = st.text_input("Seller Name", help="Optional")
            contact_phone = st.text_input("Seller Phone", help="Optional")
        
        submitted = st.form_submit_button("Add to Watchlist", type="primary")
        
        if submitted:
            if not vin or not make or not model:
                st.error("Please fill in all required fields (VIN, Make, Model)")
            else:
                try:
                    # Check for duplicate VIN
                    if not st.session_state.crm_data.empty and vin in st.session_state.crm_data["VIN"].values:
                        st.error("A car with this VIN already exists!")
                    else:
                        new_row = pd.DataFrame([[vin, make, model, year, None, None, None, None, None, "Watch"]], 
                                             columns=st.session_state.crm_data.columns)
                        st.session_state.crm_data = pd.concat([st.session_state.crm_data, new_row], ignore_index=True)
                        
                        if contact_name and contact_phone:
                            new_contact = pd.DataFrame([[contact_name, contact_phone, "Seller", vin]], 
                                                     columns=st.session_state.contact_data.columns)
                            st.session_state.contact_data = pd.concat([st.session_state.contact_data, new_contact], ignore_index=True)
                        
                        st.success(f"✅ {year} {make} {model} added to watchlist!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Error adding car: {str(e)}")

def show_market_research():
    st.subheader("🔍 Market Research & Lead Generation")
    
    col1, col2 = st.columns(2)
    with col1:
        search_make = st.text_input("Make", placeholder="e.g., Toyota")
        search_model = st.text_input("Model", placeholder="e.g., Camry")
    with col2:
        search_year = st.number_input("Year", min_value=1980, max_value=2030, step=1, value=2020)
        max_price = st.number_input("Max Price ($)", min_value=0, step=1000, value=25000)
    
    if st.button("🔍 Search Market", type="primary"):
        if search_make and search_model:
            show_market_data(search_year, search_make, search_model, max_price)
        else:
            st.warning("Please enter both Make and Model to search")

def show_market_data(year, make, model, max_price):
    """Display market research data"""
    st.subheader(f"Market Data for {year} {make} {model}")
    
    # Simulated market data (replace with real API calls)
    sample_data = {
        "Source": ["AutoTrader", "Cars.com", "CarGurus", "CarMax", "Local Dealer"],
        "Price": [max_price * 0.9, max_price * 0.95, max_price * 0.85, max_price * 1.1, max_price * 0.8],
        "Mileage": [45000, 52000, 38000, 61000, 41000],
        "Location": ["City A", "City B", "City C", "City D", "City E"]
    }
    
    df = pd.DataFrame(sample_data)
    st.dataframe(df, use_container_width=True)
    
    avg_price = df["Price"].mean()
    st.metric("Average Market Price", f"${avg_price:,.2f}")

def show_transactions():
    st.subheader("💵 Transaction Management")
    
    tab1, tab2, tab3 = st.tabs(["Mark as Purchased", "Mark as Sold", "Delete Entry"])
    
    with tab1:
        handle_purchase_tab()
    with tab2:
        handle_sold_tab()
    with tab3:
        handle_delete_tab()

def handle_purchase_tab():
    if not st.session_state.crm_data.empty:
        watch_cars = st.session_state.crm_data[st.session_state.crm_data["Status"] == "Watch"]
        if not watch_cars.empty:
            vin_options = watch_cars["VIN"].tolist()
            purchase_vin = st.selectbox("Select VIN to mark as purchased", vin_options)
            
            col1, col2 = st.columns(2)
            with col1:
                purchase_date = st.date_input("Purchase Date", value=date.today())
            with col2:
                purchase_price = st.number_input("Purchase Price ($)", min_value=0.0, step=100.0)
            
            if st.button("✅ Update Purchase Info", type="primary"):
                if purchase_price > 0:
                    update_purchase_info(purchase_vin, purchase_date, purchase_price)
                else:
                    st.error("Please enter a valid purchase price")
        else:
            st.info("No cars in watchlist to mark as purchased.")
    else:
        st.info("No cars in system yet.")

def handle_sold_tab():
    if not st.session_state.crm_data.empty:
        purchased_cars = st.session_state.crm_data[st.session_state.crm_data["Status"] == "Purchased"]
        if not purchased_cars.empty:
            vin_options = purchased_cars["VIN"].tolist()
            sold_vin = st.selectbox("Select VIN to mark as sold", vin_options)
            
            col1, col2 = st.columns(2)
            with col1:
                sold_date = st.date_input("Sold Date", value=date.today())
            with col2:
                sold_price = st.number_input("Sold Price ($)", min_value=0.0, step=100.0)
            
            if st.button("💰 Update Sold Info", type="primary"):
                if sold_price > 0:
                    update_sold_info(sold_vin, sold_date, sold_price)
                else:
                    st.error("Please enter a valid sold price")
        else:
            st.info("No purchased cars to mark as sold.")
    else:
        st.info("No cars in system yet.")

def handle_delete_tab():
    if not st.session_state.crm_data.empty:
        vin_to_delete = st.selectbox("Select VIN to delete", st.session_state.crm_data["VIN"])
        
        # Show car details before deletion
        car_info = st.session_state.crm_data[st.session_state.crm_data["VIN"] == vin_to_delete].iloc[0]
        st.write(f"**Car to delete:** {car_info['Year']} {car_info['Make']} {car_info['Model']} - Status: {car_info['Status']}")
        
        st.warning("⚠️ This action cannot be undone!")
        if st.button("🗑️ Delete Selected Car", type="secondary"):
            delete_car(vin_to_delete)
    else:
        st.info("No cars to delete.")

def update_purchase_info(vin, purchase_date, purchase_price):
    try:
        mask = st.session_state.crm_data["VIN"] == vin
        st.session_state.crm_data.loc[mask, "Purchase Date"] = purchase_date
        st.session_state.crm_data.loc[mask, "Purchase Price ($)"] = purchase_price
        st.session_state.crm_data.loc[mask, "Status"] = "Purchased"
        st.success(f"✅ Car {vin} marked as purchased for ${purchase_price:,.2f}")
        st.rerun()
    except Exception as e:
        st.error(f"Error updating purchase info: {str(e)}")

def update_sold_info(vin, sold_date, sold_price):
    try:
        mask = st.session_state.crm_data["VIN"] == vin
        purchase_price = st.session_state.crm_data.loc[mask, "Purchase Price ($)"].iloc[0]
        profit = sold_price - purchase_price
        
        st.session_state.crm_data.loc[mask, "Sold Date"] = sold_date
        st.session_state.crm_data.loc[mask, "Sold Price ($)"] = sold_price
        st.session_state.crm_data.loc[mask, "Profit ($)"] = profit
        st.session_state.crm_data.loc[mask, "Status"] = "Sold"
        
        st.success(f"✅ Car {vin} marked as sold for ${sold_price:,.2f} (Profit: ${profit:,.2f})")
        st.rerun()
    except Exception as e:
        st.error(f"Error updating sold info: {str(e)}")

def delete_car(vin):
    try:
        st.session_state.crm_data = st.session_state.crm_data[st.session_state.crm_data["VIN"] != vin]
        # Also remove associated contacts
        st.session_state.contact_data = st.session_state.contact_data[st.session_state.contact_data["Associated VIN"] != vin]
        st.success(f"✅ Car {vin} deleted successfully")
        st.rerun()
    except Exception as e:
        st.error(f"Error deleting car: {str(e)}")

def show_follow_up_tracker():
    st.subheader("📬 Follow-up Log & Tracker")
    handle_follow_up_system()

def handle_follow_up_system():
    tab1, tab2 = st.tabs(["Add Follow-up", "View Follow-ups"])
    
    with tab1:
        with st.form("follow_up_form"):
            st.write("Add New Follow-up Entry")
            dealership = st.text_input("Dealership Name")
            phone = st.text_input("Phone Number")
            email = st.text_input("Email Address")
            message = st.text_area("Message Sent", height=100)
            needs_followup = st.checkbox("Needs Follow-up")
            
            if st.form_submit_button("Add Follow-up Entry", type="primary"):
                if dealership and (phone or email):
                    new_followup = pd.DataFrame([[
                        dealership, phone, email, message, 
                        datetime.now().strftime("%Y-%m-%d %H:%M"), needs_followup
                    ]], columns=st.session_state.follow_up_log.columns)
                    
                    st.session_state.follow_up_log = pd.concat([st.session_state.follow_up_log, new_followup], ignore_index=True)
                    st.success("Follow-up entry added!")
                    st.rerun()
                else:
                    st.error("Please provide dealership name and at least phone or email")
    
    with tab2:
        if not st.session_state.follow_up_log.empty:
            st.dataframe(st.session_state.follow_up_log, use_container_width=True)
            
            # Show pending follow-ups
            pending = st.session_state.follow_up_log[st.session_state.follow_up_log["Needs Follow-Up"] == True]
            if not pending.empty:
                st.subheader("🔔 Pending Follow-ups")
                st.dataframe(pending, use_container_width=True)
        else:
            st.info("No follow-up entries yet.")

def show_contacts():
    st.subheader("📞 Contact Management")
    handle_contact_management()

def handle_contact_management():
    tab1, tab2 = st.tabs(["Add Contact", "View Contacts"])
    
    with tab1:
        with st.form("contact_form"):
            st.write("Add New Contact")
            name = st.text_input("Contact Name")
            phone = st.text_input("Phone Number")
            contact_type = st.selectbox("Contact Type", ["Seller", "Buyer", "Dealer", "Other"])
            associated_vin = st.selectbox("Associated VIN (Optional)", 
                                       ["None"] + st.session_state.crm_data["VIN"].tolist() 
                                       if not st.session_state.crm_data.empty else ["None"])
            
            if st.form_submit_button("Add Contact", type="primary"):
                if name and phone:
                    vin_value = associated_vin if associated_vin != "None" else ""
                    new_contact = pd.DataFrame([[name, phone, contact_type, vin_value]], 
                                             columns=st.session_state.contact_data.columns)
                    st.session_state.contact_data = pd.concat([st.session_state.contact_data, new_contact], ignore_index=True)
                    st.success("Contact added!")
                    st.rerun()
                else:
                    st.error("Please provide name and phone number")
    
    with tab2:
        if not st.session_state.contact_data.empty:
            st.dataframe(st.session_state.contact_data, use_container_width=True)
        else:
            st.info("No contacts yet.")

def show_dealer_tools():
    st.subheader("🛠️ Professional Dealer Tools")
    
    tab1, tab2, tab3 = st.tabs(["Offer Sheet Generator", "AI Pitch Assistant", "MMR Calculator"])
    
    with tab1:
        handle_offer_sheet()
    with tab2:
        handle_ai_pitch()
    with tab3:
        handle_mmr_calculator()

def handle_offer_sheet():
    st.write("Generate Professional Offer Sheet")
    
    col1, col2 = st.columns(2)
    with col1:
        customer_name = st.text_input("Customer Name")
        vehicle_info = st.text_input("Vehicle Info", placeholder="2020 Toyota Camry")
        offer_amount = st.number_input("Offer Amount ($)", min_value=0, step=100)
    with col2:
        trade_value = st.number_input("Trade-in Value ($)", min_value=0, step=100)
        financing_rate = st.number_input("Financing Rate (%)", min_value=0.0, max_value=30.0, step=0.1)
        monthly_payment = st.number_input("Est. Monthly Payment ($)", min_value=0, step=10)
    
    if st.button("Generate Offer Sheet", type="primary"):
        if customer_name and vehicle_info and offer_amount > 0:
            generate_offer_sheet(customer_name, vehicle_info, offer_amount, trade_value, financing_rate, monthly_payment)
        else:
            st.error("Please fill in required fields")

def generate_offer_sheet(customer_name, vehicle_info, offer_amount, trade_value, financing_rate, monthly_payment):
    offer_sheet = f"""
    **VEHICLE PURCHASE OFFER**
    
    **Customer:** {customer_name}
    **Date:** {datetime.now().strftime("%B %d, %Y")}
    **Vehicle:** {vehicle_info}
    
    ---
    
    **FINANCIAL DETAILS:**
    - Vehicle Price: ${offer_amount:,.2f}
    - Trade-in Value: ${trade_value:,.2f}
    - Net Amount: ${offer_amount - trade_value:,.2f}
    - Financing Rate: {financing_rate}% APR
    - Estimated Monthly Payment: ${monthly_payment:,.2f}
    
    ---
    
    **TERMS & CONDITIONS:**
    - Offer valid for 48 hours
    - Subject to financing approval
    - All prices plus tax, title, and fees
    - Trade-in subject to inspection
    
    **Dealer:** VelocityCarDeals
    **Contact:** theofficialadrodas56@gmail.com
    """
    
    st.markdown(offer_sheet)
    st.download_button(
        label="Download Offer Sheet",
        data=offer_sheet,
        file_name=f"offer_sheet_{customer_name.replace(' ', '_')}.txt",
        mime="text/plain"
    )

def handle_ai_pitch():
    st.write("AI-Powered Sales Pitch Assistant")
    
    customer_type = st.selectbox("Customer Type", ["First-time buyer", "Returning customer", "Trade-in customer", "Cash buyer"])
    vehicle_type = st.selectbox("Vehicle Type", ["Sedan", "SUV", "Truck", "Sports Car", "Luxury", "Economy"])
    budget_range = st.selectbox("Budget Range", ["Under $15K", "$15K-$25K", "$25K-$40K", "$40K+"])
    
    if st.button("Generate Sales Pitch", type="primary"):
        generate_sales_pitch(customer_type, vehicle_type, budget_range)

def generate_sales_pitch(customer_type, vehicle_type, budget_range):
    pitches = {
        "First-time buyer": f"Welcome! As a first-time buyer, we understand this is a big decision. Our {vehicle_type.lower()} in the {budget_range} range offers reliability, safety, and great value. We provide comprehensive warranties and financing options tailored for first-time buyers.",
        "Returning customer": f"Great to have you back! Based on your previous experience with us, I know you appreciate quality and service. This {vehicle_type.lower()} in your {budget_range} budget continues our tradition of excellence with enhanced features and reliability.",
        "Trade-in customer": f"Perfect timing for a trade-in! Your current vehicle has served you well, and this {vehicle_type.lower()} represents the next step up. With trade-in value applied to this {budget_range} vehicle, you're getting exceptional value and upgraded features.",
        "Cash buyer": f"Excellent! As a cash buyer, you have significant negotiating power. This {vehicle_type.lower()} in the {budget_range} range represents outstanding value, and with cash purchase, we can offer additional incentives and immediate ownership benefits."
    }
    pitch = pitches.get(customer_type, "Let me help you find the perfect vehicle for your needs!")
    st.success("Generated Sales Pitch:")
    st.markdown(f"**{pitch}**")
    st.write("**Key talking points:**")
    st.write("• Emphasize value proposition")
    st.write("• Highlight safety and reliability features")  
    st.write("• Mention warranty and service benefits")
    st.write("• Create urgency with limited-time offers")

def handle_mmr_calculator():
    st.write("Market Maker Report (MMR) Calculator")
    col1, col2 = st.columns(2)
    with col1:
        mmr_make = st.text_input("Make", key="mmr_make")
        mmr_model = st.text_input("Model", key="mmr_model")
        mmr_year = st.number_input("Year", min_value=1980, max_value=2030, key="mmr_year")
    with col2:
        mileage = st.number_input("Mileage", min_value=0, step=1000, key="mmr_mileage")
        condition = st.selectbox("Condition", ["Excellent", "Good", "Fair", "Poor"])
    if st.button("Calculate MMR", type="primary"):
        if mmr_make and mmr_model and mmr_year:
            calculate_mmr(mmr_make, mmr_model, mmr_year, mileage, condition)
        else:
            st.error("Please fill in vehicle details")

def calculate_mmr(make, model, year, mileage, condition):
    # Simplified MMR calculation (replace with real MMR API)
    base_value = 25000
    mileage_penalty = (mileage // 10000) * 500
    condition_factor = {
        "Excellent": 1.05,
        "Good": 1.0,
        "Fair": 0.9,
        "Poor": 0.8
    }
    value = base_value - mileage_penalty
    value *= condition_factor.get(condition, 1.0)
    value = max(value, 2000)  # Minimum value
    st.success(f"Estimated MMR for {year} {make} {model}: ${value:,.2f}")

# Initialize session state on first run
if "initialized" not in st.session_state:
    initialize_session_state()
    st.session_state.initialized = True

# Run the main application
if __name__ == "__main__":
    main()
