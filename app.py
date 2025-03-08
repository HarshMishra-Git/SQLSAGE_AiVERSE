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
if 'example_query' not in st.session_state:
    st.session_state.example_query = ""
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "Query Generator"

# Initialize utilities
dialect_converter = SQLDialectConverter()
query_optimizer = QueryOptimizer()

# Landing Page
with st.container():
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.title("🔮 SQL SAGE by AiVERSE")
        st.markdown("### AI-Powered Natural Language to SQL Query Generator")
        
        st.markdown("""
        Transform your data queries effortlessly with SQL SAGE - the intelligent assistant that converts 
        natural language into precise SQL queries. No more struggling with complex syntax!
        """)
        
        features = {
            "💬 Natural Language Processing": "Simply describe what you need in plain English",
            "⚡ Instant SQL Generation": "Get accurate SQL queries in seconds",
            "🔄 Multi-dialect Support": "Works with MySQL, PostgreSQL, SQLite, and more",
            "🛠️ Interactive Playground": "Test and refine your queries in real-time",
            "🔍 Smart Error Correction": "Automatic detection and fixing of common SQL mistakes"
        }
        
        with st.expander("✨ Key Features", expanded=True):
            for title, description in features.items():
                st.markdown(f"**{title}**: {description}")
        
        st.info("👇 Scroll down to explore all features or click on the tabs below to navigate directly to specific tools")
    
    with col2:
        # Try to load team logo, but fall back to a URL if file not found
        try:
            st.image("assets/images/team_logo.png", width=150, caption="AiVERSE Team")
        except:
            st.image("https://img.icons8.com/fluency/240/000000/database-administrator.png", width=150, caption="AiVERSE Team")
        
        st.markdown("### Get Started")
        if st.button("Try Example Query", type="primary"):
            st.session_state.example_query = "Show all customers who made purchases in the last month"
            st.session_state.active_tab = "Query Generator"
            st.rerun()

# Create tabs for different features
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "Query Generator",
    "Query Playground",
    "Schema Explorer",
    "Performance Metrics",
    "Query Corrections",
    "Blog & FAQs",
    "Settings"
])

with tab1:
    # Use the title only if not already shown in landing page
    if 'active_tab' in st.session_state and st.session_state.active_tab == "Query Generator":
        st.title("🔮 SQL SAGE by AiVERSE")
        st.markdown("### AI-Powered Natural Language to SQL Query Generator")

    # Input section with suggestions
    nl_query = st.text_area(
        "Enter your query in natural language",
        height=100,
        placeholder="Example: Show me all customers who made purchases in the last month",
        value=st.session_state.example_query if 'example_query' in st.session_state else ""
    )
    
    # Clear example query after using it
    if 'example_query' in st.session_state and st.session_state.example_query:
        st.session_state.example_query = ""

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
                            # Check if first suggestion is about correction
                            if suggestions and "Attempted corrections:" in suggestions[0]:
                                st.warning("⚠️ " + suggestions[0])
                                if len(suggestions) > 1:
                                    st.info("💡 " + suggestions[1])
                            else:
                                st.info("💡 " + suggestions[0])
                        st.session_state.user_preferences.update_performance_metrics(
                            execution_time,
                            False
                        )
                    elif results is not None:
                        # Check if query was corrected
                        was_corrected = False
                        if suggestions and "Query was automatically corrected:" in suggestions[0]:
                            was_corrected = True
                            st.success("✅ " + suggestions[0])
                            suggestions = suggestions[1:]  # Remove correction message from suggestions
                        
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
    st.title("🔄 Query Corrections")
    
    if hasattr(st.session_state.playground, 'corrector'):
        corrections = st.session_state.playground.corrector.get_recent_corrections()
        
        if corrections:
            st.write(f"Found {len(corrections)} query corrections")
            
            for correction in corrections:
                with st.expander(f"Correction at {correction['timestamp']}"):
                    st.markdown("### Original Query")
                    st.code(correction["original_query"], language="sql")
                    
                    st.markdown("### Corrected Query")
                    st.code(correction["corrected_query"], language="sql")
                    
                    st.markdown("### Corrections Made")
                    st.info(correction["correction_message"])
        else:
            st.info("No query corrections have been made yet. Run a query with errors to see the correction feature in action.")
    else:
        st.error("Query corrector not initialized properly.")

with tab6:
    st.title("📚 Blog & FAQs")
    
    # Create a dictionary of blog posts
    blog_posts = {
        "Understanding SQL Basics": {
            "date": "March 5, 2025",
            "author": "Data Team @ AiVERSE",
            "content": """
            ## SQL Fundamentals Every Data Analyst Should Know
            
            SQL (Structured Query Language) is the standard language for interacting with relational databases. 
            Whether you're just starting out or looking to refresh your knowledge, understanding these core 
            concepts will help you write more effective queries.
            
            ### SELECT Statements
            
            The `SELECT` statement is the most common command in SQL, used to retrieve data from one or more tables:
            
            ```sql
            SELECT column1, column2 FROM table_name WHERE condition;
            ```
            
            ### JOIN Operations
            
            Joins allow you to combine rows from two or more tables based on a related column:
            
            ```sql
            SELECT orders.order_id, customers.customer_name
            FROM orders
            JOIN customers ON orders.customer_id = customers.customer_id;
            ```
            
            ### Aggregate Functions
            
            Functions like COUNT, SUM, AVG, MAX, and MIN perform calculations on a set of values:
            
            ```sql
            SELECT COUNT(*) as total_orders, SUM(amount) as revenue
            FROM orders
            WHERE order_date BETWEEN '2023-01-01' AND '2023-12-31';
            ```
            
            ### GROUP BY Clauses
            
            The GROUP BY clause groups rows that have the same values into summary rows:
            
            ```sql
            SELECT category, COUNT(*) as product_count
            FROM products
            GROUP BY category;
            ```
            
            Stay tuned for more SQL tips and tutorials!
            """
        },
        "AI and SQL: The Perfect Match": {
            "date": "February 28, 2025",
            "author": "AI Research Team @ AiVERSE",
            "content": """
            ## How AI is Revolutionizing Database Interactions
            
            Artificial Intelligence is transforming how we interact with databases. Natural Language Processing 
            (NLP) models can now understand human language and convert it into structured query language (SQL), 
            making databases accessible to non-technical users.
            
            ### The Evolution of Database Interfaces
            
            1. **Command Line Interfaces**: Required memorizing complex syntax
            2. **GUI Tools**: Made databases more accessible but still required technical knowledge
            3. **Natural Language Interfaces**: Allow querying in plain human language
            
            ### Benefits of AI-Powered SQL Generation
            
            - **Democratization of Data**: Everyone in an organization can access insights without technical skills
            - **Increased Productivity**: Developers and analysts can focus on more complex tasks
            - **Reduced Errors**: AI can suggest corrections for common mistakes
            - **Faster Development**: Rapid prototyping of database queries
            
            ### The Technology Behind SQL SAGE
            
            SQL SAGE uses a combination of:
            
            - Large Language Models trained on SQL syntax and patterns
            - Context-aware prompting that considers your database schema
            - Error detection and correction mechanisms
            - Query optimization techniques
            
            The future of database interaction is conversational, and tools like SQL SAGE are leading the way.
            """
        },
        "Query Optimization Tips": {
            "date": "February 15, 2025",
            "author": "Performance Team @ AiVERSE",
            "content": """
            ## 5 Ways to Make Your SQL Queries Faster
            
            Optimizing your SQL queries can dramatically improve application performance. Here are five 
            techniques to help you write more efficient queries:
            
            ### 1. Use Specific Column Names Instead of SELECT *
            
            Selecting only the columns you need reduces the amount of data transferred:
            
            ```sql
            -- Instead of this
            SELECT * FROM customers;
            
            -- Do this
            SELECT customer_id, name, email FROM customers;
            ```
            
            ### 2. Create Appropriate Indexes
            
            Indexes speed up search operations at the cost of slower writes:
            
            ```sql
            CREATE INDEX idx_customer_email ON customers(email);
            ```
            
            ### 3. Avoid Using Functions in WHERE Clauses
            
            Functions in WHERE clauses prevent the use of indexes:
            
            ```sql
            -- Slower query
            SELECT * FROM customers WHERE YEAR(registration_date) = 2023;
            
            -- Faster query
            SELECT * FROM customers WHERE registration_date BETWEEN '2023-01-01' AND '2023-12-31';
            ```
            
            ### 4. Use JOIN Instead of Subqueries
            
            Joins are often more efficient than subqueries:
            
            ```sql
            -- Instead of this
            SELECT name FROM customers 
            WHERE customer_id IN (SELECT customer_id FROM orders WHERE amount > 1000);
            
            -- Do this
            SELECT DISTINCT c.name 
            FROM customers c
            JOIN orders o ON c.customer_id = o.customer_id
            WHERE o.amount > 1000;
            ```
            
            ### 5. Limit Results When Possible
            
            Only retrieve the data you need, especially with large tables:
            
            ```sql
            SELECT * FROM orders ORDER BY order_date DESC LIMIT 100;
            ```
            
            Keep these tips in mind when writing queries or reviewing SQL generated by SQL SAGE!
            """
        }
    }
    
    # Blog Section
    st.header("Latest Blog Posts")
    
    blog_titles = list(blog_posts.keys())
    selected_blog = st.selectbox("Select a blog post to read", blog_titles)
    
    blog = blog_posts[selected_blog]
    st.markdown(f"**{selected_blog}**")
    st.markdown(f"*Published on {blog['date']} by {blog['author']}*")
    st.markdown(blog['content'])
    
    # FAQ Section
    st.header("Frequently Asked Questions")
    
    faqs = [
        {
            "question": "What is SQL SAGE?",
            "answer": "SQL SAGE is an AI-powered tool that converts natural language questions into SQL queries. It helps users who may not be familiar with SQL syntax to interact with databases using plain English."
        },
        {
            "question": "How accurate are the generated SQL queries?",
            "answer": "SQL SAGE uses advanced language models to generate highly accurate queries. However, as with any AI tool, you should always review the generated code before executing it on production databases. The accuracy improves over time as you provide more context about your database schema."
        },
        {
            "question": "Which SQL dialects are supported?",
            "answer": "SQL SAGE supports multiple SQL dialects including MySQL, PostgreSQL, SQLite, SQL Server, and Oracle. You can select your preferred dialect from the dropdown menu."
        },
        {
            "question": "How do I improve the accuracy of generated queries?",
            "answer": "To get better results, try to be specific in your natural language query and upload your database schema. The more context the AI has about your database structure, the more accurate the generated queries will be."
        },
        {
            "question": "Can SQL SAGE optimize my existing queries?",
            "answer": "Yes! The Query Optimizer feature can analyze your existing SQL queries and suggest performance improvements. This can help you identify missing indexes, inefficient joins, or other optimization opportunities."
        },
        {
            "question": "Is my data secure when using SQL SAGE?",
            "answer": "SQL SAGE is designed with privacy in mind. Your database connection details are stored locally, and queries are processed on your own machine. The application doesn't persistently store your data or send it to external servers beyond what's needed for AI processing."
        },
        {
            "question": "How does the Query Correction feature work?",
            "answer": "The Query Correction feature automatically identifies and fixes common SQL syntax errors. It analyses the query structure and applies corrections based on the selected SQL dialect. This helps especially when you're dealing with complex queries or learning SQL."
        }
    ]
    
    for i, faq in enumerate(faqs):
        with st.expander(f"Q: {faq['question']}"):
            st.markdown(f"**A:** {faq['answer']}")
    
    # Community Section
    st.header("Community")
    st.markdown("""
    Join our community to share your experience, report issues, or suggest new features!
    
    - 🌟 [GitHub Repository](https://github.com/aiverse/sql-sage)
    - 💬 [Community Forum](https://community.aiverse.io/sql-sage)
    - 📧 Contact us: support@aiverse.io
    """)

with tab7:
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