import streamlit as st
import google.generativeai as genai
import os

# --- PAGE SETUP ---
st.set_page_config(page_title="Realtor AI Calculator", page_icon="🏠")

st.title("🏠 AI Deal Analyzer for Wholesalers")
st.write("Enter the property details below to get a deal breakdown.")

# --- SECURITY: PASSWORD PROTECTION ---
def check_password():
    """Returns `True` if the user had the correct password."""
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False

    if st.session_state.password_correct:
        return True

    password_input = st.text_input("Enter Access Password", type="password")
    if st.button("Login"):
        # We access the password securely from Streamlit Secrets
        if password_input == st.secrets["APP_PASSWORD"]:
            st.session_state.password_correct = True
            st.rerun()
        else:
            st.error("😕 Password incorrect")
    return False

if not check_password():
    st.stop(#)  # Stop execution if password is wrong

# --- BACKEND CONFIGURATION ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error("Missing Google API Key in Secrets.")
    st.stop()

# --- USER INPUTS ---
col1, col2 = st.columns(2)
with col1:
    arv = st.number_input("After Repair Value ($)", min_value=0, value=300000)
    repairs = st.number_input("Estimated Repairs ($)", min_value=0, value=40000)
with col2:
    asking_price = st.number_input("Seller Asking Price ($)", min_value=0, value=150000)
    wholesale_fee = st.number_input("Your Wholesale Fee ($)", min_value=0, value=10000)

property_notes = st.text_area("Additional Property Notes (Condition, Location, etc.)")

# --- THE AI BRAIN ---
if st.button("Analyze Deal"):
    with st.spinner("Crunching the numbers..."):
        try:
            # LOGIC GUARDRAILS
            system_instruction = """
            You are an expert Real Estate Investment Analyst. 
            Your ONLY job is to analyze this deal. 
            Do NOT answer questions about unrelated topics. 
            Be conservative in your estimates.
            """
            
            model = genai.GenerativeModel('gemini-pro')
            
            prompt = f"""
            {system_instruction}
            
            Analyze this wholesale deal:
            - ARV: ${arv}
            - Repairs: ${repairs}
            - Asking Price: ${asking_price}
            - Desired Wholesale Fee: ${wholesale_fee}
            - Notes: {property_notes}
            
            Please provide:
            1. The Maximum Allowable Offer (MAO) based on the 70% rule.
            2. A verdict: Is this a good deal?
            3. A list of risks based on the notes.
            """
            
            response = model.generate_content(prompt)
            st.markdown(response.text)
            
        except Exception as e:
            st.error(f"An error occurred: {e}")


