import streamlit as st
from prediction import predict  # Ensure this is correctly linked to your prediction_helper.py
import os
from groq import Groq
from dotenv import load_dotenv
import time

# Load environment variables from .env file
load_dotenv()

def load_api_key():
    # 1️⃣ Streamlit Cloud
    if "API_KEY" in st.secrets:
        return st.secrets["API_KEY"], "streamlit"

    # 2️⃣ AWS / Docker / Local
    env_key = os.getenv("API_KEY")
    if env_key:
        return env_key, "env"
    return None, None

# Set the page configuration and title
st.set_page_config(page_title="Credit Risk Modelling", page_icon="📊", layout="wide")
st.markdown('<h1 class="main-header">🏦 Credit Risk Assessment System</h1>', unsafe_allow_html=True)
st.title("Credit Risk Modelling")

tab1, tab2 = st.tabs([
    "Credit Score Prediction",
    "Chatbot"
])

# ------------------------------------------------------------------------------------------
# TAB 1: PREDICTION
# ------------------------------------------------------------------------------------------
with tab1:
    # Row 1: Personal & Loan Details
    row1_col1, row1_col2 = st.columns(2)
    
    with row1_col1:
        with st.container(border=True):
            st.subheader("👤 Personal & Financial")
            
            col_a, col_b = st.columns(2)
            with col_a:
                age = st.number_input('Age', min_value=18, max_value=100, value=28)
                residence_type = st.selectbox('Residence Type', ['Owned', 'Rented', 'Mortgage'])
            with col_b:
                income = st.number_input('Annual Income (₹)', min_value=0, value=1200000, step=50000)
                st.caption(f"Monthly: ₹{income//12:,.0f}")

    with row1_col2:
        with st.container(border=True):
            st.subheader("💰 Loan Details")
            
            col_a, col_b = st.columns(2)
            with col_a:
                loan_amount = st.number_input('Loan Amount (₹)', min_value=0, value=2560000, step=50000)
                loan_purpose = st.selectbox('Purpose', ['Education', 'Home', 'Auto', 'Personal'])
            with col_b:
                loan_tenure_months = st.number_input('Tenure (Months)', min_value=0, value=36)
                loan_type = st.selectbox('Loan Type', ['Unsecured', 'Secured'])
            
            if income > 0:
                loan_to_income_ratio = loan_amount / income
                st.progress(min(loan_to_income_ratio, 1.0))
                st.caption(f"Loan-to-Income Ratio: {loan_to_income_ratio:.2f}")

    # Row 2: Credit History & Behavior (Full Width)
    with st.container(border=True):
        st.subheader("📈 Credit History")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_dpd_per_delinquency = st.number_input('Avg DPD', min_value=0, value=20)
        with col2:
            deliquency_ratio = st.number_input('Delinquency Ratio (%)', 0, 100, 30)
        with col3:
            credit_utilization_ratio = st.number_input('Credit Utilization (%)', 0, 100, 30)
        with col4:
            num_open_accounts = st.number_input('Open Accounts', 1, 4, 2)

    st.markdown("---")
    
    # Calculate Button centered
    col_spacer_l, col_btn, col_spacer_r = st.columns([2, 1, 2])
    with col_btn:
        calculate_button = st.button('🚀 Calculate Risk', type="primary", use_container_width=True)

    # Button to calculate risk
    if calculate_button:
        with st.spinner('🔍 Analyzing...'):
            time.sleep(0.5)
            
        probability, credit_score, rating = predict(age, income, loan_amount, loan_tenure_months, avg_dpd_per_delinquency,
                                                    deliquency_ratio, credit_utilization_ratio, num_open_accounts,
                                                    residence_type, loan_purpose, loan_type)
        
        # Store results in session state for chatbot access
        st.session_state['credit_score'] = credit_score
        st.session_state['rating'] = rating
        st.session_state['probability'] = probability

        # Modern Results Display
        st.markdown("### 📊 Assessment Result")
        res_col1, res_col2, res_col3 = st.columns(3)
        
        with res_col1:
            st.metric("Default Probability", f"{probability:.2%}", delta_color="inverse")
        with res_col2:
            st.metric("Credit Score", credit_score)
        with res_col3:
            st.metric("Risk Rating", rating)
        
        st.info("💡 Tip: Use the 'Chatbot' tab to ask AI for advice on improving this score.")


# ------------------------------------------------------------------------------------------
# SIDEBAR - API CONFIGURATION
# ------------------------------------------------------------------------------------------
with st.sidebar:
    st.header("🤖 AI Settings")
    # Try to get API key from environment variable first
    api_key, source = load_api_key()

if api_key:
    if source == "streamlit":
        st.success("✅ Secure Mode: API Key loaded from Streamlit Secrets")
    else:
        st.success("✅ Secure Mode: API Key loaded from Environment Variables")
else:
    api_key_input = st.text_input("Groq API Key", type="password", placeholder="Enter gsk_... key here")
    # api_key = api_key_input.strip() if api_key_input else None
    # st.error("❌ API Key not found. Configure secrets or environment variables.")
    # env_api_key = os.getenv("GROQ_API_KEY")
    
    # if env_api_key:
    #     api_key = env_api_key
    #     st.success("✅ Secure Mode: API Key Loaded from Environment")
    #     # No text input shown for maximum security
    # else:
    #     api_key_input = st.text_input("Groq API Key", type="password", placeholder="Enter gsk_... key here")
    #     api_key = api_key_input.strip() if api_key_input else None
    
    if api_key:
        if not env_api_key: # Only show this if not already shown above
            st.success("API Key Detected! Brain Active 🧠")
        st.markdown("### Model Sizing")
        model_choice = st.selectbox("Select Model", ["llama-3.1-8b-instant", "llama-3.3-70b-versatile", "mixtral-8x7b-32768"], index=0)
    else:
        st.error("⚠️ GROQ API Key Required")
        model_choice = None

# ------------------------------------------------------------------------------------------
# CHATBOT (ONLINE ONLY)
# ------------------------------------------------------------------------------------------

with tab2:
    st.markdown("## 💬 Intelligent Credit Assistant")
    if not api_key:
        st.warning("🔒 This feature requires an API Key. Please configure it in the .env file or sidebar.")

    # Store chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        # Add an initial greeting
        st.session_state.chat_history.append(("Bot", "Hello! I am your AI Credit Analyst. I can explain your risk assessment and suggest improvements."))

    # Display conversation
    for speaker, msg in st.session_state.chat_history:
        with st.chat_message("user" if speaker == "You" else "assistant"):
            st.write(msg)

    # Display input
    user_input = st.chat_input("Ask a question about your credit (e.g., 'How do I improve?')")

    if user_input:
        if not api_key:
            st.error("Please add your Groq API Key to proceed.")
        else:
            # Display user message immediately
            with st.chat_message("user"):
                st.write(user_input)
            st.session_state.chat_history.append(("You", user_input))
            
            # 1. Gather User Data context
            user_data_context = {
                "credit_score": st.session_state.get("credit_score", "not calculated yet"),
                "risk_rating": st.session_state.get("rating", "N/A"),
                "probability_of_default": f"{st.session_state.get('probability', 0):.2%}" if "probability" in st.session_state else "N/A",
                "utilization_ratio": f"{credit_utilization_ratio}%",
                "days_past_due": avg_dpd_per_delinquency,
                "delinquency_ratio": f"{deliquency_ratio}%",
                "loan_amount": loan_amount,
                "income": income
            }

            # 2. Generate Response (Direct API Call)
            try:
                client = Groq(api_key=api_key)
                
                # Construct system prompt
                system_prompt = f"""
                You are an expert Credit Risk Analyst. 
                
                USER DATA:
                {user_data_context}
                
                INSTRUCTIONS:
                1. **Conversational Mode**:
                   - IF the user says "Hello", "Thanks", "Bye", "Exit", "Help", or similar social triggers:
                   - Respond naturally, politely, and briefly (1-2 sentences).
                   - DO NOT use the strict Analysis/Tips format for these.
                
                2. **Analyst Mode** (For credit/finance questions):
                   - IF the user asks about scores, money, improvement, or risk:
                   - Follow the CRITICAL FORMATTING RULES below.

                CRITICAL FORMATTING RULES (For Analyst Mode only):
                1. DO NOT use LaTeX formatting (no dollar signs like $ or $$ for math/currency). Use plain text (e.g., "INR 50,000" or "Rs.").
                2. Keep the response SHORT and readable.
                3. Structure your answer EXACTLY as follows:
                   - **Analysis**: 3-4 bullet points explaining the situation.
                   - **Tips**: 2-3 actionable tips to improve.
                4. Do not exceed these limits.
                """
                
                completion = client.chat.completions.create(
                    model=model_choice,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_input}
                    ],
                    temperature=0.7,
                    max_tokens=512,
                    stream=True
                )
                
                # Stream the response
                def generate_stream():
                    for chunk in completion:
                        if chunk.choices[0].delta.content is not None:
                            yield chunk.choices[0].delta.content

                with st.chat_message("assistant"):
                    bot_reply = st.write_stream(generate_stream())
                
                st.session_state.chat_history.append(("Bot", bot_reply))

            except Exception as e:
                st.error(f"API Error: {e}")
            
            # Force refresh to keep layout clean and input bar at bottom
            st.rerun()
