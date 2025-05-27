import streamlit as st
import streamlit_authenticator as stauth
from lib import utils
import subprocess

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
    from services.account_management_system import AMS
    email = st.session_state.get("email")
    customer = AMS(email = email)
    
    col1, col2 = st.columns([0.88, 0.12])
    col1.header(f"{customer.name}  \n **Customer ID:** *{customer.customer_id}*  \n **Email:** *{email}*", divider = "red")
    
    with col2:
        authenticator.logout(button_name = "Logout")


    st.subheader("Bank Accounts", divider = "grey")
    st.dataframe(customer.df_account, hide_index = True)
    
    col1, col2 = st.columns([0.88, 0.12])
    col1.subheader("Recent Transactions", divider = "grey")
    col2.selectbox(label = "Items", options = [5, 10, 20], index = 0, key = "n_records", label_visibility = "collapsed")
    
    for account in customer.accounts:
        st.markdown(f"##### Account: {account}")
        st.dataframe(customer.get_statement(account_number = account, n_transactions = st.session_state.n_records if "n_records" in st.session_state else 5, mode = "df"), hide_index = True)
    
    
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
            account = col1.selectbox("Account", options = customer.accounts)
            n_transactions = col2.number_input(label = "Number of Transactions", min_value = 1, max_value = 100, value = 5)
            submit_form = st.form_submit_button(label = "Confirm")
            
            if submit_form:
                df_transaction_history = customer.get_statement(account_number = account, n_transactions = n_transactions, mode = "df")
                st.dataframe(df_transaction_history, hide_index = True)
                download_file = customer.generate_statement_pdf(account_number = account, n_transactions = n_transactions)
                with open (download_file, "rb") as f:
                    download_file = f.read()
                download_flg = True
            
        st.download_button(label = "Download Statement", data = download_file, file_name = f"Statement_{customer.customer_id}.pdf", mime = 'application/pdf', disabled = not download_flg)
    
    # if send_money_btn:
    with tab2:
        with st.form(key = 'send_money_form', clear_on_submit = True):
            st.subheader('Transact', divider = "red")
            col1, col2, col3 = st.columns([0.45, 0.1, 0.45])
            account_list = customer.accounts
            from_account = col1.selectbox(label = "From Account", options = account_list)
            col2.write("")
            col2.write("")
            col2.markdown("❯❯❯❯")
            beneficiaries = customer.get_beneficiaries()
            to_account = col3.selectbox(label = "To Account", options = beneficiaries)
            
            amount = st.number_input("Amount", value = None, placeholder = "Enter Amount")
            description = st.selectbox("Description", options = ['Online Transfer', 'Grocery Store Purchase', 'Restaurant Bill Payment', 'Netflix Subscription', 'Amazon.com Purchase', 'Rent Payment', 'Utility Bill Payment', 'Gas Station Purchase', 'Coffee Shop Purchase', 'Salary Deposit', 'Interest Earned', 'Credit Card Payment', 'ACH Transfer from Jane Doe', 'PayPal Transfer Received', 'Walmart Purchase', 'Target Purchase', 'Mobile Phone Bill', 'Insurance Payment'])
            with st.expander(label = "Settings", expanded = False):
                col1, col2 = st.columns([0.5,0.5])
                location = col1.selectbox(label = "Location", options = ["Kolkata", "Delhi", "Boston", "Bali", "London", "Moscow"])
                device = col2.selectbox(label = "Device", options = ["Mobile: 10.12.42.12", "Mobile: 34.134.10.1", "Browser: 56.12.1.7", "Browser: 4.12.6.70"])
            submit_form = st.form_submit_button(label = "Send Money")
            
            if submit_form:
                
                # Check 1
                if from_account == to_account:
                    st.error("Sender and Receiver Account cannot be the same..!")
                
                # Check 2
                elif amount is None:
                    st.error("Please enter an amount to transfer..!")
                
                else:
                    from services.transaction_processing_engine import TPE
                    transaction = TPE(from_account, to_account, amount, description, location, device)
                    transaction.send_money(amount = amount)
        
                
    with st.sidebar:
        st.subheader("Datasets", divider = "red")
        btn_customer = st.button("Reset Customer")      
        btn_bank_dim = st.button("Reset Bank Dim")      
        btn_bank_accounts = st.button("Reset Bank Accounts")      
        btn_transaction_history = st.button("Reset Transaction History")      
        
        def run_subprocess(command):
            print(f"Executing Command: {command}")
            subprocess.run(command, shell = True, text = True)
            
        if btn_customer:
            command = f"{utils.get_path_env('VENV')} && python {utils.get_path_env('SCRIPT_DIR', 'load_customer.py')}"
            run_subprocess(command)
            st.rerun()
        
        if btn_bank_dim:
            command = f"{utils.get_path_env('VENV')} && python {utils.get_path_env('SCRIPT_DIR', 'bank_dim.py')}"
            run_subprocess(command)
            st.rerun()
        
        if btn_bank_accounts:
            command = f"{utils.get_path_env('VENV')} && python {utils.get_path_env('SCRIPT_DIR', 'load_bank_accounts.py')}"
            run_subprocess(command)
            st.rerun()
        
        if btn_transaction_history:
            command = f"{utils.get_path_env('VENV')} && python {utils.get_path_env('SCRIPT_DIR', 'load_transaction_history.py')}"
            run_subprocess(command)
            st.rerun()
        
elif st.session_state.get('authentication_status') is False:
    st.error('Username/password is incorrect')
elif st.session_state.get('authentication_status') is None:
    st.info('ⓘ Please enter your username and password')

