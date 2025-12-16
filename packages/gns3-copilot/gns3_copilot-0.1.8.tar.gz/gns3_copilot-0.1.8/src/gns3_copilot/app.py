"""
GNS3 Copilot Streamlit application entry point.

Main application module that initializes and runs the Streamlit-based
web interface for GNS3 Copilot with navigation between settings and chat pages.
"""

import streamlit as st

pg = st.navigation(
    [
        "ui_model/settings.py",
        "ui_model/chat.py",
        "ui_model/help.py"
    ],
    position="sidebar"
)
pg.run()

with st.sidebar:
    st.header("About")
    st.markdown(
"""
GNS3 Copilot is an AI-powered assistant designed to help network engineers withGNS3-related tasks.
It leverages advanced language models to provide insights, answer questions,
and assist with network simulations.
        
**Features:**
- Answer GNS3-related queries
- Provide configuration examples
- Assist with troubleshooting
        
**Usage:**
Simply type your questions or commands in the chat interface,
and GNS3 Copilot will respond accordingly.
        
**Note:** This is a prototype version. For more information,
visit the [GNS3 Copilot GitHub Repository](https://github.com/yueguobin/gns3-copilot).
"""
    )
