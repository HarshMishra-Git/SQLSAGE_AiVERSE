import streamlit as st
import json
from utils.sql_validator import validate_sql_query
from utils.schema_validator import validate_schema
from utils.eden_ai_client import generate_sql_query

# Page config
st.set_page_config(
    page_title="SQL SAGE by AiVERSE",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("assets/custom.css")

# Session state initialization
if 'schema' not in st.session_state:
    st.session_state.schema = None
if 'sql_query' not in st.session_state:
    st.session_state.sql_query = None
if 'show_copy_success' not in st.session_state:
    st.session_state.show_copy_success = False

# Sidebar
with st.sidebar:
    st.title("⚙️ Settings")

    # Schema upload
    st.subheader("Database Schema")
    schema_file = st.file_uploader("Upload Schema (JSON)", type=['json'])
    if schema_file:
        try:
            schema_content = json.load(schema_file)
            if validate_schema(schema_content):
                st.session_state.schema = schema_content
                st.success("Schema uploaded successfully!")
            else:
                st.error("Invalid schema format")
        except Exception as e:
            st.error(f"Error parsing schema: {str(e)}")

# Main content
st.title("🔮 SQL SAGE by AiVERSE")
st.markdown("### AI-Powered Natural Language to SQL Query Generator")

# Input section
nl_query = st.text_area(
    "Enter your query in natural language",
    height=100,
    placeholder="Example: Show me all customers who made purchases in the last month"
)

# Generate button
if st.button("Generate SQL Query", type="primary", key="generate"):
    if nl_query:
        try:
            with st.spinner("Generating SQL query..."):
                sql_query = generate_sql_query(
                    nl_query,
                    schema=st.session_state.schema
                )
                if validate_sql_query(sql_query):
                    st.session_state.sql_query = sql_query
                    st.session_state.show_copy_success = False
                else:
                    st.error("Generated query failed validation")
        except Exception as e:
            st.error(f"Error generating SQL query: {str(e)}")
    else:
        st.warning("Please enter a query first")

# Display SQL if available
if st.session_state.sql_query:
    st.markdown("### Generated SQL Query")

    # SQL query display
    query_container = st.container()
    with query_container:
        st.code(st.session_state.sql_query, language="sql")

        # Copy button in a more compact layout
        col1, col2, *_ = st.columns([1, 3, 8])
        with col1:
            if st.button("📋", key="copy"):
                st.write(st.clipboard(st.session_state.sql_query))
                st.session_state.show_copy_success = True
        with col2:
            if st.session_state.show_copy_success:
                st.success("Copied!")

# Usage instructions
with st.expander("How to use SQL SAGE"):
    st.markdown("""
    1. **Enter your query** in natural language
    2. Optionally **upload your database schema** for more accurate results
    3. Click **Generate SQL Query** to convert your query
    4. Use the **Copy** button to copy the generated SQL

    For best results:
    - Be specific in your natural language query
    - Include relevant table names if known
    - Upload your schema for context-aware generation
    """)