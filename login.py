import streamlit as st
import streamlit_authenticator as stauth
from lib import utils

config = utils.get_config()

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)


st.markdown(
    f"""
<style>
    .st-emotion-cache-1xgtwnd:before {{
        content: "🏦 GlobalPay";
        font-weight: bold;
        font-size: xx-large;
    }}
</style>""",
        unsafe_allow_html=True,
    )

authenticator.login(location = 'main')


if st.session_state.get('authentication_status'):
    authenticator.logout()
    from services.account_management_system import AMS
    email = st.session_state.get("email")
    customer = AMS(email = email)
    
    st.write(f'Welcome *{customer.name}* ({email})')
    st.title('Account Details')

    st.subheader("Bank Accounts", divider = "grey")
    st.dataframe(customer.df_account, hide_index = True)
    
    col1, col2 = st.columns([0.88, 0.12])
    col1.subheader("Transaction History", divider = "grey")
    col2.selectbox(label = "", options = [5, 10, 20], index = 0, key = "n_records")
    st.dataframe(customer.df_transaction_history, hide_index = True)
    
    
elif st.session_state.get('authentication_status') is False:
    st.error('Username/password is incorrect')
elif st.session_state.get('authentication_status') is None:
    st.info('ⓘ Please enter your username and password')


