import streamlit as st

def kpi_card(title, value, delta, color, width, height):
    st.markdown(f"""
        <div style='
            padding: 1rem;
            width: {width};
            height: {height};
            border-radius: 10px;
            background-color: #f0f2f6;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
            border-left: 5px solid {color};
        '>
            <h4 style='margin-bottom:0.2rem;'>{title}</h4>
            <h2 style='margin-top:0rem;'>{value}</h2>
            <p style='color:{"green" if "-" not in delta else "red"};'>{delta}</p>
        </div>
    """, unsafe_allow_html=True)

