import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import statsmodels
from db import get_engine

def render():
    engine = get_engine()
    amazon_orders = pd.read_sql("SELECT * FROM CleanedAmazonData", engine)
  
    st.set_page_config(layout="wide")
    st.title("CUSTOMER DASHBOARD OF AMAZON")

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
    col1, col2, col3, col4 = st.columns(4)
    col5, col6, col7, col8 =st.columns(4)
    with col1:
        st.metric("Unique Customers", f"{filtered['user_id'].nunique():,}")

    customer_orders=filtered.groupby(by='user_id').agg(order_count=('user_id','count'), ordered_amount=('selling_price',
                                                                                                         'sum')).reset_index()
    customer_orders=customer_orders.loc[customer_orders['order_count']>1,:]
    with col2:
        st.metric("Repeated Customers", f"{customer_orders.shape[0]:,}")
    with col3:
        st.metric("Repeat Purchase Rate", f"{customer_orders.shape[0]/filtered['user_id'].nunique()*100:.2f}%")
    with col4:
        st.metric("Repeat Customer Revenue", f"₹{customer_orders ['ordered_amount'].sum()/1000000:.2f}M")
    with col5:
        st.metric("Repeat Customer Revenue %", f"{customer_orders ['ordered_amount'].sum()/filtered['selling_price'].sum()*100:.2f}%")

    customer_wise_sales=filtered.groupby(by='user_id').agg(sales=('selling_price', 
                                                                'sum')).sort_values(by='sales', ascending=False).reset_index()
    customer_wise_sales.columns=['customer', 'sales']
    top5=round(customer_wise_sales.head(5)['sales'].sum()/filtered['selling_price'].sum()*100, 2)
    with col6:
        st.metric("Top 5 Customers Share share", f"{top5}%")
    
    with col7:
        st.metric("Maximum Ordered Amount", f"₹{filtered.groupby(by='user_id')['selling_price'].sum().max()/1000:.2f}K")

    # Charts
    c1, c2 = st.columns(2)
    category_customers=filtered.groupby(by='category')['user_id'].nunique().reset_index()
    category_customers.columns=['category', 'customer_base']
    category_customers=category_customers.sort_values(by='customer_base')

    fig1 = px.pie(
        category_customers, 
        names='category', 
        values='customer_base', 
        title='CATEGORY WISE CUSTOMER BASE',
     hole=0.6 
    )
    fig1.update_traces(
        textposition='inside',
        textinfo='value+percent',   
        insidetextorientation='radial',
        textfont=dict(size=12),
        texttemplate='%{value:,}<br>%{percent}',
        automargin=True
    )
    c1.plotly_chart(fig1, width="stretch")

    top15=round(customer_wise_sales.head(15)['sales'].sum()/filtered['selling_price'].sum()*100, 2)
    top50=round(customer_wise_sales.head(50)['sales'].sum()/filtered['selling_price'].sum()*100, 2)
    top100=round(customer_wise_sales.head(100)['sales'].sum()/filtered['selling_price'].sum()*100, 2)
    top_n=pd.DataFrame({'Top N': ['Top 15', 'Top 50', 'Top 100'], 'Sales Share':[top15, top50, top100]})
    fig2 = px.pie(
        top_n, 
        names='Top N', 
        values='Sales Share', 
        title='TOP N CUSTOMERS SALES SHARE',
        color_discrete_sequence=['#2E86AB', '#F6C85F', '#6FB07F'] ,
        hole=0.6 
    )
    fig2.update_traces(
        textposition='inside',
        textinfo='value',   
        insidetextorientation='radial',
        textfont=dict(size=12),
        automargin=True,
        texttemplate='%{value:.1f}%'
    )
    c2.plotly_chart(fig2, width="stretch")

    c3, c4= st.columns(2)

    subcategory_customers=filtered.groupby(by=
                    'sub_category1').agg(customer_base=('user_id','nunique')).sort_values(by='customer_base').reset_index().tail(5)
    fig3= px.bar(
        subcategory_customers,
        x='customer_base',
        y='sub_category1',
        orientation='h', 
        title='TOP 5 SUBCATEGORIES BY CUSTOMER BASE',
        color='customer_base',
        color_continuous_scale='Blues',
        text='customer_base' 
    )
    fig3.update_layout(
        yaxis=dict(categoryorder='total ascending'),
        title_font=dict(size=18),
        xaxis_title="Customer Base",
        yaxis_title="Subcategory"
    )
    c3.plotly_chart(fig3, width="stretch")

    fig4= px.bar(
        customer_orders.head(5),
        x='order_count',
        y='user_id',
        orientation='h', 
        title='TOP 5 LOYAL CUSTOMERS',
        color='order_count',
        color_continuous_scale='oranges',
        text='order_count' 
    )
    fig4.update_layout(
        yaxis=dict(categoryorder='total ascending'),
        title_font=dict(size=18),
        xaxis_title="Order Count",
        yaxis_title="Customer"
    )
    c4.plotly_chart(fig4, width="stretch")