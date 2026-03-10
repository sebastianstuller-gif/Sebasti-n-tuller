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
st.set_page_config(page_title="AUTOCESTAK pro", layout="wide", initial_sidebar_state="collapsed")

# --- JAZYKOVÝ SLOVNÍK (SK / EN) ---
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

# --- POKROČILÝ CSS STYLING ---
# --- POKROČILÝ CSS STYLING ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"], .stApp { font-family: 'Inter', sans-serif; background-color: #ffffff !important; color: #000000 !important; }
    
    /* Skrytie bočného panela */
    [data-testid="collapsedControl"] { display: none !important; }
    [data-testid="stSidebar"] { display: none !important; }
    
    /* Navigácia */
    .nav-btn > button { background-color: transparent !important; color: #000000 !important; font-weight: 600 !important; border: none !important; box-shadow: none !important; transition: 0.2s; padding: 0 10px !important; }
    .nav-btn > button:hover { color: #ff4b4b !important; }
    
    /* Jazyk */
    .lang-btn > button { background-color: transparent !important; color: #aaaaaa !important; font-weight: 600 !important; border: none !important; box-shadow: none !important; padding: 0 5px !important; min-width: auto !important; height: auto !important; }
    .lang-btn > button:hover { color: #000000 !important; }
    .lang-active > button { background-color: transparent !important; color: #000000 !important; font-weight: 800 !important; border: none !important; border-bottom: 2px solid #000 !important; border-radius: 0 !important; box-shadow: none !important; padding: 0 5px !important; min-width: auto !important; height: auto !important; }
    
    .login-btn > button { background-color: #f0f0f0 !important; color: #000 !important; border-radius: 20px !important; font-weight: 600; border: none !important; padding: 0 20px !important; }
    
    .black-box { background-color: #111111; color: #ffffff; padding: 40px; border-radius: 12px; text-align: center; }
    .black-box h4 { color: #aaaaaa; font-weight: 400; margin-bottom: 10px; }
    .black-box h2 { color: #ffffff; font-size: 38px; margin: 10px 0 30px 0; font-weight: 800; }
    
    .buy-btn > button { background-color: #ffffff !important; color: #000000 !important; border-radius: 6px !important; font-weight: 600 !important; border: none !important; width: 100%; height: 3em; text-transform: uppercase; letter-spacing: 1px; }
    .buy-btn > button:hover { background-color: #dddddd !important; }
    
    .contact-box { background-color: #f8f9fa; border: 1px solid #eeeeee; padding: 30px; border-radius: 16px; margin-top: 40px; display: inline-block; min-width: 350px; }
    .contact-box .small-text { color: #888888; font-size: 13px; font-weight: 600; text-transform: uppercase; margin-bottom: 15px; letter-spacing: 0.5px; }
    .contact-box h3 { font-size: 24px; font-weight: 800; margin: 0 0 5px 0; }
    .contact-box .email { color: #555555; font-size: 15px; margin: 0; }
    
    .hero-title { font-size: 54px; font-weight: 800; line-height: 1.1; margin-top: 60px; margin-bottom: 20px; letter-spacing: -1.5px; }
    .hero-subtitle { font-size: 20px; color: #555555; font-weight: 400; max-width: 600px; margin-bottom: 40px; }
    
    /* --- ULTIMÁTNY FIX PRE BIELE PÍSMO V ČIERNYCH BUNKÁCH --- */
    
    /* 1. Obaly buniek na čierno */
    div[data-baseweb="input"] > div, 
    div[data-baseweb="select"] > div, 
    div[data-baseweb="textarea"] > div,
    .stTextInput div[data-baseweb="input"],
    .stNumberInput div[data-baseweb="input"] { 
        background-color: #111111 !important; 
        border: 1px solid #333333 !important; 
        border-radius: 6px !important; 
    }
    
    /* 2. Samotný text vnútri (natvrdo na bielo) */
    div[data-baseweb="input"] input, 
    div[data-baseweb="textarea"] textarea,
    input[class*="st-"], 
    textarea[class*="st-"] {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        caret-color: #ffffff !important;
        background-color: transparent !important;
    }
    
    /* 3. Fix pre Selectbox (roletku) */
    div[data-baseweb="select"] span {
        color: #ffffff !important;
    }
    
    /* Názvy nad bunkami ostanú čierne */
    label, label p { color: #000000 !important; font-weight: 600 !important; }
    
    /* Tlačidlo Generovať */
    .gen-btn > button { background-color: #000 !important; color: #fff !important; width: 100%; height: 3.5em; border-radius: 4px !important; font-weight: bold !important; border: none !important; }
    </style>
    """, unsafe_allow_html=True)

# --- TOP NAVIGATION BAR ---
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
    # HERO SECTION
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
    
    # ABOUT FOUNDER SECTION
    f1, f2 = st.columns([1, 2])
    with f1:
        if os.path.exists("profilovka.png"):
            st.image("profilovka.png", use_container_width=True)
        elif os.path.exists("profilovka.jpg"):
            st.image("profilovka.jpg", use_container_width=True)
        else:
            st.info("Nahrajte svoju fotku na GitHub s názvom 'profilovka.jpg'")
            
    with f2:
        st.markdown("<h2 style='margin-bottom: 20px;'>Automatizácia pre moderné účtovníctvo</h2>", unsafe_allow_html=True)
        st.write("""
        Našou víziou je posunúť účtovníctvo do 21. storočia. Chápeme, že pre účtovné kancelárie a podnikateľov je čas tou najcennejšou komoditou. 
        Preto sme vytvorili **AUTOCESTAK pro** – nástroj, ktorý plne automatizuje únavnú administratívu okolo cestovných náhrad, 
        eliminuje chybovosť pri výpočtoch a šetrí desiatky hodín vašej práce mesačne. 
        
        Sústreďte sa na to, čo je pre váš biznis skutočne dôležité. Rutinné papierovačky a výpočty nechajte na náš inteligentný algoritmus.
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
        col_x, col_y = st.columns(2)
        with col_x:
            meno = st.text_input("Meno zamestnanca", value="Sebastián Štuller")
            spz = st.text_input("ŠPZ vozidla", value="LV-000XX")
            mesiac_nazov = st.selectbox("Mesiac", ["Január", "Február", "Marec", "Apríl", "Máj", "Jún", "Júl", "August", "September", "Október", "November", "December"])
            start_miesta_input = st.text_area("Miesta štartu (oddelené čiarkou)", value="Mýtne Ludany, Levice")
            mesta_sk = st.text_area("Destinácie (oddelené čiarkou)", value="Bratislava, Nitra, Trenčín, Poprad, Žilina")
            
        with col_y:
            cielova_suma = st.number_input("Cieľová suma (€)", value=1500.0, step=50.0)
            
            spotreba = st.number_input("Spotreba (l/100km)", value=6.5, step=0.1)
            st.caption("ℹ️ *Údaj z technického preukazu (kombinovaná spotreba).*")
            
            cena_phm = st.number_input("Cena PHM (€/l)", value=1.62, step=0.01)
            st.markdown("<div style='margin-top: -10px; margin-bottom: 15px; font-size: 12px;'><a href='https://datacube.statistics.sk/#!/view/sk/VBD_INTERN/sp0202ms/v_sp0202ms_00_00_00_sk' target='_blank' style='color: #666; text-decoration: none;'>🔗 Zdroj: ŠÚ SR (Mesačné ceny PHM)</a></div>", unsafe_allow_html=True)
            
            amortizacia = st.number_input("Amortizácia (€/km)", value=0.265, format="%.3f")
            st.markdown("<div style='margin-top: -10px; margin-bottom: 15px; font-size: 12px;'><a href='https://www.slov-lex.sk/pravne-predpisy/SK/ZZ/2024/73/' target='_blank' style='color: #666; text-decoration: none;'>🔗 Zdroj: Zákonná sadzba MPSVR SR</a></div>", unsafe_allow_html=True)
            
            stravne_val = st.number_input("Stravné (€/deň)", value=8.30, step=0.10)
            st.markdown("<div style='margin-top: -10px; margin-bottom: 15px; font-size: 12px;'><a href='https://www.slov-lex.sk/pravne-predpisy/SK/ZZ/2024/211/' target='_blank' style='color: #666; text-decoration: none;'>🔗 Zdroj: Opatrenie o stravnom</a></div>", unsafe_allow_html=True)

        st.markdown('<div style="margin-top:20px;"></div>', unsafe_allow_html=True)
        st.markdown("""<style>.gen-btn > button { background-color: #000 !important; color: #fff !important; width: 100%; height: 3em; border-radius: 4px !important; font-weight: bold; border: none !important; }</style>""", unsafe_allow_html=True)
        st.markdown('<div class="gen-btn">', unsafe_allow_html=True)
        if st.button("🚀 Vygenerovať Excel"):
            with st.spinner('Pripravujem dáta a generujem Excel...'):
                start_mesta_list = [s.strip() for s in start_miesta_input.split(',')]
                mesta_list = [m.strip() for m in mesta_sk.split(',')]
                sadzba_km = amortizacia + ((spotreba / 100) * cena_phm)
                mesiace_dict = {"Január": 1, "Február": 2, "Marec": 3, "Apríl": 4, "Máj": 5, "Jún": 6, "Júl": 7, "August": 8, "September": 9, "Október": 10, "November": 11, "December": 12}
                mes_int = mesiace_dict[mesiac_nazov]
                rok = 2026
                
                sk_holidays = holidays.Slovakia(years=rok)
                dni = [datetime.date(rok, mes_int, d) for d in range(1, calendar.monthrange(rok, mes_int)[1] + 1) if datetime.date(rok, mes_int, d).weekday() < 5 and datetime.date(rok, mes_int, d) not in sk_holidays]
                random.shuffle(dni)
                
                cena_jednej_cesty = (270 * sadzba_km) + stravne_val
                pocet_ciest = max(1, min(len(dni), int(round(cielova_suma / cena_jednej_cesty))))
                celkove_km = int(round((cielova_suma - (pocet_ciest * stravne_val)) / sadzba_km))
                km_list = [celkove_km // pocet_ciest] * pocet_ciest
                for i in range(celkove_km % pocet_ciest): km_list[i] += 1
                
                vybrane_dni = sorted(dni[:pocet_ciest])

                wb = Workbook()
                ws = wb.active
                ws.title = f"{mesiac_nazov}_{rok}"
                for col, width in zip(['A','B','C','D','E','F','G','H','I','J'], [12,30,25,15,22,15,12,12,22,15]):
                    ws.column_dimensions[col].width = width

                ws['A1'] = f"VYÚČTOVANIE PRACOVNEJ CESTY - {meno}"
                ws['A1'].font = Font(bold=True)
                ws.append(["Dátum", "ODCHOD-PRÍCHOD", "Použitý dopravný prostriedok", "Vzdialenosť v km", "Začiatok a koniec výkonu", "Cestovné", "Stravné", "Nocľažné", "Nutné vedľajšie výdavky", "Spolu"])
                for cell in ws[2]: cell.font = Font(bold=True); cell.alignment = Alignment(wrap_text=True, horizontal="center", vertical="center")
                ws.append([""] * 10); ws.append([""] * 10)
                ws.append(["", "", "", "", "", "EUR", "EUR", "EUR", "EUR", "EUR"])
                for cell in ws[5]: cell.alignment = Alignment(horizontal="right")

                current_row = 6
                for idx, d in enumerate(vybrane_dni):
                    km = km_list[idx]
                    aktualny_start = random.choice(start_mesta_list)
                    mozne_destinacie = [m for m in mesta_list if m != aktualny_start]
                    if not mozne_destinacie: mozne_destinacie = mesta_list
                    aktualny_ciel = random.choice(mozne_destinacie)
                    
                    cestovne = km * sadzba_km
                    spolu = cestovne + stravne_val
                    
                    ws.append([d.strftime("%Y-%m-%d"), aktualny_start, f"AUV ({spz})", km, "8.00", cestovne, stravne_val, "", "", spolu])
                    ws.cell(row=current_row, column=6).number_format = '0.0000'; ws.cell(row=current_row, column=7).number_format = '0.00'; ws.cell(row=current_row, column=10).number_format = '0.0000'
                    ws.append(["", aktualny_ciel, "", "", "16:30:00", "", "", "", "", ""])
                    current_row += 2

                ws.append([""] * 10) 
                sum_row = current_row + 1
                ws.cell(row=sum_row, column=1, value="Spolu").font = Font(bold=True)
                ws.cell(row=sum_row, column=6, value=f"=SUM(F6:F{current_row-1})").number_format = '#,##0.00'
                ws.cell(row=sum_row, column=7, value=f"=SUM(G6:G{current_row-1})").number_format = '#,##0.00'
                ws.cell(row=sum_row, column=10, value=f"=SUM(J6:J{current_row-1})").number_format = '#,##0.00'
                for col in [6, 7, 10]: ws.cell(row=sum_row, column=col).font = Font(bold=True)

                output = io.BytesIO()
                wb.save(output)
                output.seek(0)
                
                st.success("✅ Hotovo!")
                st.download_button(label="📥 Stiahnuť Excel", data=output, file_name=f"Cestak_{meno.replace(' ', '_')}_{mesiac_nazov}_2026.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state["page"] == "Podpora":
    st.title("Podpora")
    st.write("V prípade problémov s generovaním alebo nastavením sadzieb nás neváhajte kontaktovať na čísle **+421 911 781 362**.")

elif st.session_state["page"] == "O nás":
    st.title("O projekte AUTOCESTAK pro")
    st.markdown("""
        Tento systém vyvinul **Sebastián Štuller** pre zefektívnenie procesov v spoločnosti **jmcreditplus s.r.o.**
    """)
