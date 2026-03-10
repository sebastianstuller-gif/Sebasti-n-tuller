import streamlit as st
import random
import datetime
import calendar
import holidays
import io
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment

# --- 1. ZÁKLADNÉ NASTAVENIE ---
st.set_page_config(page_title="AutoCesták PRO", page_icon="🚀", layout="wide")

# Vlastné CSS pre biznis vzhľad
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #ff4b4b; color: white; }
    .price-box { padding: 20px; border-radius: 10px; border: 1px solid #ddd; background-color: white; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGIN LOGIKA (Session State) ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

def check_password():
    if st.session_state["authenticated"]:
        return True
    
    st.title("🔒 Prístup do systému")
    password = st.text_input("Zadajte prístupové heslo:", type="password")
    if st.button("Prihlásiť sa"):
        if password == "levice2026":
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("❌ Nesprávne heslo")
    return False

# --- 3. SIDEBAR (Navigácia a Branding) ---
with st.sidebar:
    st.title("AutoCesták PRO")
    st.markdown("---")
    page = st.radio("Menu:", ["🏠 Domov & Cenník", "📊 Generátor cesťákov", "ℹ️ O nás"])
    st.markdown("---")
    st.markdown("### 🏢 Kontakt")
    st.markdown("**Sebastian Tuller**\n\nTuller Automation s.r.o.\nLevice, Slovensko")
    
    if st.session_state["authenticated"]:
        if st.button("Odhlásiť sa"):
            st.session_state["authenticated"] = False
            st.rerun()

# --- 4. OBSAH STRÁNOK ---

if page == "🏠 Domov & Cenník":
    st.title("Vitajte v AutoCesták PRO")
    st.subheader("Automatizácia, ktorá šetrí hodiny ručnej práce.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="price-box"><h3>🆓 FREE</h3><p>5 cesťákov mesačne<br>Iba Slovensko</p><h4>0 €</h4></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="price-box" style="border: 2px solid #ff4b4b;"><h3>💎 PRO</h3><p><b>Neobmedzene</b><br>Excel export<br>Zahraničie</p><h4>19 € / mes</h4></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="price-box"><h3>🏢 KANCELÁRIA</h3><p>Viac užívateľov<br>API prístup<br>Podpora</p><h4>Dohodou</h4></div>', unsafe_allow_html=True)

elif page == "📊 Generátor cesťákov":
    if check_password():
        st.title("📊 Generátor cestovných príkazov")
        
        tab_sk, tab_zahranicie = st.tabs(["🇸🇰 Slovenské cesťáky", "🌍 Zahraničné cesťáky"])

        with tab_sk:
            col1, col2 = st.columns(2)
            with col1:
                meno = st.text_input("Meno a Priezvisko:", value="Jozef Mrkvička")
                spz = st.text_input("ŠPZ Vozidla:", value="LV-123XY")
                mesiac_nazov = st.selectbox("Mesiac:", ["Január", "Február", "Marec", "Apríl", "Máj", "Jún", "Júl", "August", "September", "Október", "November", "December"])
                start_miesto = st.text_input("Miesto štartu:", value="Mýtne Ludany")
            with col2:
                cielova_suma = st.number_input("Cieľová suma mesačne (€):", value=1500.0)
                spotreba = st.number_input("Spotreba (l/100km):", value=6.5)
                cena_phm = st.number_input("Cena PHM (€/l):", value=1.62)
                amortizacia = st.number_input("Amortizácia (€/km):", value=0.265, format="%.3f")
                stravne_val = st.number_input("Stravné (€/deň):", value=8.30)

            mesta_sk = st.text_area("Zoznam destinácií:", value="Bratislava, Nitra, Trenčín, Poprad, Žilina")

            if st.button("🚀 Vygenerovať SK cesťák"):
                # --- VÝPOČTOVÁ LOGIKA ---
                sadzba_km = amortizacia + ((spotreba / 100) * cena_phm)
                mesiace_dict = {"Január": 1, "Február": 2, "Marec": 3, "Apríl": 4, "Máj": 5, "Jún": 6, "Júl": 7, "August": 8, "September":
