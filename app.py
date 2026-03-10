import streamlit as st
import random
import datetime
import calendar
import holidays
import io
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment

# --- 1. ZÁKLADNÉ NASTAVENIE A STYLING ---
st.set_page_config(page_title="AutoCesták PRO", page_icon="🚀", layout="wide")

# Vlastné CSS pre krajší vzhľad
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #ff4b4b; color: white; }
    .sidebar-text { font-size: 14px; color: #555; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGIN LOGIKA ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

def check_password():
    def password_entered():
        if st.session_state["password"] == "levice2026": # Tvoje heslo
            st.session_state["authenticated"] = True
            del st.session_state["password"]
        else:
            st.error("❌ Nesprávne heslo")

    if not st.session_state["authenticated"]:
        st.title("🔒 Prístup do systému")
        st.text_input("Zadajte prístupové heslo:", type="password", on_change=password_entered, key="password")
        return False
    return True

# --- 3. SIDEBAR (Logo a Info o firme) ---
with st.sidebar:
    # st.image("logo.png", width=200) # Tu pridaj svoje logo neskôr
    st.title("AutoCesták PRO")
    st.markdown("---")
    st.markdown("### 🏢 O tvorcovi")
    st.markdown("**Sebastian Tuller**")
    st.markdown("*Founder & Financial Architect*")
    st.markdown("---")
    st.markdown("**Tuller Automation s.r.o.**")
    st.markdown("Levice, Slovensko")
    st.markdown("---")
    
    # Navigácia
    page = st.radio("Menu:", ["🏠 Domov & Cenník", "📊 Generátor cesťákov", "ℹ️ O nás"])

# --- 4. OBSAH STRÁNOK ---

if page == "🏠 Domov & Cenník":
    st.title("Vitajte v AutoCesták PRO")
    st.subheader("Najrýchlejší spôsob, ako spracovať firemné cesty.")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("### 🆓 FREE")
        st.markdown("- 5 cesťákov mesačne\n- Iba Slovensko\n- Bez exportu do Excelu")
        st.button("Vyskúšať", key="free")

    with col2:
        st.success("### 💎 PRO")
        st.markdown("- **Neobmedzene** cesťákov\n- Slovensko + Zahraničie\n- **Priamy export do Excelu**\n- Automatické diéty")
        st.button("Zakúpiť PRO (19€/mes)", key="pro")

    with col3:
        st.warning("### 🏢 ENTERPRISE")
        st.markdown("- Pre účtovné kancelárie\n- Viac užívateľov\n- API prepojenie\n- Prioritná podpora")
        st.button("Kontaktovať", key="ent")

    

elif page == "📊 Generátor cesťákov":
    if check_password():
        st.title("📊 Generátor cestovných príkazov")
        # --- TU VLOŽÍŠ TEN KÓD, KTORÝ SME ROBILI NAPOSLEDY (ZÁLOŽKY, VÝPOČTY ATĎ.) ---
        st.write("Vitaj, Sebastian. Systém je pripravený na generovanie.")
        # (Sem skopíruj kód od tab_sk, tab_zahranicie z minula)

elif page == "ℹ️ O nás":
    st.title("O projekte")
    st.write("""
    Tento softvér vznikol ako reakcia na neefektívne ručné spracovávanie cestovných príkazov 
    v účtovných kanceláriách. Spájame **finančnú expertízu** s **automatizáciou v Pythone**.
    """)
    st.markdown("---")
    st.subheader("Naša vízia")
    st.write("Pomáhať slovenským podnikateľom tráviť menej času byrokraciou a viac času budovaním biznisu.")
