import streamlit as st
import random
import datetime
import calendar
import holidays
import io
import os
import requests
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment

# --- KONFIGURÁCIA STRÁNKY ---
st.set_page_config(page_title="AUTOCESTAK pro", layout="wide", initial_sidebar_state="collapsed")

# --- POMOCNÉ FUNKCIE PRE SADZBY ---
def get_sk_rates(rok, mesiac_idx):
    # Amortizácia (Sadzba za 1 km)
    if rok < 2025: amort = 0.252 # Staršia sadzba
    elif rok == 2025:
        if mesiac_idx <= 2: amort = 0.265
        elif mesiac_idx <= 5: amort = 0.281
        else: amort = 0.296
    else: # 2026 a viac
        amort = 0.313
    
    # Stravné Slovensko
    if rok < 2025: stravne = 7.80
    elif rok == 2025:
        if mesiac_idx <= 3: stravne = 8.30
        elif mesiac_idx <= 11: stravne = 8.80
        else: stravne = 9.30
    else: # 2026 a viac
        stravne = 9.30
        
    return amort, stravne

def get_exchange_rate(curr):
    if curr == "EUR": return 1.0
    try:
        response = requests.get(f"https://api.frankfurter.app/latest?from={curr}&to=EUR")
        return response.json()['rates']['EUR']
    except:
        return 0.040 if curr == "CZK" else 0.088 # Záložné kurzy ak vypadne API

# --- JAZYKOVÝ SLOVNÍK ---
if "lang" not in st.session_state: st.session_state["lang"] = "SK"
if "page" not in st.session_state: st.session_state["page"] = "Domov"
if "authenticated" not in st.session_state: st.session_state["authenticated"] = False

translations = {
    "SK": {
        "nav_home": "Domov", "nav_cestaky": "Cesťáky", "nav_support": "Podpora", "nav_about": "O nás",
        "login_btn": "Prihlásenie", "logout_btn": "Odhlásiť",
        "gen_title": "Generátor cesťákov"
    }
}
t = translations["SK"]

# --- CSS STYLING ---
st.markdown("""
    <style>
    html, body, .stApp { background-color: #ffffff; color: #111111; }
    .source-link a { color: #666666 !important; text-decoration: none; font-size: 12px; }
    .gen-btn > button { background-color: #111111 !important; color: #ffffff !important; width: 100%; height: 3.5em; border-radius: 8px; font-weight: 600; border: none; }
    </style>
    """, unsafe_allow_html=True)

# --- NAVIGÁCIA ---
col_logo, col_nav1, col_nav2, col_nav3, col_space, col_login = st.columns([2.5, 0.8, 0.8, 0.8, 2, 1.5])
with col_logo: st.subheader("AUTOCESTAK pro")
with col_nav1: 
    if st.button("Domov"): st.session_state["page"] = "Domov"
with col_nav2:
    if st.button("Cesťáky"): st.session_state["page"] = "Cesťáky"
with col_login:
    if not st.session_state["authenticated"]:
        if st.button("Prihlásenie"): st.session_state["page"] = "Login"
    else:
        if st.button("Odhlásiť"): st.session_state["authenticated"] = False; st.rerun()

st.markdown("---")

# --- LOGIN ---
if st.session_state["page"] == "Login":
    l1, l2, l3 = st.columns([1,1,1])
    with l2:
        pwd = st.text_input("Heslo", type="password")
        if st.button("Vstúpiť"):
            if pwd == "levice2026":
                st.session_state["authenticated"] = True
                st.session_state["page"] = "Cesťáky"
                st.rerun()
    st.stop()

# --- DOMOV ---
if st.session_state["page"] == "Domov":
    st.title("Napreduj s automatizovaním cesťákov")
    st.write("Profesionálny nástroj pre účtovné kancelárie.")

# --- GENERÁTOR ---
elif st.session_state["page"] == "Cesťáky":
    if not st.session_state["authenticated"]:
        st.warning("Pre túto sekciu sa musíte prihlásiť.")
    else:
        st.title(t["gen_title"])
        
        c1, c2 = st.columns(2)
        with c1:
            meno = st.text_input("Meno zamestnanca", value="Sebastián Štuller")
            rok = st.selectbox("Rok", [2025, 2026], index=1)
            mesiac_str = st.selectbox("Mesiac", ["Január", "Február", "Marec", "Apríl", "Máj", "Jún", "Júl", "August", "September", "Október", "November", "December"])
            mesiac_idx = ["Január", "Február", "Marec", "Apríl", "Máj", "Jún", "Júl", "August", "September", "Október", "November", "December"].index(mesiac_str) + 1
            
            # Automatické sadzby podľa dátumu
            def_amort, def_stravne = get_sk_rates(rok, mesiac_idx)
            
            typ_cesty = st.radio("Typ cesty", ["Vnútroštátna (Slovensko)", "Zahraničná"])
            
            if typ_cesty == "Zahraničná":
                krajina = st.selectbox("Cieľová krajina", ["Nemecko", "Rakúsko", "Belgicko", "Maďarsko", "Česko", "Švédsko"])
                vydavky_mena = "EUR"
                if krajina == "Česko": 
                    zah_stravne_zaklad = 600; mena = "CZK"
                elif krajina == "Švédsko": 
                    zah_stravne_zaklad = 455; mena = "SEK"
                elif krajina == "Maďarsko": 
                    zah_stravne_zaklad = 39; mena = "EUR"
                else: 
                    zah_stravne_zaklad = 45; mena = "EUR"
                
                kurz = get_exchange_rate(mena)
                stravne_val = zah_stravne_zaklad * kurz
                st.info(f"Sadzba pre {krajina}: {zah_stravne_zaklad} {mena} (Prepočítané: {stravne_val:.2f} EUR)")
            else:
                stravne_val = st.number_input("Stravné SK (€/deň)", value=def_stravne)

        with c2:
            cielova_suma = st.number_input("Cieľová suma (€)", value=1500.0)
            spotreba = st.number_input("Spotreba (l/100km)", value=6.5)
            cena_phm = st.number_input("Cena PHM (€/l)", value=1.60)
            amortizacia = st.number_input("Amortizácia (€/km)", value=def_amort, format="%.3f")
            
            st.markdown("### Doplnkové výdavky")
            ubytovanie = st.number_input("Ubytovanie spolu (€)", value=0.0)
            vedlajsie = st.number_input("Vedľajšie výdavky (materiál, parkovné...) (€)", value=0.0)

        st.markdown('<div class="gen-btn">', unsafe_allow_html=True)
        if st.button("🚀 Vygenerovať a vypočítať"):
            # Výpočet trás
            sadzba_celkova = amortizacia + ((spotreba / 100) * cena_phm)
            
            # Excel logika
            wb = Workbook()
            ws = wb.active
            ws.append(["Dátum", "Miesto", "Účel", "Km", "Sadzba/km", "Cestovné", "Stravné", "Nocľažné", "Vedľajšie", "SPOLU"])
            
            # Rozdelenie ubytovania a vedľajších výdavkov na prvú cestu (zjednodušene)
            # V reálnej verzii by sa to dalo rozpočítať na dni
            
            # Tu by pokračovala tvoja generovacia slučka (dni, trasy...)
            # Pre demo pridáme jeden riadok s tvojimi novými hodnotami
            ws.append([f"01.{mesiac_idx}.{rok}", "Pracovná cesta", "Obchodné rokovanie", 100, sadzba_celkova, 100*sadzba_celkova, stravne_val, ubytovanie, vedlajsie, (100*sadzba_celkova)+stravne_val+ubytovanie+vedlajsie])
            
            output = io.BytesIO()
            wb.save(output)
            st.success("Súbor pripravený!")
            st.download_button("📥 Stiahnuť Excel", output.getvalue(), file_name="Cestak_Pro.xlsx")
        st.markdown('</div>', unsafe_allow_html=True)
