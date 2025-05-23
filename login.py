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
    authenticator.logout(button_name = "Logout")
    from services.account_management_system import AMS
    email = st.session_state.get("email")
    customer = AMS(email = email)
    
    st.write(f'Welcome *{customer.name}* ({email})')
    st.title('Account Details')

    st.subheader("Bank Accounts", divider = "grey")
    st.dataframe(customer.df_account, hide_index = True)
    
    col1, col2 = st.columns([0.88, 0.12])
    col1.subheader("Recent Transactions", divider = "grey")
    col2.selectbox(label = "Items", options = [5, 10, 20], index = 0, key = "n_records", label_visibility = "collapsed")
    st.dataframe(customer.df_transaction_history, hide_index = True)
    
    
    #         css = """.st-emotion-cache-7czcpc {
#     display: block;
#     margin: auto;
# }"""

#         st.markdown(f'<style>{css}</style>', unsafe_allow_html = True)


    st.subheader("Services", divider = "grey")
    
    # cols = st.columns(4)
    
    # with cols[0].container(height = 180):
    #     st.image("assets/statement.png", width = 80)
    #     get_statement_btn = st.button(label = "Get Statement", key = "statement", help = "Get bank statement", use_container_width = True)
        

    # with cols[1].container(height = 180):
    #     st.image("assets/send_money.png", width = 80)
    #     send_money_btn = st.button(label = "Send Money", key = "transact", help = "Send money to others", use_container_width = True)
    
    tab1, tab2 = st.tabs(["Statements", "Send Money"])
    
    
    # if get_statement_btn:
    with tab1:
        with st.form(key = 'get_statement_form'):
            download_flg = False
            download_file = ""
            st.subheader('Get Statement', divider = "red")
            col1, col2 = st.columns([0.5, 0.5])
            n_transactions = col1.number_input(label = "Number of Transactions", min_value = 1, max_value = 100, value = 5)
            submit_form = st.form_submit_button(label = "Confirm")
            
            if submit_form:
                df_transaction_history = customer.get_statement(n_transactions, mode = "df")
                st.dataframe(df_transaction_history, hide_index = True)
                download_file = customer.generate_statement_pdf(n_transactions)
                with open (download_file, "rb") as f:
                    download_file = f.read()
                download_flg = True
            
        st.download_button(label = "Download Statement", data = download_file, file_name = f"Statement_{customer.customer_id}.pdf", mime = 'application/pdf', disabled = not download_flg)
    
    # if send_money_btn:
    with tab2:
        with st.form(key = 'send_money_form', clear_on_submit = True):
            st.subheader('Transact', divider = "red")
            col1, col2, col3 = st.columns([0.45, 0.1, 0.45])
            from_account = col1.selectbox(label = "From Account", options = customer.df_account["ACCOUNT_NUMBER"].to_list())
            col2.write("")
            col2.write("")
            col2.markdown("❯❯❯❯")
            to_account = col3.selectbox(label = "To Account", options = customer.df_account["ACCOUNT_NUMBER"].to_list())
            amount = st.number_input("Amount", value = None, step = 1, placeholder = "Enter Amount")
            with st.expander(label = "Settings", expanded = True):
                col1, col2 = st.columns([0.5,0.5])
                location = col1.selectbox(label = "Location", options = ["Kolkata", "Delhi", "Boston", "Bali", "London", "Moscow"])
                device = col2.selectbox(label = "Device", options = ["Mobile: 10.12.42.12", "Mobile: 34.134.10.1", "Browser: 56.12.1.7", "Browser: 4.12.6.70"])
            submit_form = st.form_submit_button(label = "Send Money")
            
    
elif st.session_state.get('authentication_status') is False:
    st.error('Username/password is incorrect')
elif st.session_state.get('authentication_status') is None:
    st.info('ⓘ Please enter your username and password')
