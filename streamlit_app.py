# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom Smoothie!
    """)

name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Snowflake session setup
cnx = st.connection("snowflake")
session = cnx.session()

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

    # SQL insert statement for the new order
    my_insert_stmt = f"""
    INSERT INTO smoothies.public.orders (ingredients, name_on_order)
    VALUES ('{ingredients_string}', '{name_on_order}')
    """

    # Submit the order
    if st.button('Submit Order'):
        session.sql(my_insert_stmt).collect()  # Execute the insert query when button is clicked
        st.success('Your Smoothie is ordered!', icon="✅")
