import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import statsmodels
from db import get_engine


def render():
    engine=get_engine()
    amazon_orders = pd.read_sql("SELECT * FROM CleanedAmazonData", engine)
    st.set_page_config(layout="wide")
    st.title("AMAZON ORDERS INSIGHTS")
    
    st.sidebar.header("Filters")

    # Category filter with "All"
    categories = amazon_orders['category'].unique().tolist()
    categories.sort()
    category_selected = st.sidebar.multiselect(
        "Select Category",
        options=categories,
        default=categories  
    )

    # Subcategory filter depends on selected category
    subcategories = amazon_orders[amazon_orders['category'].isin(category_selected)]['sub_category1'].unique().tolist()
    subcategories.sort()
    subcategory_selected = st.sidebar.multiselect(
        "Select Subcategory",
        options=subcategories,
        default=subcategories  
    )

    # Apply filters
    if category_selected: 
        filtered = amazon_orders[(amazon_orders['category'].isin(category_selected)) & 
                                (amazon_orders['sub_category1'].isin(subcategory_selected))]
    else:
        filtered = amazon_orders.copy()

    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    col5, col6, col7, col8 = st.columns(4)
    with col1:
        st.metric("📦 Unique Products", f"{filtered['product_id'].nunique():,}")
    with col2:
        st.metric("🛒 Total Orders", f"{filtered['product_id'].count():,}")
    with col3:
        st.metric("💸 Average Discount", f"{filtered['discount_percentage'].mean()*100:.2f}%")
    with col4:
        st.metric("💰 Average Selling Price", f"₹{filtered['selling_price'].mean():,.0f}")
    with col5:
        st.metric("📂 Unique Categories", filtered['category'].nunique())
    with col6:
        st.metric("🗂️ Unique Subcategories", filtered['sub_category1'].nunique())

    max_price_row = filtered.loc[filtered['selling_price'].idxmax()]
    with col7:
        st.metric("🏆 Highest Price Product", f"{max_price_row['product_id']}")

    # Charts
    c1, c2=st.columns(2)

    category_orders = filtered['category'].value_counts().reset_index()
    category_orders.columns = ['category', 'order_count']

    fig1 = px.pie(
        category_orders, 
        names='category', 
        values='order_count', 
        title='CATEGORY WISE ORDER FREQUENCY',
        hole=0.6 
    )
    fig1.update_traces(
        textposition='inside',
        textinfo='value+percent',   
        insidetextorientation='radial',
        textfont=dict(size=12),
        automargin=True,
        texttemplate='%{value:,}<br>%{percent}'
    )
    c1.plotly_chart(fig1, width="stretch")


    price = (filtered.groupby(['category', 'product_id'], as_index=False)['selling_price'].mean())

    highest_price_product = price.loc[price.groupby('category')['selling_price'].idxmax()]

    fig2 = px.bar(
        highest_price_product.sort_values(by='selling_price', ascending=False),
        x='category',
        y='selling_price',
        text='product_id',
        title='HIGHEST PRICED PRODUCT PER CATEGORY',
        color='selling_price',
        color_continuous_scale='Blues'
    )

    fig2.update_traces(textposition='outside')
    fig2.update_layout(xaxis_title='Category', yaxis_title='Selling Price')

    c2.plotly_chart(fig2, width="stretch")

    c3, c4=st.columns(2)

    top_subcategories = (filtered['sub_category1'].value_counts().head(5).reset_index())
    top_subcategories.columns = ['subcategory', 'order_count']

    fig3 = px.bar(
        top_subcategories,
        y='subcategory',
        x='order_count',
        orientation='h',
        title='TOP 5 SUBCATEGORIES BY ORDER FREQUENCY',
        text='order_count',
        color='order_count',
        color_continuous_scale='greens'
    )

    fig3.update_traces(textposition='inside')
    fig3.update_layout(yaxis=dict(categoryorder='total ascending'), xaxis_title='Subcategory', yaxis_title='Order Count')

    c3.plotly_chart(fig3, width="stretch")

    discount_orders = (filtered.groupby('discount_percentage')['product_id'].count().reset_index())
    discount_orders['discount_percentage']=discount_orders['discount_percentage']*100
    discount_orders.columns = ['discount', 'order_count']

    fig4 = px.scatter(
        discount_orders,
        x='discount',
        y='order_count',
        title='DISCOUNT vs NUMBER OF ORDERS',
        size='order_count',
        hover_data=['discount', 'order_count'],
        color='order_count',
        color_continuous_scale='Cividis',
        trendline='ols'
    )

    fig4.update_layout(
        xaxis_title='Discount (%)',
        yaxis_title='Number of Orders'
    )

    c4.plotly_chart(fig4, width="stretch")

