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
        "login_title": "Prístup do generátora", "login_pass": "Heslo", "login_submit": "Vstúpiť",
        "gen_title": "Generátor cesťákov"
    },
    "EN": {
        "nav_home": "Home", "nav_cestaky": "App", "nav_support": "Support", "nav_about": "About Us",
        "login_btn": "Login", "logout_btn": "Logout",
        "hero_title": "Advance your travel expense automation with us",
        "hero_sub": "We are here to help and streamline your workflow.",
        "contact_small": "Call us and we will help you",
        "plan_mo": "Monthly Subscription", "plan_yr": "Yearly Subscription", "btn_buy": "Buy now",
        "login_title": "Generator Access", "login_pass": "Password", "login_submit": "Enter",
        "gen_title": "Expense Generator"
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
    .lang-btn > button { background-color: transparent !important; color: #aaaaaa !important; font-weight: 600 !important; border: none !important; box-shadow: none !important; padding: 0 5px !important; min-width: auto !important; height: auto !important; }
    .lang-btn > button:hover { color: #111111 !important; }
    .lang-active > button { background-color: transparent !important; color: #111111 !important; font-weight: 800 !important; border: none !important; border-bottom: 2px solid #111 !important; border-radius: 0 !important; box-shadow: none !important; padding: 0 5px !important; min-width: auto !important; height: auto !important; }
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
    </style>
    """, unsafe_allow_html=True)

# --- NAVIGÁCIA ---
col_logo, col_nav0, col_nav1, col_nav2, col_nav3, col_space, col_sk, col_en, col_login = st.columns([2.5, 0.8, 0.8, 0.8, 0.8, 1.5, 0.4, 0.4, 1.5])
with col_logo:
    if os.path.exists("logo.png.png"): st.image("logo.png.png", width=160)
    elif os.path.exists("logo.png"): st.image("logo.png", width=160)
    else: st.markdown("<h3 style='margin:0; padding:0;'>AUTOCESTAK pro</h3>", unsafe_allow_html=True)
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
with col_sk:
    cls = "lang-active" if st.session_state["lang"] == "SK" else "lang-btn"
    st.markdown(f'<div class="{cls}">', unsafe_allow_html=True)
    if st.button("SK", key="lang_sk"): st.session_state["lang"] = "SK"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
with col_en:
    cls = "lang-active" if st.session_state["lang"] == "EN" else "lang-btn"
    st.markdown(f'<div class="{cls}">', unsafe_allow_html=True)
    if st.button("EN", key="lang_en"): st.session_state["lang"] = "EN"; st.rerun()
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
        st.title(t["gen_title"])
        st.markdown("<br>", unsafe_allow_html=True)
        
        # --- NASTAVENIA ČASU A KRAJINY ---
        mesiace_zoznam = ["Január", "Február", "Marec", "Apríl", "Máj", "Jún", "Júl", "August", "September", "Október", "November", "December"]
        c_krajina, c_rok, c_mes = st.columns(3)
        with c_krajina: krajina = st.selectbox("Krajina cesty", ["Slovensko", "Nemecko", "Rakúsko", "Belgicko", "Maďarsko", "Česko", "Švédsko"])
        with c_rok: rok = st.selectbox("Rok", [2024, 2025, 2026], index=2)
        with c_mes: mesiac_nazov = st.selectbox("Mesiac", mesiace_zoznam)
        
        mesiac_int = mesiace_zoznam.index(mesiac_nazov) + 1
        
        # --- LOGIKA PRE AMORTIZÁCIU A STRAVNÉ ---
        def_amort = 0.313
        if rok < 2026:
            if mesiac_int <= 2: def_amort = 0.265
            elif mesiac_int <= 5: def_amort = 0.281
            else: def_amort = 0.296
            
        kurz_mena = "EUR"
        def_kurz = 1.0
        stravne_local = 0.0
        
        if krajina == "Slovensko":
            if rok >= 2026: def_stravne_eur = 9.30
            else:
                if mesiac_int <= 3: def_stravne_eur = 8.30
                elif mesiac_int <= 11: def_stravne_eur = 8.80
                else: def_stravne_eur = 9.30
        elif krajina in ["Nemecko", "Rakúsko", "Belgicko"]: def_stravne_eur = 45.0
        elif krajina == "Maďarsko": def_stravne_eur = 39.0
        elif krajina == "Česko": 
            stravne_local = 600.0; kurz_mena = "CZK"
            def_kurz = get_exchange_rate("CZK")
            def_stravne_eur = round(stravne_local / def_kurz, 2)
        elif krajina == "Švédsko":
            stravne_local = 455.0; kurz_mena = "SEK"
            def_kurz = get_exchange_rate("SEK")
            def_stravne_eur = round(stravne_local / def_kurz, 2)

        st.markdown("---")
        
        col_x, col_space, col_y = st.columns([1, 0.1, 1])
        
        with col_x:
            meno = st.text_input("Meno zamestnanca", value="Sebastián Štuller")
            spz = st.text_input("ŠPZ vozidla", value="LV-000XX")
            start_miesta_input = st.text_input("Štartovacie miesto (oddelené čiarkou)", value="Mýtne Ludany, Levice")
            mesta_sk = st.text_input("Konečné destinácie (oddelené čiarkou)", value="Bratislava, Nitra, Trenčín, Poprad, Žilina")
            
            st.markdown("<br><b>Extra výdavky:</b>", unsafe_allow_html=True)
            noclazne_suma = st.number_input("Nocľažné / Ubytovanie celkom (€)", value=0.0, step=10.0)
            vedlajsie_suma = st.number_input("Nutné vedľajšie výdavky celkom (€)", value=0.0, step=10.0)
            
        with col_y:
            cielova_suma = st.number_input("Cieľová suma (€)", value=1500.0, step=50.0)
            
            spotreba = st.number_input("Spotreba (l/100km)", value=6.5, step=0.1)
            
            cena_phm = st.number_input("Cena PHM (€/l)", value=1.62, step=0.01)
            st.markdown('<div class="verify-link">🔍 <a href="https://datacube.statistics.sk/#!/view/sk/VBD_INTERN/sp0202ms/v_sp0202ms_00_00_00_sk" target="_blank">Overiť ceny PHM (Štatistický úrad SR)</a></div>', unsafe_allow_html=True)
            
            amortizacia = st.number_input("Amortizácia (€/km)", value=float(def_amort), format="%.3f")
            st.markdown('<div class="verify-link">🔍 <a href="https://www.slov-lex.sk/pravne-predpisy/SK/ZZ/2024/73/" target="_blank">Overiť sadzbu amortizácie (Slov-lex)</a></div>', unsafe_allow_html=True)
            
            if kurz_mena != "EUR":
                kurz_input = st.number_input(f"Aktuálny kurz (1 EUR = X {kurz_mena})", value=float(def_kurz), format="%.3f")
                st.markdown(f'<div class="verify-link">🔍 <a href="https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html" target="_blank">Overiť kurz na ECB</a></div>', unsafe_allow_html=True)
                stravne_eur_calc = round(stravne_local / kurz_input, 2)
                stravne_val = st.number_input(f"Stravné v € ({stravne_local} {kurz_mena})", value=float(stravne_eur_calc), step=0.10)
            else:
                stravne_val = st.number_input("Stravné (€/deň)", value=float(def_stravne_eur), step=0.10)
                st.markdown('<div class="verify-link">🔍 <a href="https://www.slov-lex.sk/pravne-predpisy/SK/ZZ/2024/211/" target="_blank">Overiť stravné SR (Slov-lex)</a></div>', unsafe_allow_html=True)

        st.markdown('<div style="margin-top:30px;"></div>', unsafe_allow_html=True)
        
        suhlas = st.checkbox("Potvrdzujem, že zadané údaje sú pravdivé. Som si vedomý právnej zodpovednosti voči daňovému úradu.")
        
        st.markdown('<div class="gen-btn">', unsafe_allow_html=True)
        if st.button("🚀 Vygenerovať profesionálnu tabuľku"):
            if not suhlas:
                st.error("Musíte súhlasiť s podmienkami.")
            else:
                with st.spinner('Pripravujem dáta a formátujem tabuľku...'):
                    start_mesta_list = [s.strip() for s in start_miesta_input.split(',')]
                    mesta_list = [m.strip() for m in mesta_sk.split(',')]
                    sadzba_km = amortizacia + ((spotreba / 100) * cena_phm)
                    
                    sk_holidays = holidays.Slovakia(years=rok)
                    dni = [datetime.date(rok, mesiac_int, d) for d in range(1, calendar.monthrange(rok, mesiac_int)[1] + 1) if datetime.date(rok, mesiac_int, d).weekday() < 5 and datetime.date(rok, mesiac_int, d) not in sk_holidays]
                    random.shuffle(dni)
                    
                    cista_suma_na_cesty = cielova_suma - noclazne_suma - vedlajsie_suma
                    cena_jednej_cesty = (270 * sadzba_km) + stravne_val
                    pocet_ciest = max(1, min(len(dni), int(round(cista_suma_na_cesty / cena_jednej_cesty))))
                    celkove_km = int(round((cista_suma_na_cesty - (pocet_ciest * stravne_val)) / sadzba_km))
                    km_list = [celkove_km // pocet_ciest] * pocet_ciest
                    for i in range(celkove_km % pocet_ciest): km_list[i] += 1
                    vybrane_dni = sorted(dni[:pocet_ciest])

                    # --- EXCEL FORMÁTOVANIE A ZÁPIS ---
                    wb = Workbook()
                    ws = wb.active
                    ws.title = f"Vyúčtovanie_{mesiac_nazov}_{rok}"
                    
                    # Nastavenie šírok stĺpcov
                    widths = [14, 25, 22, 10, 15, 12, 12, 12, 12, 14]
                    for i, w in enumerate(widths): 
                        ws.column_dimensions[chr(65+i)].width = w

                    # ZÁHLAVIE DOKUMENTU
                    ws.merge_cells('A1:J1')
                    ws['A1'] = "VYÚČTOVANIE PRACOVNEJ CESTY"
                    ws['A1'].font = Font(size=14, bold=True)
                    ws['A1'].alignment = Alignment(horizontal="center")

                    ws['A3'] = "Meno a priezvisko:"
                    ws['C3'] = meno
                    ws['A4'] = "Vozidlo (ŠPZ):"
                    ws['C4'] = spz
                    ws['A5'] = "Obdobie:"
                    ws['C5'] = f"{mesiac_nazov} {rok}"
                    
                    for r in range(3,6): 
                        ws[f'A{r}'].font = Font(bold=True)

                    # HLAVIČKA TABUĽKY
                    headers = ["Dátum", "Miesto (Od-Do)", "Vozidlo", "Km", "Čas", "Cestovné", "Stravné", "Ubytko", "Vedľajšie", "Spolu (€)"]
                    ws.append([]) # Voľný riadok 6
                    row_h = 7
                    
                    for c, text in enumerate(headers):
                        cell = ws.cell(row=row_h, column=c+1, value=text)
                        cell.font = Font(bold=True)
                        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
                        cell.border = thin_border

                    # DOPLNENIE DÁT DO TABUĽKY A ORÁMOVANIE
                    curr = 8
                    for idx, d in enumerate(vybrane_dni):
                        km = km_list[idx]
                        akt_noc = noclazne_suma if idx == 0 else 0.0
                        akt_vedl = vedlajsie_suma if idx == (len(vybrane_dni)-1) else 0.0
                        cesto = km * sadzba_km
                        total = cesto + stravne_val + akt_noc + akt_vedl
                        
                        # Prvý riadok cesty (Odchod)
                        ws.append([
                            d.strftime("%d.%m.%Y"), 
                            random.choice(start_mesta_list), 
                            spz, 
                            km, 
                            "08:00", 
                            round(cesto, 2), 
                            stravne_val, 
                            akt_noc if akt_noc > 0 else "", 
                            akt_vedl if akt_vedl > 0 else "", 
                            round(total, 2)
                        ])
                        # Druhý riadok cesty (Príchod)
                        ws.append(["", random.choice(mesta_list), "", "", "16:30", "", "", "", "", ""])
                        
                        # Pridanie orámovania (borders) a zarovnania na oba riadky
                        for r_off in [0, 1]:
                            for c_idx in range(1, 11):
                                ws.cell(row=curr+r_off, column=c_idx).border = thin_border
                                ws.cell(row=curr+r_off, column=c_idx).alignment = Alignment(horizontal="center", vertical="center")
                        curr += 2

                    # SUMA NA KONCI TABUĽKY
                    ws.append([])
                    sum_row = curr + 1
                    ws.cell(row=sum_row, column=1, value="CELKOM K VÝPLATE:").font = Font(bold=True)
                    ws.cell(row=sum_row, column=10, value=f"=SUM(J8:J{curr-1})").font = Font(bold=True)
                    ws.cell(row=sum_row, column=10).border = thin_border

                    # SEKCOA PRE PODPISY
                    ws.append([])
                    ws.append([])
                    sig_row = ws.max_row + 1
                    
                    ws.cell(row=sig_row, column=1, value="V Leviciach, dňa: " + datetime.date.today().strftime("%d.%m.%Y"))
                    
                    # Čiara pre zamestnanca
                    ws.cell(row=sig_row+2, column=1, value="......................................................")
                    ws.cell(row=sig_row+3, column=1, value="Podpis zamestnanca")
                    
                    # Čiara pre schvaľovateľa
                    ws.cell(row=sig_row+2, column=7, value="......................................................")
                    ws.cell(row=sig_row+3, column=7, value="Schválil (podpis a pečiatka)")

                    # ULOŽENIE SÚBORU
                    output = io.BytesIO()
                    wb.save(output)
                    output.seek(0)
                    
                    st.success("✅ Profesionálny dokument bol úspešne vygenerovaný.")
                    st.download_button("📥 Stiahnuť Excel", output, f"Cestak_{meno.replace(' ', '_')}_{mesiac_nazov}_{rok}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state["page"] == "Podpora":
    st.title("Podpora")
    st.write("V prípade problémov s generovaním alebo nastavením sadzieb nás neváhajte kontaktovať na čísle **+421 911 781 362**.")

elif st.session_state["page"] == "O nás":
    st.title("O projekte AUTOCESTAK pro")
    st.markdown("Tento systém vyvinul **Sebastián Štuller** pre zefektívnenie procesov v spoločnosti **jmcreditplus s.r.o.**")
