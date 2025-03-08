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

generate_btn = st.button("Generate SQL Query", type="primary")

if generate_btn and nl_query:
    try:
        with st.spinner("Generating SQL query..."):
            sql_query = generate_sql_query(
                nl_query,
                schema=st.session_state.schema
            )

            # Validate generated SQL
            if validate_sql_query(sql_query):
                # Create a container for the SQL output
                sql_container = st.container()

                with sql_container:
                    st.markdown("### Generated SQL Query")

                    # Display SQL in a single code block
                    st.code(sql_query, language="sql")

                    # Add copy button with success message
                    if st.button("📋 Copy SQL Query"):
                        st.write(st.clipboard(sql_query))
                        st.success("✅ SQL query copied to clipboard!")
            else:
                st.error("Generated query failed validation")

    except Exception as e:
        st.error(f"Error generating SQL query: {str(e)}")
else:
    if generate_btn:
        st.warning("Please enter a query first")

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