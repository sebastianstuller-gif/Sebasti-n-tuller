import streamlit as st
import random
import datetime
import calendar
import holidays
import io
import os
import requests
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side

# --- ZÍSKANIE KĽÚČA ---
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]

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

# --- PROFI GOOGLE MAPS VZDIALENOSTI ---
@st.cache_data(ttl=86400)
def get_google_distance(start_city, end_city, api_key):
    if not start_city or not end_city or start_city.strip().lower() == end_city.strip().lower():
        return 0
    try:
        url = "https://maps.googleapis.com/maps/api/distancematrix/json"
        params = {"origins": start_city, "destinations": end_city, "key": api_key}
        res = requests.get(url, params=params, timeout=5).json()
        if res.get("status") == "OK":
            element = res["rows"][0]["elements"][0]
            if element.get("status") == "OK":
                return round(element["distance"]["value"] / 1000)
    except Exception:
        pass
    return 50 

# --- SESSION STATE PRE MANUÁLNE CESTY ---
if "manual_trips" not in st.session_state:
    st.session_state.manual_trips = []
if "temp_stops" not in st.session_state:
    st.session_state.temp_stops = []

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
        "contact_small": "Zavolajte nám a mi vám pomôžeme",
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
    .buy-btn > button { background-color: #ffffff !important; color: #111111 !important; border-radius: 6px !important; width: 100%; height: 3em; text-transform: uppercase; letter-spacing: 1px; }
    .contact-box { background-color: #f8f9fa; border: 1px solid #eeeeee; padding: 30px; border-radius: 16px; margin-top: 40px; }
    .hero-title { font-size: 54px; font-weight: 800; line-height: 1.1; margin-top: 60px; margin-bottom: 20px; letter-spacing: -1.5px; }
    .gen-btn > button { background-color: #111111 !important; color: #ffffff !important; width: 100%; height: 3.5em; border-radius: 8px !important; font-weight: 600 !important; border: none !important; }
    .manual-box { background-color: #f9f9fb; padding: 20px; border-radius: 10px; border: 1px dashed #ccc; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- NAVIGÁCIA ---
col_logo, col_nav0, col_nav1, col_nav2, col_nav3, col_space, col_login = st.columns([2.5, 0.8, 0.8, 0.8, 0.8, 2.3, 1.5])
with col_logo: st.markdown("<h3>AUTOCESTAK pro</h3>", unsafe_allow_html=True)
with col_nav0: 
    if st.button(t["nav_home"]): st.session_state["page"] = "Domov"; st.session_state["show_login"] = False
with col_nav1:
    if st.button(t["nav_cestaky"]): st.session_state["page"] = "Cesťáky"; st.session_state["show_login"] = False

if not st.session_state["authenticated"] and st.session_state["show_login"]:
    st.markdown("---")
    l1, l2, l3 = st.columns([1, 1, 1])
    with l2:
        pwd = st.text_input(t["login_pass"], type="password")
        if st.button(t["login_submit"]):
            if pwd == "levice2026":
                st.session_state["authenticated"] = True
                st.session_state["page"] = "Cesťáky"
                st.rerun()
            else: st.error("Nesprávne heslo.")
    st.stop()

# --- OBSAH ---
if st.session_state["page"] == "Domov":
    st.markdown(f"<div class='hero-title'>{t['hero_title']}</div>", unsafe_allow_html=True)
    st.write("Vitajte v systéme AUTOCESTAK pro.")

elif st.session_state["page"] == "Cesťáky":
    if not st.session_state["authenticated"]:
        st.info("Pre prístup sa prosím prihláste.")
    else:
        st.title("Generátor cesťákov")
        
        typ_cesty = st.radio("Typ cesty:", ["1️⃣ Klasické jednodňové cesty", "2️⃣ Turnus / Dlhodobá cesta"])
        
        mesiace_zoznam = ["Január", "Február", "Marec", "Apríl", "Máj", "Jún", "Júl", "August", "September", "Október", "November", "December"]
        c_krajina, c_rok, c_mes = st.columns(3)
        with c_krajina: krajina = st.selectbox("Krajina", ["Slovensko", "Nemecko", "Rakúsko", "Česko"])
        with c_rok: rok = st.selectbox("Rok", [2024, 2025, 2026], index=2)
        with c_mes: mesiac_nazov = st.selectbox("Mesiac", mesiace_zoznam)
        
        mesiac_int = mesiace_zoznam.index(mesiac_nazov) + 1
        dni_v_mesiaci = calendar.monthrange(rok, mesiac_int)[1]
        sk_hol_obj = holidays.Slovakia(years=rok)

        # SADZBY
        def_amort = 0.313 if rok >= 2026 else 0.296
        stravne_val = 9.30 if krajina == "Slovensko" else 45.0

        st.markdown("---")
        
        if "Klasické" in typ_cesty:
            col_left, col_right = st.columns(2)
            
            with col_left:
                meno = st.text_input("Meno zamestnanca", value="Sebastián Štuller")
                spz = st.text_input("ŠPZ vozidla", value="LV-000XX")
                start_miesta_input = st.text_area("Štartovacie miesta (AI dopĺňanie):", value="Levice")
                mesta_sk = st.text_area("Cieľové destinácie (AI dopĺňanie):", value="Bratislava\nNitra\nPraha\nBrno")
                
            with col_right:
                cielova_suma = st.number_input("Cieľová suma (€)", value=1500.0)
                spotreba = st.number_input("Spotreba (l/100km)", value=6.5)
                cena_phm = st.number_input("Cena PHM (€/l)", value=1.62)
                amortizacia = st.number_input("Amortizácia (€/km)", value=float(def_amort), format="%.3f")
                sadzba_km = amortizacia + ((spotreba / 100) * cena_phm)

            # --- NOVÁ SEKCIÁ: MANUÁLNE CESTY ---
            st.markdown("### 📍 Manuálne pridanie konkrétnych ciest (Fixné dni)")
            with st.container():
                st.markdown('<div class="manual-box">', unsafe_allow_html=True)
                m_col1, m_col2, m_col3 = st.columns([1, 1, 1])
                with m_col1: m_date = st.date_input("Dátum fixnej cesty", datetime.date(rok, mesiac_int, 1))
                with m_col2: m_start = st.text_input("Miesto štartu", value="Levice", key="m_start")
                with m_col3: m_end = st.text_input("Konečný cieľ", value="", placeholder="napr. Praha", key="m_end")
                
                # Medzizastávky
                st.write("---")
                st.write("**Medzizastávky (voliteľné):**")
                for i, stop in enumerate(st.session_state.temp_stops):
                    st.session_state.temp_stops[i] = st.text_input(f"Stredné mesto {i+1}", value=stop, key=f"stop_{i}")
                
                if st.button("➕ Pridať medzizastávku"):
                    st.session_state.temp_stops.append("")
                    st.rerun()
                
                if st.button("✅ Uložiť túto manuálnu cestu do zoznamu"):
                    if m_end:
                        # Vytvorenie trasy: Start -> Stop1 -> Stop2 -> End -> Start
                        full_route = [m_start] + [s for s in st.session_state.temp_stops if s.strip()] + [m_end]
                        st.session_state.manual_trips.append({"date": m_date, "route": full_route})
                        st.session_state.temp_stops = [] # reset
                        st.success("Cesta pridaná do zoznamu.")
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            # Zoznam pridaných ciest
            if st.session_state.manual_trips:
                st.write("**Vaše naplánované manuálne cesty:**")
                for i, trip in enumerate(st.session_state.manual_trips):
                    st.info(f"📅 {trip['date'].strftime('%d.%m.')}: {' -> '.join(trip['route'])}")
                if st.button("🗑️ Vymazať všetky manuálne cesty"):
                    st.session_state.manual_trips = []
                    st.rerun()

            st.markdown("---")
            if st.button("🚀 Vygenerovať profesionálny cesťák"):
                with st.spinner('Počítam trasy cez Google...'):
                    wb = Workbook()
                    ws = wb.active
                    ws.title = "Vyúčtovanie"
                    
                    # Záhlavie tabuľky
                    headers = ["Dátum", "Miesto (Od-Do)", "Vozidlo", "Km", "Čas", "Cestovné", "Stravné", "Ubytko", "Vedľajšie", "Spolu (€)"]
                    for c, text in enumerate(headers):
                        cell = ws.cell(row=8, column=c+1, value=text)
                        cell.font = Font(bold=True); cell.alignment = Alignment(horizontal="center"); cell.border = thin_border

                    curr = 9
                    aktualna_suma = 0.0
                    pouzite_dni = set()

                    # 1. NAJSKÔR SPRACOVAŤ MANUÁLNE CESTY
                    for trip in st.session_state.manual_trips:
                        route = trip["route"]
                        total_km = 0
                        # Výpočet km pre celú trasu (tam aj späť)
                        for j in range(len(route)-1):
                            total_km += get_google_distance(route[j], route[j+1], GOOGLE_API_KEY)
                        # Cesta späť z posledného bodu do štartu
                        total_km += get_google_distance(route[-1], route[0], GOOGLE_API_KEY)
                        
                        cesto = total_km * sadzba_km
                        total = cesto + stravne_val
                        aktualna_suma += total
                        pouzite_dni.add(trip["date"])
                        
                        ws.append([trip["date"].strftime("%d.%m.%Y"), " -> ".join(route), spz, total_km, "08:00", round(cesto, 2), stravne_val, "", "", round(total, 2)])
                        for c_idx in range(1, 11): ws.cell(row=curr, column=c_idx).border = thin_border
                        curr += 1

                    # 2. DOPOČÍTAŤ ZVYŠOK (AI DOPĹŇANIE)
                    if aktualna_suma < cielova_suma:
                        start_mesta = [s.strip() for s in start_miesta_input.split('\n') if s.strip()]
                        ciele = [m.strip() for m in mesta_sk.split('\n') if m.strip()]
                        
                        vsetky_dni = [datetime.date(rok, mesiac_int, d) for d in range(1, dni_v_mesiaci + 1)]
                        pracovne_dni = [d for d in vsetky_dni if d.weekday() < 5 and d not in sk_hol_obj and d not in pouzite_dni]
                        random.shuffle(pracovne_dni)

                        for d in pracovne_dni:
                            if aktualna_suma >= cielova_suma: break
                            s_m = random.choice(start_mesta)
                            e_m = random.choice(ciele)
                            km = get_google_distance(s_m, e_m, GOOGLE_API_KEY) * 2
                            cesto = km * sadzba_km
                            total = cesto + stravne_val
                            aktualna_suma += total
                            
                            ws.append([d.strftime("%d.%m.%Y"), f"{s_m} -> {e_m} -> {s_m}", spz, km, "08:00", round(cesto, 2), stravne_val, "", "", round(total, 2)])
                            for c_idx in range(1, 11): ws.cell(row=curr, column=c_idx).border = thin_border
                            curr += 1

                    # Finálne súčty a export
                    ws.cell(row=curr+1, column=10, value=f"=SUM(J9:J{curr})").font = Font(bold=True)
                    
                    output = io.BytesIO()
                    wb.save(output)
                    st.download_button("📥 Stiahnuť Excel", output.getvalue(), "Cestak.xlsx")
