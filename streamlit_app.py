# Import python packages
import streamlit as st
import snowflake.connector
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom Smoothie!
    """)

# Input for the name on the smoothie
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Snowflake connection setup
@st.cache_resource  # Cache the session to avoid repeated logins
def init_snowflake_connection():
    conn = snowflake.connector.connect(
        account='your_account',
        user='your_user',
        password='your_password',
        warehouse='your_warehouse',
        database='smoothies',
        schema='public',
        role='your_role'
    )
    return Session.builder.configs(conn).create()

# Retrieve Snowflake session
try:
    session = init_snowflake_connection()

    # Retrieve fruit options from Snowflake
    my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME')).collect()

    # Convert fruit options to a list for multiselect
    fruit_names = [row['FRUIT_NAME'] for row in my_dataframe]

    # Multiselect for ingredients
    ingredients_list = st.multiselect(
        'Choose up to 5 ingredients:',
        fruit_names,  # Pass the list of fruit names
        max_selections=5  # Ensure proper selection limitation
    )

    if ingredients_list:
        # Create a comma-separated string of ingredients
        ingredients_string = ', '.join(ingredients_list)

        st.write('Ingredients:', ingredients_string)

        # SQL insert statement for the new order (using parameterized query to prevent SQL injection)
        insert_query = """
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES (%s, %s)
        """

        # Submit the order
        if st.button('Submit Order'):
            try:
                session.execute(insert_query, [ingredients_string, name_on_order])
                st.success('Your Smoothie is ordered!', icon="✅")
            except Exception as e:
                st.error(f"Error submitting order: {e}")
except Exception as e:
    st.error(f"Error connecting to Snowflake: {e}")
