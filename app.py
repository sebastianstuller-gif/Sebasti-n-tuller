import streamlit as st
import random
import datetime
import calendar
import holidays
import io
import os
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment

# --- KONFIGURÁCIA STRÁNKY ---
st.set_page_config(page_title="AUTOCESTAK pro", layout="wide")

# --- ELEGANTNÝ STYLING (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #1a1a1a;
    }
    .stButton>button {
        background-color: #000000;
        color: white;
        border-radius: 2px;
        border: none;
        letter-spacing: 1px;
        text-transform: uppercase;
        font-weight: 600;
        height: 3.5em;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #333333;
        border: none;
    }
    .price-box {
        padding: 40px 20px;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        background-color: #ffffff;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
    .price-box h4 { margin-bottom: 10px; color: #555; }
    .price-box h2 { font-size: 32px; margin: 15px 0; color: #000; }
    .price-box p { color: #888; font-size: 14px; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN LOGIKA ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

def check_password():
    if st.session_state["authenticated"]:
        return True
    
    st.markdown("<h2 style='text-align: center; margin-top: 50px;'>Prístup k systému</h2>", unsafe_allow_html=True)
    col_a, col_b, col_c = st.columns([1, 1.5, 1])
    with col_b:
        password = st.text_input("Prístupové heslo", type="password")
        if st.button("Vstúpiť do generátora"):
            if password == "levice2026":
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Nesprávne prístupové údaje.")
    return False

# --- SIDEBAR (Branding) ---
with st.sidebar:
    # Opravený názov súboru na logo.png.png
    if os.path.exists("logo.png.png"):
        st.image("logo.png.png", use_container_width=True)
    elif os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    else:
        st.markdown("<h1 style='font-size: 24px; text-align: center;'>AUTOCESTAK<br><span style='font-weight: 300;'>pro</span></h1>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    page = st.radio("Navigácia", ["Domov", "Generátor", "O systéme"])
    st.markdown("---")
    st.markdown(f"""
        <div style='font-size: 12px; color: gray; line-height: 1.6;'>
            Founder: <b>Sebastián Štuller</b><br>
            Spracovateľ: <b>jmcreditplus s.r.o.</b><br>
            Verzia: 1.0.2 Pro
        </div>
    """, unsafe_allow_html=True)
    
    if st.session_state["authenticated"]:
        if st.button("Odhlásiť"):
            st.session_state["authenticated"] = False
            st.rerun()

# --- OBSAH ---
if page == "Domov":
    st.title("AUTOCESTAK pro")
    st.subheader("Profesionálna automatizácia cestovných príkazov.")
    st.markdown("Šetrite hodiny ručnej práce mesačne s naším inteligentným algoritmom.")
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col_left, col_mid, col_right = st.columns([1, 2, 1])
    with col_mid:
        st.markdown("<h3 style='text-align: center;'>Vyberte si váš plán</h3><br>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("""
                <div class="price-box">
                    <h4>Mesačne</h4>
                    <p>Ideálne pre jednotlivcov</p>
                    <h2>9,99 €</h2>
                    <p>bez viazanosti</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button("Aktivovať mesačne", key="btn_mo"):
                st.info("Platobná brána sa pripravuje.")

        with c2:
            st.markdown("""
                <div class="price-box" style="border: 2px solid #000;">
                    <h4>Ročne</h4>
                    <p>Najlepšia hodnota</p>
                    <h2>100 €</h2>
                    <p>ušetríte 20 € ročne</p>
                </div>
            """, unsafe_allow
