import streamlit as st
import json
import pandas as pd
from datetime import datetime
from utils.sql_validator import validate_sql_query
from utils.schema_validator import validate_schema
from utils.eden_ai_client import generate_sql_query
from utils.sql_dialects import SQLDialectConverter
from utils.query_optimizer import QueryOptimizer
from utils.query_history import QueryHistory
from utils.schema_visualizer import SchemaVisualizer
from utils.error_handler import SQLErrorHandler

# Page config
st.set_page_config(
    page_title="SQL SAGE by AiVERSE",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("assets/custom.css")

# Initialize components
if 'query_history' not in st.session_state:
    st.session_state.query_history = QueryHistory()
if 'schema' not in st.session_state:
    st.session_state.schema = None
if 'sql_query' not in st.session_state:
    st.session_state.sql_query = None
if 'selected_dialect' not in st.session_state:
    st.session_state.selected_dialect = 'mysql'

# Initialize utilities
dialect_converter = SQLDialectConverter()
query_optimizer = QueryOptimizer()

# Sidebar
with st.sidebar:
    st.title("⚙️ Settings")

    # SQL Dialect Selection
    st.subheader("SQL Dialect")
    selected_dialect = st.selectbox(
        "Select SQL Dialect",
        options=list(SQLDialectConverter.SUPPORTED_DIALECTS.keys()),
        format_func=lambda x: SQLDialectConverter.SUPPORTED_DIALECTS[x]
    )

    if selected_dialect != st.session_state.selected_dialect:
        st.session_state.selected_dialect = selected_dialect
        if st.session_state.sql_query:
            st.session_state.sql_query = dialect_converter.convert_query(
                st.session_state.sql_query,
                selected_dialect
            )

    # Schema upload and visualization
    st.subheader("Database Schema")
    schema_file = st.file_uploader("Upload Schema (JSON)", type=['json'])
    if schema_file:
        try:
            schema_content = json.load(schema_file)
            if validate_schema(schema_content):
                st.session_state.schema = schema_content
                if st.session_state.schema:
                    visualizer = SchemaVisualizer(st.session_state.schema)
                    st.plotly_chart(visualizer.get_plotly_figure(), use_container_width=True)
                st.success("Schema uploaded successfully!")
            else:
                st.error("Invalid schema format")
        except Exception as e:
            st.error(f"Error parsing schema: {str(e)}")

    # Query History
    st.subheader("Query History")
    if st.button("Show Recent Queries"):
        recent_queries = st.session_state.query_history.get_recent_queries()
        for query in recent_queries:
            with st.expander(f"Query from {query['timestamp']}"):
                st.text(query['natural_query'])
                st.code(query['sql_query'], language="sql")
                if st.button("Use This Query", key=query['timestamp']):
                    st.session_state.sql_query = query['sql_query']
                    st.rerun()

# Main content
st.title("🔮 SQL SAGE by AiVERSE")
st.markdown("### AI-Powered Natural Language to SQL Query Generator")

# Input section with suggestions
nl_query = st.text_area(
    "Enter your query in natural language",
    height=100,
    placeholder="Example: Show me all customers who made purchases in the last month"
)

# Generate button with loading animation
if st.button("Generate SQL Query", type="primary"):
    if nl_query:
        try:
            with st.spinner("🎭 Analyzing your query..."):
                # Generate SQL
                sql_query = generate_sql_query(
                    nl_query,
                    schema=st.session_state.schema
                )

                # Validate and optimize
                if validate_sql_query(sql_query):
                    optimized_query, suggestions = query_optimizer.optimize_query(
                        sql_query,
                        st.session_state.schema
                    )

                    # Convert to selected dialect
                    final_query = dialect_converter.convert_query(
                        optimized_query,
                        st.session_state.selected_dialect
                    )

                    # Save to history
                    st.session_state.query_history.add_query(
                        nl_query,
                        final_query,
                        st.session_state.selected_dialect
                    )

                    # Update session state
                    st.session_state.sql_query = final_query

                    # Show optimization suggestions
                    if suggestions:
                        with st.expander("📊 Query Optimization Suggestions"):
                            for suggestion in suggestions:
                                st.info(suggestion)
                else:
                    error_msg, color, suggestion = SQLErrorHandler.format_error(
                        "Invalid SQL query generated"
                    )
                    st.error(error_msg)
                    st.info(f"💡 Suggestion: {suggestion}")

        except Exception as e:
            error_msg, color, suggestion = SQLErrorHandler.format_error(str(e))
            st.error(error_msg)
            st.info(f"💡 Suggestion: {suggestion}")
    else:
        st.warning("Please enter a query first")

# Display SQL if available
if st.session_state.sql_query:
    st.markdown("### Generated SQL Query")
    st.code(st.session_state.sql_query, language="sql")

    # Export options
    export_format = st.selectbox(
        "Export Format",
        options=["CSV", "Excel"],
        key="export_format"
    )

    if st.button("Export Query"):
        try:
            # Create sample data for export
            data = pd.DataFrame({
                "query": [st.session_state.sql_query],
                "dialect": [st.session_state.selected_dialect],
                "timestamp": [datetime.now().isoformat()]
            })

            if export_format == "CSV":
                data.to_csv("query_export.csv", index=False)
                st.success("Query exported to CSV!")
            else:
                data.to_excel("query_export.xlsx", index=False)
                st.success("Query exported to Excel!")
        except Exception as e:
            st.error(f"Error exporting query: {str(e)}")

# Usage instructions
with st.expander("How to use SQL SAGE"):
    st.markdown("""
    1. **Enter your query** in natural language
    2. Optionally **upload your database schema** for more accurate results
    3. Select your preferred **SQL dialect**
    4. Click **Generate SQL Query** to convert your query
    5. Review optimization suggestions and error messages
    6. Use the built-in copy button in the code block to copy the generated SQL
    7. Export your query in CSV or Excel format

    For best results:
    - Be specific in your natural language query
    - Include relevant table names if known
    - Upload your schema for context-aware generation
    - Check the optimization suggestions for better performance
    """)