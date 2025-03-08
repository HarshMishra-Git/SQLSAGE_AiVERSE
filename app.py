"""SQL SAGE - AI-Powered SQL Query Generator"""
import streamlit as st
import json
import pandas as pd
from datetime import datetime
import time
from utils.sql_validator import validate_sql_query
from utils.schema_validator import validate_schema
from utils.eden_ai_client import generate_sql_query
from utils.sql_dialects import SQLDialectConverter
from utils.query_optimizer import QueryOptimizer
from utils.query_history import QueryHistory
from utils.schema_visualizer import SchemaVisualizer
from utils.error_handler import SQLErrorHandler
from utils.query_playground import QueryPlayground
from utils.user_preferences import UserPreferences

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
if 'playground' not in st.session_state:
    st.session_state.playground = QueryPlayground()
if 'user_preferences' not in st.session_state:
    st.session_state.user_preferences = UserPreferences()

# Initialize utilities
dialect_converter = SQLDialectConverter()
query_optimizer = QueryOptimizer()

# Create tabs for different features
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Query Generator",
    "Query Playground",
    "Schema Explorer",
    "Performance Metrics",
    "Settings"
])

with tab1:
    st.title("🔮 SQL SAGE by AiVERSE")
    st.markdown("### AI-Powered Natural Language to SQL Query Generator")

    # Input section with suggestions
    nl_query = st.text_area(
        "Enter your query in natural language",
        height=100,
        placeholder="Example: Show me all customers who made purchases in the last month"
    )

    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("Generate SQL Query", type="primary"):
            if nl_query:
                try:
                    start_time = time.time()
                    with st.spinner("🎭 Analyzing your query..."):
                        sql_query = generate_sql_query(
                            nl_query,
                            schema=st.session_state.schema
                        )

                        if validate_sql_query(sql_query):
                            optimized_query, suggestions = query_optimizer.optimize_query(
                                sql_query,
                                st.session_state.schema
                            )

                            final_query = dialect_converter.convert_query(
                                optimized_query,
                                st.session_state.selected_dialect
                            )

                            execution_time = time.time() - start_time
                            st.session_state.user_preferences.update_performance_metrics(
                                execution_time,
                                True
                            )

                            st.session_state.query_history.add_query(
                                nl_query,
                                final_query,
                                st.session_state.selected_dialect
                            )

                            st.session_state.sql_query = final_query

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
                            st.session_state.user_preferences.update_performance_metrics(
                                time.time() - start_time,
                                False
                            )

                except Exception as e:
                    error_msg, color, suggestion = SQLErrorHandler.format_error(str(e))
                    st.error(error_msg)
                    st.info(f"💡 Suggestion: {suggestion}")
            else:
                st.warning("Please enter a query first")

    with col2:
        st.markdown("### SQL Dialect")
        selected_dialect = st.selectbox(
            "Select SQL Dialect",
            options=list(SQLDialectConverter.SUPPORTED_DIALECTS.keys()),
            format_func=lambda x: SQLDialectConverter.SUPPORTED_DIALECTS[x],
            key="dialect_selector"
        )

        if selected_dialect != st.session_state.selected_dialect:
            st.session_state.selected_dialect = selected_dialect
            st.session_state.user_preferences.update_preference("dialect", selected_dialect)
            if st.session_state.sql_query:
                st.session_state.sql_query = dialect_converter.convert_query(
                    st.session_state.sql_query,
                    selected_dialect
                )

    if st.session_state.sql_query:
        st.markdown("### Generated SQL Query")
        st.code(st.session_state.sql_query, language="sql")

        col1, col2 = st.columns([1, 1])
        with col1:
            # Export options
            export_format = st.selectbox(
                "Export Format",
                options=["CSV", "Excel"]
            )

            if st.button("Export Query"):
                try:
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

        with col2:
            # Share query
            if st.button("Share Query"):
                annotation = st.text_area("Add notes (optional)")
                if st.button("Confirm Share"):
                    st.session_state.user_preferences.add_shared_query({
                        "query": st.session_state.sql_query,
                        "natural_query": nl_query,
                        "dialect": st.session_state.selected_dialect,
                        "annotation": annotation,
                        "shared_at": datetime.now().isoformat()
                    })
                    st.success("Query shared successfully!")

with tab2:
    st.title("🎮 Interactive Query Playground")
    test_query = st.text_area(
        "Enter your SQL query",
        height=150,
        help="Write your SQL query here to test it against the database"
    )

    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("Execute Query", type="primary"):
            if test_query:
                start_time = time.time()
                with st.spinner("🔍 Executing query..."):
                    results, error, suggestions = st.session_state.playground.execute_test_query(
                        test_query,
                        st.session_state.selected_dialect
                    )
                    execution_time = time.time() - start_time

                    if error:
                        st.error(error)
                        if suggestions:
                            st.info("💡 " + suggestions[0])
                        st.session_state.user_preferences.update_performance_metrics(
                            execution_time,
                            False
                        )
                    elif results is not None:
                        st.dataframe(results)
                        if suggestions:
                            with st.expander("📊 Query Optimization Suggestions"):
                                for suggestion in suggestions:
                                    st.info(suggestion)
                        st.session_state.user_preferences.update_performance_metrics(
                            execution_time,
                            True
                        )
            else:
                st.warning("Please enter a query to execute")

    with col2:
        with st.expander("📋 Available Tables"):
            tables = st.session_state.playground.db.get_table_schema().keys()
            for table in tables:
                st.markdown(f"**{table}**")
                preview = st.session_state.playground.get_table_preview(table)
                if preview is not None:
                    st.dataframe(preview, height=150)

with tab3:
    st.title("📊 Schema Explorer")
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

with tab4:
    st.title("📈 Performance Metrics")
    metrics = st.session_state.user_preferences.get_preference("performance_metrics")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Queries", metrics["total_queries"])
    with col2:
        success_rate = (metrics["successful_queries"] / metrics["total_queries"] * 100 
                       if metrics["total_queries"] > 0 else 0)
        st.metric("Success Rate", f"{success_rate:.1f}%")
    with col3:
        st.metric("Avg. Execution Time", f"{metrics['average_execution_time']:.3f}s")

    st.subheader("Recent Shared Queries")
    shared_queries = st.session_state.user_preferences.get_shared_queries()
    for query in shared_queries:
        with st.expander(f"Query shared on {query['shared_at']}"):
            st.text(query['natural_query'])
            st.code(query['sql_query'], language="sql")
            if query['annotation']:
                st.info(f"📝 Note: {query['annotation']}")

with tab5:
    st.title("⚙️ Settings")

    # Theme settings
    theme = st.selectbox(
        "Theme",
        options=["light", "dark"],
        index=0 if st.session_state.user_preferences.get_preference("theme") == "light" else 1
    )
    if theme != st.session_state.user_preferences.get_preference("theme"):
        st.session_state.user_preferences.update_preference("theme", theme)

    # Font size
    font_size = st.select_slider(
        "Font Size",
        options=["small", "medium", "large"],
        value=st.session_state.user_preferences.get_preference("font_size", "medium")
    )
    if font_size != st.session_state.user_preferences.get_preference("font_size"):
        st.session_state.user_preferences.update_preference("font_size", font_size)

    # Editor preferences
    show_line_numbers = st.checkbox(
        "Show Line Numbers",
        value=st.session_state.user_preferences.get_preference("show_line_numbers", True)
    )
    if show_line_numbers != st.session_state.user_preferences.get_preference("show_line_numbers"):
        st.session_state.user_preferences.update_preference("show_line_numbers", show_line_numbers)

    auto_complete = st.checkbox(
        "Enable Auto-Complete",
        value=st.session_state.user_preferences.get_preference("auto_complete", True)
    )
    if auto_complete != st.session_state.user_preferences.get_preference("auto_complete"):
        st.session_state.user_preferences.update_preference("auto_complete", auto_complete)

    # Connection profiles
    st.subheader("Connection Profiles")
    if st.button("Add New Connection Profile"):
        with st.form("new_connection"):
            profile_name = st.text_input("Profile Name")
            host = st.text_input("Host")
            port = st.text_input("Port")
            database = st.text_input("Database")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")

            if st.form_submit_button("Save Profile"):
                st.session_state.user_preferences.add_connection_profile({
                    "name": profile_name,
                    "host": host,
                    "port": port,
                    "database": database,
                    "username": username,
                    "password": password
                })
                st.success("Connection profile saved!")

    # Display existing profiles
    profiles = st.session_state.user_preferences.get_connection_profiles()
    for profile in profiles:
        with st.expander(f"Profile: {profile['name']}"):
            st.text(f"Host: {profile['host']}")
            st.text(f"Database: {profile['database']}")
            st.text(f"Username: {profile['username']}")

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
    8. Try the interactive playground to test your queries
    9. Explore the schema visualization for better understanding
    10. Monitor performance metrics in the new Performance Metrics tab.
    11. Customize the application's appearance and behavior in the Settings tab.


    For best results:
    - Be specific in your natural language query
    - Include relevant table names if known
    - Upload your schema for context-aware generation
    - Check the optimization suggestions for better performance
    """)