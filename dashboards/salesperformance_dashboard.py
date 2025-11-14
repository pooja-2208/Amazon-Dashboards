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
    st.title("PRODUCT SALES ANALYSIS AND PERFORAMNCE METRICS")

    st.sidebar.header("Filters")

    # Category filter 
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
    col1, col2, col3, col4= st.columns(4)
    col5, col6, col7, col8 = st.columns(4)
    with col1:
        st.metric("Total Sales", f"₹{filtered['selling_price'].sum()/1000000:,.2f}M")
    with col2:
        st.metric("Average Order Value", f"₹{filtered['selling_price'].mean():,.2f}")

    top_product = filtered.groupby('product_id')['selling_price'].sum().idxmax()
    with col3:
        st.metric("Top Selling Product",top_product)

    product_sales=filtered.groupby(by='product_id').agg(sales=('selling_price', 'sum')).sort_values(by='sales',
                                                                                            ascending=False).reset_index()
    top_5=round(product_sales.head(5)['sales'].sum()/filtered['selling_price'].sum()*100, 2)
    with col4:
        st.metric("Top 5 Products Sale Share", f"{top_5}%")

    top_category = filtered.groupby('category')['selling_price'].sum().idxmax()
    with col5:
        st.metric("Top Selling Category", top_category)

    top_subcategory1 = filtered.groupby('sub_category1')['selling_price'].sum().idxmax()
    with col6:
        st.metric("Top Selling Sub Category1", top_subcategory1)

    top_subcategory2 = filtered.groupby('sub_category2')['selling_price'].sum().idxmax()
    with col7:
        st.metric("Top Selling Sub Category2", top_subcategory2)

    top_subcategory3 = filtered.groupby('sub_category3')['selling_price'].sum().idxmax()
    with col8:
        st.metric("Top Selling Sub Category3", top_subcategory3)

    # Charts
    c1, c2, c3= st.columns(3)
    fig1 = px.bar(
        product_sales.head(5),
        x='product_id',
        y='sales',
        title='TOP 5 PRODUCTS BY SALE AMOUNT',
        text='sales',
        color='sales',
        color_continuous_scale='blues'
    )

    fig1.update_traces(textposition='outside')
    fig1.update_layout(xaxis_title='Product', yaxis_title='Sales')

    c1.plotly_chart(fig1, width="stretch")

    top_20=round(product_sales.head(20)['sales'].sum()/filtered['selling_price'].sum()*100, 2)
    top_50=round(product_sales.head(50)['sales'].sum()/filtered['selling_price'].sum()*100, 2)
    top_100=round(product_sales.head(100)['sales'].sum()/filtered['selling_price'].sum()*100, 2)
    top_N=pd.DataFrame({'Top_N': ['Top 20', 'Top 50', 'Top 100'], 'Sales_Share':[top_20, top_50, top_100]})
    fig2 = px.pie(
        top_N, 
        names='Top_N', 
        values='Sales_Share', 
        title='SALES SHARE BY TOP N PRODUCTS',
        hole=0.6 
    )
    fig2.update_traces(
        textposition='inside',
        textinfo='value',   
        insidetextorientation='radial',
        textfont=dict(size=12),
        automargin=True,
        texttemplate='%{value:.2f}%'
    )
    c2.plotly_chart(fig2, width="stretch")

    sale_amount = (filtered.groupby(['category', 'product_id'], as_index=False).agg(sale_amount=('selling_price','sum')))

    highest_sale_product = sale_amount.loc[sale_amount.groupby('category')['sale_amount'].idxmax()]

    fig3 = px.bar(
    highest_sale_product.sort_values(by='sale_amount', ascending=False),
        x='category',
        y='sale_amount',
        text='product_id',
        title='CATEGORY WISE TOP SELLING PRODUCT',
        color='sale_amount',
        color_continuous_scale='greens'
    )

    fig3.update_traces(textposition='outside')
    fig3.update_layout(xaxis_title='Category', yaxis_title='Selling Price')

    c3.plotly_chart(fig3, width="stretch")

    c4, c5, c6= st.columns(3)
    prod=filtered.groupby(by='product_id').agg(avg_price=('selling_price', 'mean'), avg_discount=('discount_percentage', 'mean'),
                                            avg_rating=('rating', 'mean'), sales=('selling_price', 'sum')).reset_index()
    prod['avg_discount']=prod['avg_discount']*100
    fig4 = px.scatter(
        prod,
        x='avg_price',
        y='sales',
        title='PRICE VS SALES',
        size='sales',
        hover_data=['avg_price', 'sales'],
        color='sales',
        color_continuous_scale='Cividis',
        trendline='ols'
        )

    fig4.update_layout(
        xaxis_title='Price',
        yaxis_title='Sales',
        title_font=dict(size=18),
    )

    c4.plotly_chart(fig4, width="stretch")

    fig5 = px.scatter(
        prod,
        x='avg_discount',
        y='sales',
        title='DISCOUNT VS SALES',
        size='sales',
        hover_data=['avg_discount', 'sales'],
        color='sales',
        color_continuous_scale='Turbo',
        trendline='ols'
    )

    fig5.update_layout(
        xaxis_title='Discount',
        yaxis_title='Sales',
        title_font=dict(size=18),
    )

    c5.plotly_chart(fig5, width="stretch")

    fig6 = px.scatter(
        prod,
        x='avg_rating',
        y='sales',
        title='RATING VS SALES',
        size='sales',
        hover_data=['avg_rating', 'sales'],
        color='sales',
        color_continuous_scale='plasma',
        trendline='ols'
    )

    fig6.update_layout(
        xaxis_title='Rating',
        yaxis_title='Sales',
        title_font=dict(size=18),
    )

    c6.plotly_chart(fig6, width="stretch")