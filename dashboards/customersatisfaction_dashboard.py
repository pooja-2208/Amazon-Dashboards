import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import statsmodels
import plotly.graph_objects as go
from db import get_engine

def render():
    engine=get_engine()
    amazon_orders = pd.read_sql("SELECT * FROM CleanedAmazonData", engine)
  
    st.set_page_config(layout="wide")
    st.title("AMAZON CUSTOMER SATISFACTION ANALYSIS")

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
    with col1:
        st.metric("Average Rating", f"{filtered['rating'].mean():,.2f}")

    prod=filtered.groupby(by='product_id').agg(avg_price=('selling_price', 'mean'), avg_discount=('discount_percentage', 'mean'),
                                           avg_rating=('rating', 'mean'), avg_ratingcount=('rating_count', 'mean'),
                                           order_count=('product_id','count'), sales=('selling_price', 'sum')).reset_index()
    prod['avg_discount']=prod['avg_discount']*100
    share_of_products_with_average_rating_greater_than_or_equal_to_4=round(prod.loc[prod['avg_rating']>=4,
                                                                       'avg_rating'].count()/prod['avg_rating'].count()*100, 2)
    with col2:
        st.metric("Share of Products >= 4", f"{share_of_products_with_average_rating_greater_than_or_equal_to_4}%")

    avg_rating1 = filtered.groupby('category', as_index=False)['rating'].mean()
    highest_rating1 = avg_rating1.loc[avg_rating1['rating'].idxmax()]
    with col3:
        st.metric("High Rating Category", highest_rating1['category'])

    avg_rating2 = filtered.groupby('sub_category1', as_index=False)['rating'].mean()
    highest_rating2 = avg_rating2.loc[avg_rating2['rating'].idxmax()]
    with col4:
        st.metric("High Rating Sub Category1", highest_rating2['sub_category1'])

    # Charts
    c1, c2= st.columns(2)
    max_rating = prod['avg_rating'].max()
    top_rated = prod[prod['avg_rating'] == max_rating]
    fig1= go.Figure(data=[go.Table(
        header=dict(
            values=['Product ID', 'Rating'],
            fill_color='lightblue',
            align='center',
            font=dict(size=14, color='black')
        ),
        cells=dict(
            values=[
                top_rated['product_id'],
                top_rated['avg_rating']
            ],
            fill_color='lavender',
            align='center',
            font=dict(size=13),
            height=30
        )
    )])

    fig1.update_layout(
        title={
            'text': f"Top Rated Products",
            'x': 0.5,            
            'xanchor': 'center',
            'yanchor': 'top',
            'y': 0.95             
        },
        margin=dict(t=60, b=20),  
    )

    c1.plotly_chart(fig1, width="stretch")

    category_rating=filtered.groupby(by='category').agg(avg_rating=('rating', 'mean')).sort_values(by=
                                                                                    'avg_rating', ascending=False).reset_index()
    category_rating['avg_rating']=category_rating['avg_rating'].round(2)
    fig2= go.Figure(data=[go.Table(
        header=dict(
            values=['Category', 'Rating'],
            fill_color='lightblue',
            align='center',
            font=dict(size=14, color='black')
        ),
        cells=dict(
            values=[
                category_rating['category'],
                category_rating['avg_rating']
            ],
            align='center',
            font=dict(size=13),
            fill_color='lavender',
            height=30
        )
    )])

    fig2.update_layout(
        title={
            'text': f"CATEGORY WISE AVERAGE RATING",
            'x': 0.5,            
            'xanchor': 'center',
            'yanchor': 'top',
            'y': 0.95             
        },
        margin=dict(t=60, b=20)
    )

    c2.plotly_chart(fig2, width="stretch")

    c3, c4= st.columns(2)

    prod_clean = prod.dropna(subset=['avg_rating'])
    fig3 = px.scatter(
        prod_clean,
        x='avg_price',
        y='avg_rating',
        title='PRICE VS RATING',
        size='avg_rating',
        hover_data=['avg_price', 'avg_rating'],
        color='avg_rating',
        color_continuous_scale='Viridis',
        trendline='ols'
    )

    fig3.update_layout(
        xaxis_title='Price',
        yaxis_title='Rating',
        title_font=dict(size=18),
    )

    c3.plotly_chart(fig3, width="stretch")

    fig4 = px.scatter(
        prod_clean,
        x='avg_discount',
        y='avg_rating',
        title='DISCOUNT VS RATING',
        size='avg_rating',
        hover_data=['avg_discount', 'avg_rating'],
        color='avg_rating',
        color_continuous_scale='Cividis',
        trendline='ols'
    )

    fig4.update_layout(
        xaxis_title='Discount',
        yaxis_title='Rating',
        title_font=dict(size=18),
    )

    c4.plotly_chart(fig4, width="stretch")

    c5, c6= st.columns(2)
    fig5 = px.scatter(
        prod_clean,
        x='avg_ratingcount',
        y='avg_rating',
        title='RATING COUNT VS RATING',
        size='avg_rating',
        hover_data=['avg_ratingcount', 'avg_rating'],
        color='avg_rating',
        color_continuous_scale='blues',
        trendline='ols'
    )

    fig5.update_layout(
        xaxis_title='Rating Count',
        yaxis_title='Rating',
        title_font=dict(size=18),
    )

    c5.plotly_chart(fig5, width="stretch")

    rating_orders=filtered.groupby(by='rating').agg(order_count=('rating','count')).reset_index()
    rating_orders=rating_orders.dropna(subset='rating')
    fig6 = px.scatter(
        rating_orders,
        x='rating',
        y='order_count',
        title='RATING VS NUMBER OF ORDERS',
        size='rating',
        hover_data=['rating', 'order_count'],
        color='rating',
        color_continuous_scale='plasma',
        trendline='ols'
    )

    fig6.update_layout(
        xaxis_title='Rating',
        yaxis_title='Number of Orders',
        title_font=dict(size=18),
    )

    c6.plotly_chart(fig6, width="stretch")