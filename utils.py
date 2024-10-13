import streamlit as st

def show_error_message(message):
    st.error(message)

def show_success_message(message):
    st.success(message)

def show_info_message(message):
    st.info(message)

def confirm_action(message):
    return st.button(message)
