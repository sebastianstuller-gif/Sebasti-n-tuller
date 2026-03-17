import streamlit as st
import random
import datetime
import calendar
import holidays
import io
import os
import requests
import time
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side

# --- KONFIGURÁCIA STRÁNKY ---
st.set_page_config(page_title="AUTOCESTAK pro", layout="wide", initial_sidebar_state="collapsed")

# --- ŠTÝL ORÁMOVANIA PRE EXCEL ---
thin_border = Border(
    left=Side(style='thin'), 
    right=Side(style='thin'), 
    top=Side(style='thin'), 
    bottom=Side(style='thin')
)

# --- CACHOVANIE KURZOV ECB ---
@st.cache_data(ttl=3600)
def get_exchange_rate(currency):
    try:
        response = requests.get("https://api.frankfurter.app/latest?from=EUR")
        data = response.json()
        rates = data.get("rates", {})
        if currency in rates:
            return rates[currency]
    except Exception as e:
        pass
    fallbacks = {"CZK": 25.3, "SEK": 11.2, "HUF": 395.0}
    return fallbacks.get(currency, 1.0)

# --- CACHOVANIE REÁLNYCH VZDIALENOSTÍ Z MÁP ---
@st.cache_data(ttl=86400)
def get_real_distance(start_city, end_city):
    try:
        headers = {'User-Agent': 'AutocestakPro/1.0 (sebastian@jmcredit.sk)'}
        s_url = f"https://nominatim.openstreetmap.org/search?q={start_city},+Slovakia&format=json&limit=1"
        e_url = f"https://nominatim.openstreetmap.org/search?q={end_city},+Slovakia&format=json&limit=1"
        
        s_res = requests.get(s_url, headers=headers).json()
        time.sleep(0.5) # Ochrana proti zablokovaniu serverom
        e_res = requests.get(e_url, headers=headers).json()
        
        if s_res and e_res:
            lon1, lat1 = s_res[0]['lon'], s_res[0]['lat']
            lon2, lat2 = e_res[0]['lon'], e_res[0]['lat']
            
            route_url = f"http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=false"
            r_res = requests.get(route_url).json()
            if r_res.get("code") == "Ok":
                return round(r_res["routes"][0]["distance"] / 1000) # Prevod z metrov na km
    except Exception as e:
        pass
    return random.randint(30, 80) # Núdzová záloha

# --- JAZYKOVÝ SLOVNÍK ---
if "lang" not in st.session_state: st.session_state["lang"] = "SK"
if "page" not in st.session_state: st.session_state["page"] = "Domov"
if "authenticated" not in st.session_state: st.session_state["authenticated"] = False
if "show_login" not in st.session_state: st.session_state["show_login"] = False

translations = {
    "SK": {
        "nav_home": "Domov", "nav_cestaky": "Cesťáky", "nav_support": "Podpora", "nav_about": "O nás",
        "login_btn": "Prihlásenie", "logout_btn": "Odhlásiť",
        "hero_title": "Napreduj s automatizovaním cesťákov s nami",
        "hero_sub": "Sme tu, aby sme pomohli a zefektívnili vašu prácu.",
        "contact_small": "Zavolajte nám a my vám pomôžeme",
        "plan_mo": "Mesačné predplatné", "plan_yr": "Ročné predplatné", "btn_buy": "Kúpiť",
        "login_title": "Prístup do generátora", "login_pass": "Heslo", "login_submit": "Vstúpiť"
    }
}
t = translations[st.session_state["lang"]]

# --- CSS STYLING ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;800&display=swap');
    html, body, [class*="css"], .stApp { font-family: 'Inter', sans-serif !important; background-color: #ffffff !important; color: #111111 !important; }
    [data-testid="collapsedControl"] { display: none !important; }
    [data-testid="stSidebar"] { display: none !important; }
    .nav-btn > button { background-color: transparent !important; color: #111111 !important; font-weight: 500 !important; border: none !important; box-shadow: none !important; transition: 0.2s; padding: 0 10px !important; }
    .nav-btn > button:hover { color: #555555 !important; }
    .login-btn > button { background-color: #f4f4f5 !important; color: #111 !important; border-radius: 20px !important; font-weight: 600; border: none !important; padding: 0 20px !important; transition: 0.2s; }
    .login-btn > button:hover { background-color: #e4e4e7 !important; }
    .black-box { background-color: #111111; color: #ffffff; padding: 40px; border-radius: 12px; text-align: center; }
    .black-box h4 { color: #aaaaaa; font-weight: 400; margin-bottom: 10px; }
    .black-box h2 { color: #ffffff; font-size: 38px; margin: 10px 0 30px 0; font-weight: 800; }
    .buy-btn > button { background-color: #ffffff !important; color: #111111 !important; border-radius: 6px !important; font-weight: 600 !important; border: none !important; width: 100%; height: 3em; text-transform: uppercase; letter-spacing: 1px; transition: 0.2s; }
    .buy-btn > button:hover { background-color: #f4f4f5 !important; }
    .contact-box { background-color: #f8f9fa; border: 1px solid #eeeeee; padding: 30px; border-radius: 16px; margin-top: 40px; display: inline-block; min-width: 350px; }
    .contact-box .small-text { color: #888888; font-size: 13px; font-weight: 600; text-transform: uppercase; margin-bottom: 15px; letter-spacing: 0.5px; }
    .contact-box h3 { font-size: 24px; font-weight: 800; margin: 0 0 5px 0; }
    .contact-box .email { color: #555555; font-size: 15px; margin: 0; }
    .hero-title { font-size: 54px; font-weight: 800; line-height: 1.1; margin-top: 60px; margin-bottom: 20px; letter-spacing: -1.5px; }
    .hero-subtitle { font-size: 20px; color: #555555; font-weight: 400; max-width: 600px; margin-bottom: 40px; }
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] { background-color: #f4f4f5 !important; color: #111111 !important; border: 1px solid #e4e4e7 !important; border-radius: 6px !important; }
    label, label p { color: #333333 !important; font-weight: 600 !important; font-size: 14px !important; margin-bottom: 4px !important; }
    .gen-btn > button { background-color: #111111 !important; color: #ffffff !important; width: 100%; height: 3.5em; border-radius: 8px !important; font-weight: 600 !important; border: none !important; transition: 0.2s; }
    .gen-btn > button:hover { background-color: #333333 !important; }
    .verify-link { font-size: 12px; margin-top: -10px; margin-bottom: 15px; color: #111; font-weight: 500; }
    .verify-link a { color: #0066cc !important; text-decoration: underline !important; }
    .stRadio > div { flex-direction: row; gap: 20px; background-color: #f8f9fa; padding: 15px; border-radius: 10px; border: 1px solid #eee; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- NAVIGÁCIA ---
col_logo, col_nav0, col_nav1, col_nav2, col_nav3, col_space, col_login = st.columns([2.5, 0.8, 0.8, 0.8, 0.8, 2.3, 1.5])
with col_logo:
    st.markdown("<h3 style='margin:0; padding:0;'>AUTOCESTAK pro</h3>", unsafe_allow_html=True)
with col_nav0:
    st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
    if st.button(t["nav_home"]): st.session_state["page"] = "Domov"; st.session_state["show_login"] = False
    st.markdown('</div>', unsafe_allow_html=True)
with col_nav1:
    st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
    if st.button(t["nav_cestaky"]): st.session_state["page"] = "Cesťáky"; st.session_state["show_login"] = False
    st.markdown('</div>', unsafe_allow_html=True)
with col_nav2:
    st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
    if st.button(t["nav_support"]): st.session_state["page"] = "Podpora"; st.session_state["show_login"] = False
    st.markdown('</div>', unsafe_allow_html=True)
with col_nav3:
    st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
    if st.button(t["nav_about"]): st.session_state["page"] = "O nás"; st.session_state["show_login"] = False
    st.markdown('</div>', unsafe_allow_html=True)
with col_login:
    st.markdown('<div class="login-btn">', unsafe_allow_html=True)
    if not st.session_state["authenticated"]:
        if st.button(t["login_btn"]): 
            st.session_state["show_login"] = not st.session_state["show_login"]
            st.rerun()
    else:
        if st.button(t["logout_btn"]): 
            st.session_state["authenticated"] = False
            st.session_state["page"] = "Domov"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# --- LOGIN FORM ---
if st.session_state["show_login"] and not st.session_state["authenticated"]:
    st.markdown(f"<h3 style='text-align: center;'>{t['login_title']}</h3>", unsafe_allow_html=True)
    l1, l2, l3 = st.columns([1, 1, 1])
    with l2:
        pwd = st.text_input(t["login_pass"], type="password")
        st.markdown('<div style="margin-top: 15px;"></div>', unsafe_allow_html=True)
        st.markdown('<div class="login-btn" style="text-align: center;">', unsafe_allow_html=True)
        if st.button(t["login_submit"]):
            if pwd == "levice2026":
                st.session_state["authenticated"] = True
                st.session_state["show_login"] = False
                st.session_state["page"] = "Cesťáky"
                st.rerun()
            else:
                st.error("Nesprávne heslo.")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- OBSAH STRÁNOK ---
if st.session_state["page"] == "Domov":
    c1, c2 = st.columns([1.5, 1])
    with c1:
        st.markdown(f"<div class='hero-title'>{t['hero_title']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='hero-subtitle'>{t['hero_sub']}</div>", unsafe_allow_html=True)
        st.markdown(f"""
            <div class='contact-box'>
                <div class='small-text'>{t['contact_small']}</div>
                <h3>📞 +421 911 781 362</h3>
                <p class='email'>✉️ sebastian.stuller@jmcredit.sk</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("<br>", unsafe_allow_html=True)
    
    f1, f2 = st.columns([1, 2])
    with f1:
        if os.path.exists("profilovka.png"): st.image("profilovka.png", use_container_width=True)
        elif os.path.exists("profilovka.jpg"): st.image("profilovka.jpg", use_container_width=True)
        else: st.info("Nahrajte svoju fotku na GitHub s názvom 'profilovka.jpg'")
            
    with f2:
        st.markdown("<h2 style='margin-bottom: 20px;'>Automatizácia pre moderné účtovníctvo</h2>", unsafe_allow_html=True)
        st.write("""
        Našou víziou je posunúť účtovníctvo do 21. storočia. Chápeme, že pre účtovné kancelárie a podnikateľov je čas tou najcennejšou komoditou. 
        Preto sme vytvorili **AUTOCESTAK pro** – nástroj, ktorý plne automatizuje únavnú administratívu okolo cestovných náhrad, eliminuje chybovosť pri výpočtoch a šetrí desiatky hodín vašej práce mesačne. 
        """)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div style='background-color: #f8f9fa; padding: 25px; border-radius: 12px; border-left: 4px solid #111;'>
            <h4 style='margin-top: 0;'>Kontakt & Fakturačné údaje</h4>
            <b>Meno:</b> Sebastián Štuller<br>
            <b>Spoločnosť:</b> jmcreditplus s.r.o.<br>
            <b>Adresa:</b> Obchodný dom Leo, Ul. Ľ. Štúra 7101/1A, 934 01 Levice<br>
            <b>IČO:</b> 36 848 549<br>
            <b>IČ DPH:</b> SK 2022477479<br>
            <b>Mobil:</b> +421 911 781 362<br>
            <b>E-mail:</b> sebastian.stuller@jmcredit.sk
        </div>
        """, unsafe_allow_html=True)

elif st.session_state["page"] == "Cesťáky":
    if not st.session_state["authenticated"]:
        st.markdown("<br><br>", unsafe_allow_html=True)
        p1, p2, p3, p4 = st.columns([1, 2, 2, 1])
        with p2:
            st.markdown(f"""
                <div class="black-box">
                    <h4>{t['plan_mo']}</h4>
                    <h2>9,99 €</h2>
                </div>
            """, unsafe_allow_html=True)
            st.markdown('<div class="buy-btn" style="margin-top:-20px; position:relative; z-index:10; padding:0 40px;">', unsafe_allow_html=True)
            if st.button(t["btn_buy"], key="b1"): st.info("Platobná brána sa pripravuje.")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with p3:
            st.markdown(f"""
                <div class="black-box">
                    <h4>{t['plan_yr']}</h4>
                    <h2>100 €</h2>
                </div>
            """, unsafe_allow_html=True)
            st.markdown('<div class="buy-btn" style="margin-top:-20px; position:relative; z-index:10; padding:0 40px;">', unsafe_allow_html=True)
            if st.button(t["btn_buy"] + " ", key="b2"): st.info("Platobná brána sa pripravuje.")
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.title("Generátor cesťákov")
        
        typ_cesty = st.radio("Vyberte typ pracovných ciest:", 
                             ["1️⃣ Klasické jednodňové cesty (Každý deň návrat domov)", 
                              "2️⃣ Turnus / Dlhodobá cesta (Ubytovanie v zahraničí/mimo bydliska)"])
        st.markdown("<br>", unsafe_allow_html=True)
        
        mesiace_zoznam = ["Január", "Február", "Marec", "Apríl", "Máj", "Jún", "Júl", "August", "September", "Október", "November", "December"]
        c_krajina, c_rok, c_mes = st.columns(3)
        with c_krajina: krajina = st.selectbox("Krajina cesty / turnusu", ["Slovensko", "Nemecko", "Rakúsko", "Belgicko", "Maďarsko", "Česko", "Švédsko"])
        with c_rok: rok = st.selectbox("Rok", [2024, 2025, 2026], index=2)
        with c_mes: mesiac_nazov = st.selectbox("Mesiac", mesiace_zoznam)
        
        mesiac_int = mesiace_zoznam.index(mesiac_nazov) + 1
        dni_v_mesiaci = calendar.monthrange(rok, mesiac_int)[1]
        
        sk_hol_obj = holidays.Slovakia(years=rok)
        vsetky_dni_v_mesiaci = [datetime.date(rok, mesiac_int, d) for d in range(1, dni_v_mesiaci + 1)]
        nedele_a_sviatky = [d for d in vsetky_dni_v_mesiaci if d.weekday() == 6 or d in sk_hol_obj]
        moznosti_ned_svi = {d.strftime("%d.%m.%Y") + (" (Sviatok)" if d in sk_hol_obj else " (Nedeľa)"): d for d in nedele_a_sviatky}
        
        def_amort = 0.313 if rok >= 2026 else (0.265 if mesiac_int <= 2 else (0.281 if mesiac_int <= 5 else 0.296))
        
        kurz_mena = "EUR"
        def_kurz = 1.0
        stravne_local = 0.0
        
        if krajina == "Slovensko":
            def_stravne_eur = 9.30 if rok >= 2026 else (8.30 if mesiac_int <= 3 else (8.80 if mesiac_int <= 11 else 9.30))
        elif krajina in ["Nemecko", "Rakúsko", "Belgicko"]: def_stravne_eur = 45.0
        elif krajina == "Maďarsko": def_stravne_eur = 39.0
        elif krajina == "Česko": 
            stravne_local = 600.0; kurz_mena = "CZK"; def_kurz = get_exchange_rate("CZK"); def_stravne_eur = round(stravne_local / def_kurz, 2)
        elif krajina == "Švédsko":
            stravne_local = 455.0; kurz_mena = "SEK"; def_kurz = get_exchange_rate("SEK"); def_stravne_eur = round(stravne_local / def_kurz, 2)

        st.markdown("---")
        
        vybrane_nedele_sviatky = [] 
        
        if "Klasické" in typ_cesty:
            st.subheader("Parametre pre Jednodňové cesty")
            col_x, col_y = st.columns(2)
            with col_x:
                meno = st.text_input("Meno zamestnanca", value="Sebastián Štuller")
                spz = st.text_input("ŠPZ vozidla", value="LV-000XX")
                start_miesta_input = st.text_input("Štartovacie miesto (oddelené čiarkou)", value="Mýtne Ludany, Levice")
                mesta_sk = st.text_input("Konečné destinácie (oddelené čiarkou)", value="Bratislava, Nitra, Trenčín")
                
                praca_sobota = st.checkbox("Pracuje sa aj v Sobotu? (Generovať cesty na soboty)", value=False)
                praca_nedela = st.checkbox("Pracuje sa aj v Nedeľu / Sviatok? (Vybrať konkrétne dni)", value=False, key="ned1")
                if praca_nedela:
                    if moznosti_ned_svi:
                        vyber = st.multiselect("Vyberte konkrétne nedele/sviatky, kedy sa pracovalo:", options=list(moznosti_ned_svi.keys()), key="ms1")
                        vybrane_nedele_sviatky = [moznosti_ned_svi[v] for v in vyber]
                    else:
                        st.info("V tomto mesiaci nie sú žiadne sviatky ani nedele.")
                
                st.markdown("<br>", unsafe_allow_html=True)
                noclazne_suma = st.number_input("Nocľažné / Ubytovanie celkom (€)", value=0.0, step=10.0)
                vedlajsie_suma = st.number_input("Nutné vedľajšie výdavky celkom (€)", value=0.0, step=10.0)
                
            with col_y:
                cielova_suma = st.number_input("Cieľová suma (€)", value=1500.0, step=50.0)
                spotreba = st.number_input("Spotreba (l/100km)", value=6.5, step=0.1)
                cena_phm = st.number_input("Cena PHM (€/l)", value=1.62, step=0.01)
                st.markdown('<div class="verify-link">🔍 <a href="https://datacube.statistics.sk/#!/view/sk/VBD_INTERN/sp0202ms/v_sp0202ms_00_00_00_sk" target="_blank">Overiť ceny PHM (ŠÚ SR)</a></div>', unsafe_allow_html=True)
                
                amortizacia = st.number_input("Amortizácia (€/km)", value=float(def_amort), format="%.3f")
                st.markdown('<div class="verify-link">🔍 <a href="https://www.slov-lex.sk/pravne-predpisy/SK/ZZ/2024/73/" target="_blank">Overiť sadzbu amortizácie (Slov-lex)</a></div>', unsafe_allow_html=True)
                
                if krajina != "Slovensko":
                    sk_zaklad = 9.30 if rok >= 2026 else (8.30 if mesiac_int <= 3 else (8.80 if mesiac_int <= 11 else 9.30))
                    if kurz_mena != "EUR":
                        kurz_input = st.number_input(f"Aktuálny kurz (1 EUR = X {kurz_mena})", value=float(def_kurz), format="%.3f")
                        st.markdown(f'<div class="verify-link">🔍 <a href="https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html" target="_blank">Overiť kurz na ECB</a></div>', unsafe_allow_html=True)
                        zaklad_zahranicie = round(stravne_local / kurz_input, 2)
                    else:
                        zaklad_zahranicie = def_stravne_eur
                        
                    st.markdown("<br><b>🇪🇺 Zákonné krátenie stravného (Prechod hraníc):</b>", unsafe_allow_html=True)
                    cas_zahranicie = st.selectbox("Čas strávený v zahraničí (podľa Min. práce):", 
                                                  ["do 6 hodín (25 % zo základnej sadzby)", "nad 6 až do 12 hodín (50 % zo základnej sadzby)", "nad 12 hodín (100 % zo základnej sadzby)"], index=1)
                    if "do 6" in cas_zahranicie: zah_vypocet = zaklad_zahranicie * 0.25
                    elif "do 12" in cas_zahranicie: zah_vypocet = zaklad_zahranicie * 0.50
                    else: zah_vypocet = zaklad_zahranicie
                        
                    stravne_zah_cast = st.number_input("Zahraničná časť stravného (€)", value=float(zah_vypocet), step=0.10)
                    st.markdown('<div class="verify-link">🔍 <a href="https://www.employment.gov.sk/sk/praca-zamestnanost/vztah-zamestnanca-zamestnavatela/cestovne-nahrady/zahranicna-cesta/stravne.html" target="_blank">Overiť zahraničné stravné (Ministerstvo práce)</a></div>', unsafe_allow_html=True)

                    stravne_sk_cast = st.number_input("Slovenská časť stravného v € (ak vznikol nárok v SR)", value=float(sk_zaklad), step=0.10)
                    st.markdown('<div class="verify-link">🔍 <a href="https://www.ip.gov.sk/cestovne-nahrady-pri-pracovnej-ceste/" target="_blank">Overiť tuzemské stravné (Inšpektorát práce)</a></div>', unsafe_allow_html=True)
                    
                    stravne_val = stravne_sk_cast + stravne_zah_cast
                    st.success(f"💡 Výsledné stravné na 1 deň cesty (SK + Zahraničie): **{stravne_val:.2f} €**")
                else:
                    stravne_val = st.number_input("Stravné v € na deň (SR)", value=float(def_stravne_eur), step=0.10)
                    st.markdown('<div class="verify-link">🔍 <a href="https://www.ip.gov.sk/cestovne-nahrady-pri-pracovnej-ceste/" target="_blank">Overiť sadzby a časové pásma SR (Inšpektorát práce)</a></div>', unsafe_allow_html=True)

        else: # TURNUS
            st.subheader("Parametre pre Turnus / Zahraničnú montáž")
            st.info("💡 Tento režim vygeneruje 1. deň ako Cestu na turnus, stredné dni ako denné dochádzanie z ubytovania do práce a posledný deň ako Návrat domov.")
            col_x, col_y = st.columns(2)
            with col_x:
                meno = st.text_input("Meno zamestnanca", value="Sebastián Štuller")
                spz = st.text_input("ŠPZ vozidla", value="LV-000XX")
                
                start_turnus = st.date_input("Dátum odchodu na turnus", datetime.date(rok, mesiac_int, 1))
                ma_navrat = st.checkbox("Vracia sa v tomto mesiaci domov?", value=True)
                if ma_navrat:
                    end_turnus = st.date_input("Dátum návratu domov", datetime.date(rok, mesiac_int, min(28, dni_v_mesiaci)))
                else:
                    end_turnus = datetime.date(rok, mesiac_int, dni_v_mesiaci)
                    
                praca_sobota = st.checkbox("Pracuje a dochádza z ubytovania na stavbu aj v Sobotu?", value=True)
                praca_nedela = st.checkbox("Pracuje a dochádza na stavbu aj v Nedeľu / Sviatok? (Vybrať konkrétne dni)", value=False, key="ned2")
                if praca_nedela:
                    if moznosti_ned_svi:
                        vyber = st.multiselect("Vyberte konkrétne nedele/sviatky, kedy sa na turnuse pracovalo:", options=list(moznosti_ned_svi.keys()), key="ms2")
                        vybrane_nedele_sviatky = [moznosti_ned_svi[v] for v in vyber]
                
            with col_y:
                miesto_domov = st.text_input("Miesto bydliska / Štart", value="Žemberovce")
                miesto_ubytovanie = st.text_input("Miesto ubytovania na turnuse", value="Heinsberg, Nemecko")
                miesto_praca = st.text_input("Miesto výkonu práce (Stavba)", value="Výkon práce Heinsberg")
                
                km_tam = st.number_input("Vzdialenosť na turnus (Cesta tam v km)", value=1150)
                km_denne = st.number_input("Denné dochádzanie do práce (Ubytovanie -> Stavba -> Ubytovanie) v km", value=15)
                
                spotreba = st.number_input("Spotreba (l/100km)", value=6.5, step=0.1)
                cena_phm = st.number_input("Cena PHM (€/l)", value=1.62, step=0.01)
                st.markdown('<div class="verify-link">🔍 <a href="https://datacube.statistics.sk/#!/view/sk/VBD_INTERN/sp0202ms/v_sp0202ms_00_00_00_sk" target="_blank">Overiť ceny PHM (ŠÚ SR)</a></div>', unsafe_allow_html=True)
                
                amortizacia = st.number_input("Amortizácia (€/km)", value=float(def_amort), format="%.3f")
                st.markdown('<div class="verify-link">🔍 <a href="https://www.slov-lex.sk/pravne-predpisy/SK/ZZ/2024/73/" target="_blank">Overiť sadzbu amortizácie (Slov-lex)</a></div>', unsafe_allow_html=True)
                
                if krajina != "Slovensko":
                    sk_zaklad = 9.30 if rok >= 2026 else (8.30 if mesiac_int <= 3 else (8.80 if mesiac_int <= 11 else 9.30))
                    if kurz_mena != "EUR":
                        kurz_input = st.number_input(f"Aktuálny kurz (1 EUR = X {kurz_mena})", value=float(def_kurz), format="%.3f")
                        st.markdown(f'<div class="verify-link">🔍 <a href="https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html" target="_blank">Overiť kurz na ECB</a></div>', unsafe_allow_html=True)
                        zaklad_zahranicie = round(stravne_local / kurz_input, 2)
                    else:
                        zaklad_zahranicie = def_stravne_eur
                        
                    st.markdown("<br><b>🇪🇺 Zákonné krátenie stravného (Prechod hraníc):</b>", unsafe_allow_html=True)
                    cas_zahranicie = st.selectbox("Čas strávený v zahraničí (podľa Min. práce):", 
                                                  ["do 6 hodín (25 % zo základnej sadzby)", "nad 6 až do 12 hodín (50 % zo základnej sadzby)", "nad 12 hodín (100 % zo základnej sadzby)"], index=1, key="cas2")
                    if "do 6" in cas_zahranicie: zah_vypocet = zaklad_zahranicie * 0.25
                    elif "do 12" in cas_zahranicie: zah_vypocet = zaklad_zahranicie * 0.50
                    else: zah_vypocet = zaklad_zahranicie
                        
                    stravne_zah_cast = st.number_input("Zahraničná časť stravného (€)", value=float(zah_vypocet), step=0.10, key="zah_turnus")
                    st.markdown('<div class="verify-link">🔍 <a href="https://www.employment.gov.sk/sk/praca-zamestnanost/vztah-zamestnanca-zamestnavatela/cestovne-nahrady/zahranicna-cesta/stravne.html" target="_blank">Overiť zahraničné stravné (Ministerstvo práce)</a></div>', unsafe_allow_html=True)

                    stravne_sk_cast = st.number_input("Slovenská časť stravného v € (ak vznikol nárok v SR)", value=float(sk_zaklad), step=0.10, key="sk_turnus")
                    st.markdown('<div class="verify-link">🔍 <a href="https://www.ip.gov.sk/cestovne-nahrady-pri-pracovnej-ceste/" target="_blank">Overiť tuzemské stravné (Inšpektorát práce)</a></div>', unsafe_allow_html=True)
                    
                    stravne_val = stravne_sk_cast + stravne_zah_cast
                    st.success(f"💡 Výsledné stravné na 1 deň cesty: **{stravne_val:.2f} €**")
                else:
                    stravne_val = st.number_input("Stravné v € na deň", value=float(def_stravne_eur), step=0.10)
                    st.markdown('<div class="verify-link">🔍 <a href="https://www.slov-lex.sk/pravne-predpisy/SK/ZZ/2024/211/" target="_blank">Overiť stravné (Slov-lex)</a></div>', unsafe_allow_html=True)

        st.markdown('<div style="margin-top:20px;"></div>', unsafe_allow_html=True)
        suhlas = st.checkbox("Potvrdzujem, že zadané údaje sú pravdivé.")
        
        st.markdown('<div class="gen-btn">', unsafe_allow_html=True)
        if st.button("🚀 Vygenerovať profesionálny cesťák"):
            if not suhlas:
                st.error("Musíte súhlasiť s podmienkami (zaškrtnite políčko vyššie).")
            else:
                with st.spinner('Pripravujem dokument a rátam vzdialenosti...'):
                    sadzba_km = amortizacia + ((spotreba / 100) * cena_phm)
                    
                    wb = Workbook()
                    ws = wb.active
                    ws.title = f"Vyúčtovanie_{mesiac_nazov}_{rok}"
                    
                    widths = [14, 30, 20, 10, 15, 12, 12, 12, 12, 14]
                    for i, w in enumerate(widths): ws.column_dimensions[chr(65+i)].width = w

                    ws.merge_cells('A1:J1')
                    ws['A1'] = "VYÚČTOVANIE PRACOVNEJ CESTY"
                    ws['A1'].font = Font(size=14, bold=True); ws['A1'].alignment = Alignment(horizontal="center")

                    ws['A3'] = "Meno a priezvisko:"; ws['C3'] = meno
                    ws['A4'] = "Vozidlo (ŠPZ):"; ws['C4'] = spz
                    ws['A5'] = "Obdobie:"; ws['C5'] = f"{mesiac_nazov} {rok}"
                    
                    # --- NOVINKA: ZÁPIS PARAMETROV DO HLAVIČKY EXCELU ---
                    ws['F3'] = "Spotreba (l/100km):"; ws['G3'] = spotreba
                    ws['F4'] = "Cena PHM (€/l):"; ws['G4'] = cena_phm
                    ws['F5'] = "Amortizácia (€/km):"; ws['G5'] = amortizacia
                    ws['F6'] = "Sadzba celkom (€/km):"; ws['G6'] = round(sadzba_km, 3)

                    for r in range(3,7): 
                        ws[f'A{r}'].font = Font(bold=True)
                        ws[f'F{r}'].font = Font(bold=True)
                        ws[f'F{r}'].alignment = Alignment(horizontal="right")
                        ws[f'G{r}'].alignment = Alignment(horizontal="left")

                    headers = ["Dátum", "Miesto (Od-Do)", "Vozidlo", "Km", "Čas", "Cestovné", "Stravné", "Ubytko", "Vedľajšie", "Spolu (€)"]
                    row_h = 8
                    for c, text in enumerate(headers):
                        cell = ws.cell(row=row_h, column=c+1, value=text)
                        cell.font = Font(bold=True); cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True); cell.border = thin_border

                    curr = 9
                    
                    if "Klasické" in typ_cesty:
                        dni = []
                        for d in vsetky_dni_v_mesiaci:
                            is_standard_workday = d.weekday() <= (5 if praca_sobota else 4) and d not in sk_hol_obj
                            if is_standard_workday or (d in vybrane_nedele_sviatky):
                                dni.append(d)
                        
                        random.shuffle(dni)
                        start_mesta_list = [s.strip() for s in start_miesta_input.split(',')]
                        mesta_list = [m.strip() for m in mesta_sk.split(',')]
                        
                        aktualna_suma = noclazne_suma + vedlajsie_suma
                        dosiahnuta_suma = False
                        vybrane_cesty = []
                        
                        for idx, d in enumerate(dni):
                            if aktualna_suma >= cielova_suma:
                                dosiahnuta_suma = True
                                break
                                
                            start_m = random.choice(start_mesta_list)
                            end_m = random.choice(mesta_list)
                            if start_m == end_m: continue
                            
                            km_jedna_cesta = get_real_distance(start_m, end_m)
                            km_den_spolu = km_jedna_cesta * 2
                            
                            cesto = km_den_spolu * sadzba_km
                            total = cesto + stravne_val
                            aktualna_suma += total
                            
                            vybrane_cesty.append({
                                "datum": d, "start": start_m, "end": end_m, "km": km_den_spolu, 
                                "cesto": cesto, "total": total
                            })
                            
                        vybrane_cesty = sorted(vybrane_cesty, key=lambda x: x["datum"])
                        
                        for idx, cesta in enumerate(vybrane_cesty):
                            akt_noc = noclazne_suma if idx == 0 else 0.0
                            akt_vedl = vedlajsie_suma if idx == (len(vybrane_cesty)-1) else 0.0
                            celkovy_total = cesta["total"] + akt_noc + akt_vedl
                            
                            ws.append([cesta["datum"].strftime("%d.%m.%Y"), f"{cesta['start']} -> {cesta['end']}", spz, cesta["km"], "08:00", round(cesta["cesto"], 2), stravne_val, akt_noc if akt_noc>0 else "", akt_vedl if akt_vedl>0 else "", round(celkovy_total, 2)])
                            ws.append(["", f"{cesta['end']} -> {cesta['start']}", "", "", "16:30", "", "", "", "", ""])
                            
                            for r_off in [0, 1]:
                                for c_idx in range(1, 11):
                                    ws.cell(row=curr+r_off, column=c_idx).border = thin_border; ws.cell(row=curr+r_off, column=c_idx).alignment = Alignment(horizontal="center", vertical="center")
                            curr += 2
                            
                        if not dosiahnuta_suma and aktualna_suma < (cielova_suma * 0.95):
                            st.warning(f"⚠️ UPOZORNENIE (Reálne GPS mapy): Vzhľadom na reálne vzdialenosti medzi zadanými mestami nebolo možné dosiahnuť {cielova_suma} €. Vygenerovalo sa {aktualna_suma:.2f} €. Pre vyššiu sumu musíte pridať vzdialenejšie mestá do zoznamu.")
                            
                    else:
                        for day in range(1, dni_v_mesiaci + 1):
                            d = datetime.date(rok, mesiac_int, day)
                            if d < start_turnus or (ma_navrat and d > end_turnus): continue
                            
                            is_start = (d == start_turnus)
                            is_end = (ma_navrat and d == end_turnus)
                            is_standard_workday = d.weekday() <= (5 if praca_sobota else 4) and d not in sk_hol_obj
                            is_workday = is_standard_workday or (d in vybrane_nedele_sviatky)
                            
                            km = 0; trasa_od = ""; trasa_do = ""; cas_od = "08:00"; cas_do = "16:30"; ma_cestu = False
                            
                            if is_start:
                                km = km_tam; trasa_od = miesto_domov; trasa_do = miesto_ubytovanie; cas_od = "06:00"; cas_do = "20:00"; ma_cestu = True
                            elif is_end:
                                km = km_tam; trasa_od = miesto_ubytovanie; trasa_do = miesto_domov; cas_od = "06:00"; cas_do = "20:00"; ma_cestu = True
                            elif is_workday:
                                km = km_denne; trasa_od = miesto_ubytovanie; trasa_do = miesto_praca; ma_cestu = True
                                
                            cesto = km * sadzba_km if ma_cestu else 0
                            total = cesto + stravne_val
                            
                            if ma_cestu:
                                ws.append([d.strftime("%d.%m.%Y"), f"{trasa_od} -> {trasa_do}", spz, km, cas_od, round(cesto, 2), stravne_val, "", "", round(total, 2)])
                                ws.append(["", f"{trasa_do} -> {trasa_od}", "", "", cas_do, "", "", "", "", ""])
                                for r_off in [0, 1]:
                                    for c_idx in range(1, 11):
                                        ws.cell(row=curr+r_off, column=c_idx).border = thin_border; ws.cell(row=curr+r_off, column=c_idx).alignment = Alignment(horizontal="center", vertical="center")
                                curr += 2
                            else:
                                ws.append([d.strftime("%d.%m.%Y"), "Deň voľna (Ubytovanie)", "", 0, "-", 0, stravne_val, "", "", stravne_val])
                                for c_idx in range(1, 11):
                                    ws.cell(row=curr, column=c_idx).border = thin_border; ws.cell(row=curr, column=c_idx).alignment = Alignment(horizontal="center", vertical="center")
                                curr += 1

                    ws.append([])
                    sum_row = curr + 1
                    ws.cell(row=sum_row, column=1, value="CELKOM K VÝPLATE:").font = Font(bold=True)
                    ws.cell(row=sum_row, column=10, value=f"=SUM(J8:J{curr-1})").font = Font(bold=True)
                    ws.cell(row=sum_row, column=10).border = thin_border

                    ws.append([]); ws.append([])
                    sig_row = ws.max_row + 1
                    ws.cell(row=sig_row, column=1, value="V Leviciach, dňa: " + datetime.date.today().strftime("%d.%m.%Y"))
                    ws.cell(row=sig_row+2, column=1, value="......................................................")
                    ws.cell(row=sig_row+3, column=1, value="Podpis zamestnanca")
                    ws.cell(row=sig_row+2, column=7, value="......................................................")
                    ws.cell(row=sig_row+3, column=7, value="Schválil (podpis a pečiatka)")

                    output = io.BytesIO()
                    wb.save(output)
                    output.seek(0)
                    
                    st.success("✅ Profesionálny dokument vygenerovaný.")
                    st.download_button("📥 Stiahnuť Excel", output, f"Cestak_{meno.replace(' ', '_')}_{mesiac_nazov}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state["page"] == "Podpora":
    st.title("Podpora")
    st.write("V prípade akýchkoľvek problémov s aplikáciou, úpravy sadzieb alebo technickej podpory nás prosím kontaktujte na:")
    st.markdown("""
    * **Telefón:** +421 911 781 362
    * **E-mail:** sebastian.stuller@jmcredit.sk
    """)

elif st.session_state["page"] == "O nás":
    st.title("O projekte AUTOCESTAK pro")
    st.write("""
    **AUTOCESTAK pro** je moderný, plne automatizovaný nástroj vytvorený pre účtovníkov, ekonómov a majiteľov firiem. 
    Našim cieľom je zbaviť vás zbytočnej a zdĺhavej administratívy spojenej s ručným nahadzovaním a prepočítavaním pracovných ciest.
    """)
    st.markdown("""
    ### Čo prinášame:
    * **Presnosť:** Všetky sadzby (amortizácia, stravné) sú priamo viazané na legislatívu a automaticky sa prispôsobujú obdobiu.
    * **Zahraničné meny:** Live kurzy priamo z Európskej centrálnej banky.
    * **Rýchlosť:** Generovanie profesionálnych, naformátovaných Excel dokumentov jedným kliknutím.
    
    Tento systém vyvinul **Sebastián Štuller** pre zefektívnenie účtovných procesov a prispôsobenie moderným štandardom 21. storočia.
    """)
