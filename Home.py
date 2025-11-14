import streamlit as st
from credentials import USER_CREDENTIALS
import time
from dashboards import orders_dashboard, customer_dashboard, salesperformance_dashboard, customersatisfaction_dashboard, powerbi_dashboards

st.set_page_config(page_title="Main Dashboard", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""

def login_page():

    # Reduce page padding (top/bottom)
    st.markdown("""
    <style>
    .block-container {
        padding-top: 5rem;
        padding-bottom: 2rem;
        max-width: 600px;        
    }
                
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='login-box'>", unsafe_allow_html=True)

    st.markdown(
        "<h3 style='text-align:center; color:#FF9900;'>🔒 Login to AMAZON DATA ANALYSIS</h3>",
        unsafe_allow_html=True
    )

    username = st.text_input("👤 Username")
    password = st.text_input("🔑 Password", type="password")

    if st.button("Login"):
        if USER_CREDENTIALS.get(username) == password:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.success("✅ Welcome Pooja Pravallika Anthati")
            time.sleep(1)
            st.rerun()
        else:
            st.error("❌ Invalid username or password")

    st.markdown("</div>", unsafe_allow_html=True)

def main_page():   
    page_bg_color = """
        <style>
        [data-testid="stAppViewContainer"] {
            background: linear-gradient(135deg, #FF9900, #232F3E);
            color: white;
        }
        [data-testid="stHeader"] {
            background: rgba(0,0,0,0);
        }
        </style>
        """
    st.markdown(page_bg_color, unsafe_allow_html=True)
    st.image("https://images.seeklogo.com/logo-png/40/1/amazon-logo-png_seeklogo-408548.png", width=400)


# Sidebar Navigation
dashboards_dict={
    "Home": main_page,
    "Orders Dashboard" : orders_dashboard.render,
    "Customer Dashboard" : customer_dashboard.render,
    "Product Sales Performance Dashboard" : salesperformance_dashboard.render,
    "Customer Satisfaction Dashboard" : customersatisfaction_dashboard.render,
    "Power BI Dashboards" : powerbi_dashboards.render

}
# Render the appropriate page
if st.session_state["logged_in"]:
    page = st.sidebar.radio("Go to", list(dashboards_dict.keys()))

    # Logout button
    if st.sidebar.button("Logout"):
        st.session_state["logged_in"] = False
        st.rerun()

    dashboards_dict[page]()
else:
    login_page()