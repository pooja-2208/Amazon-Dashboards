import streamlit as st

def render():
    st.set_page_config(layout="wide")

    powerbi_embed_url = "https://app.powerbi.com/view?r=eyJrIjoiNjM3N2Y1YjMtMjZiNS00NmY5LWJhMzAtNjlhODc2M2Y1MDg5IiwidCI6ImY2ZjZlYTBhLTExYjctNGE1MS1hMTc1LTUwMzQxZDRlMDdmYiJ9"

    st.markdown(
        f"""
        <iframe width="100%" height="600" src="{powerbi_embed_url}" frameborder="0" allowFullScreen="true"></iframe>
        """,
        unsafe_allow_html=True
    )