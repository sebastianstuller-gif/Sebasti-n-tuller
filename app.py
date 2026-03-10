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
if "page" not in st.session_state: st.session_state["page"] = "Úvod"
if "authenticated" not in st.session_state: st.session_state["authenticated"] = False
if "show_login" not in st.session_state: st.session_state["show_login"] = False

translations = {
    "SK": {
        "nav_home": "Úvod", "nav_cestaky": "Cesťáky", "nav_support": "Podpora", "nav_about": "O nás",
        "login_btn": "Prihlásenie", "logout_btn": "Odhlásiť",
        "hero_title": "Napreduj s automatizovaním cesťákov s nami",
        "hero_sub": "Sme tu, aby sme pomohli a zefektívnili vašu prácu.",
        "contact_small": "Zavolajte nám a my vám pomôžeme",
        "plan_mo": "Mesačné predplatné", "plan_yr": "Ročné predplatné", "btn_buy": "Kúpiť",
        "login_title": "Prístup do generátora", "login_pass": "Heslo", "login_submit": "Vstúpiť",
        "gen_title": "Generátor cesťákov"
    },
    "EN": {
        "nav_home": "Home", "nav_cestaky": "App", "nav_support": "Support", "nav_about": "About",
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

# --- POKROČILÝ CSS STYLING (Skrytie sidebaru, top navbar, boxy) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"], .stApp { font-family: 'Inter', sans-serif; background-color: #ffffff !important; color: #000000 !important; }
    
    /* Úplné skrytie predvoleného bočného panela */
    [data-testid="collapsedControl"] { display: none !important; }
    [data-testid="stSidebar"] { display: none !important; }
    
    /* Navigačné tlačidlá (ako text) */
    .nav-btn > button { background-color: transparent !important; color: #000000 !important; font-weight: 600 !important; border: none !important; box-shadow: none !important; transition: 0.2s; }
    .nav-btn > button:hover { color: #ff4b4b !important; }
    
    /* Tlačidlo Prihlásenie */
    .login-btn > button { background-color: #f0f0f0 !important; color: #000 !important; border-radius: 20px !important; font-weight: 600; border: none !important; padding: 0 20px !important; }
    
    /* Tmavé cenníkové boxy */
    .black-box { background-color: #111111; color: #ffffff; padding: 40px; border-radius: 12px; text-align: center; }
    .black-box h4 { color: #aaaaaa; font-weight: 400; margin-bottom: 10px; }
    .black-box h2 { color: #ffffff; font-size: 38px; margin: 10px 0 30px 0; font-weight: 800; }
    
    /* Biele tlačidlo Kúpiť */
    .buy-btn > button { background-color: #ffffff !important; color: #000000 !important; border-radius: 6px !important; font-weight: 600 !important; border: none !important; width: 100%; height: 3em; text-transform: uppercase; letter-spacing: 1px; }
    .buy-btn > button:hover { background-color: #dddddd !important; }
    
    /* Kontaktný box (z fotky) */
    .contact-box { background-color: #f8f9fa; border: 1px solid #eeeeee; padding: 30px; border-radius: 16px; margin-top: 40px; display: inline-block; min-width: 350px; }
    .contact-box .small-text { color: #888888; font-size: 13px; font-weight: 600; text-transform: uppercase; margin-bottom: 15px; letter-spacing: 0.5px; }
    .contact-box h3 { font-size: 24px; font-weight: 800; margin: 0 0 5px 0; }
    .contact-box .email { color: #555555; font-size: 15px; margin: 0; }
    
    /* Typografia Úvodnej strany */
    .hero-title { font-size: 54px; font-weight: 800; line-height: 1.1; margin-top: 60px; margin-bottom: 20px; letter-spacing: -1.5px; }
    .hero-subtitle { font-size: 20px; color: #555555; font-weight: 400; max-width: 600px; margin-bottom: 40px; }
    
    /* Inputy v generátore */
    input, textarea, select, div[data-baseweb="select"] > div { background-color: #f5f5f5 !important; color: #000 !important; border: 1px solid #ddd !important; border-radius: 6px; }
    </style>
    """, unsafe_allow_html=True)

# --- TOP NAVIGATION BAR ---
col_logo, col_nav1, col_nav2, col_nav3, col_space, col_lang, col_login = st.columns([2, 1, 1, 1, 3, 1, 1.5])

with col_logo:
    if os.path.exists("logo.png.png"): st.image("logo.png.png", width=150)
    elif os.path.exists("logo.png"): st.image("logo.png", width=150)
    else: st.markdown("<h3 style='margin:0; padding:0;'>AUTOCESTAK pro</h3>", unsafe_allow_html=True)

with col_nav1:
    st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
    if st.button(t["nav_home"]): st.session_state["page"] = "Úvod"; st.session_state["show_login"] = False
    st.markdown('</div>', unsafe_allow_html=True)

with col_nav2:
    st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
    if st.button(t["nav_cestaky"]): st.session_state["page"] = "Cesťáky"; st.session_state["show_login"] = False
    st.markdown('</div>', unsafe_allow_html=True)

with col_nav3:
    st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
    if st.button(t["nav_about"]): st.session_state["page"] = "O nás"; st.session_state["show_login"] = False
    st.markdown('</div>', unsafe_allow_html=True)

with col_lang:
    selected_lang = st.selectbox("🌐", ["SK", "EN"], index=0 if st.session_state["lang"] == "SK" else 1, label_visibility="collapsed")
    if selected_lang != st.session_state["lang"]:
        st.session_state["lang"] = selected_lang
        st.rerun()

with col_login:
    st.markdown('<div class="login-btn">', unsafe_allow_html=True)
    if not st.session_state["authenticated"]:
        if st.button(t["login_btn"]): 
            st.session_state["show_login"] = not st.session_state["show_login"]
            st.rerun()
    else:
        if st.button(t["logout_btn"]): 
            st.session_state["authenticated"] = False
            st.session_state["page"] = "Úvod"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# --- LOGIN FORM (Zobrazí sa len ak sa klikne na Prihlásenie) ---
if st.session_state["show_login"] and not st.session_state["authenticated"]:
    st.markdown(f"<h3 style='text-align: center;'>{t['login_title']}</h3>", unsafe_allow_html=True)
    l1, l2, l3 = st.columns([1, 1, 1])
    with l2:
        pwd = st.text_input(t["login_pass"], type="password")
        st.markdown('<div class="buy-btn">', unsafe_allow_html=True)
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

if st.session_state["page"] == "Úvod":
    c1, c2 = st.columns([1.5, 1])
    with c1:
        st.markdown(f"<div class='hero-title'>{t['hero_title']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='hero-subtitle'>{t['hero_sub']}</div>", unsafe_allow_html=True)
        
        # Kontaktný box podľa fotky
        st.markdown(f"""
            <div class='contact-box'>
                <div class='small-text'>{t['contact_small']}</div>
                <h3>📞 +421 911 781 362</h3>
                <p class='email'>✉️ sebastian.stuller@jmcredit.sk</p>
            </div>
        """, unsafe_allow_html=True)

elif st.session_state["page"] == "Cesťáky":
    if not st.session_state["authenticated"]:
        # CENNÍK (Čierne boxy)
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
        # GENERÁTOR (Viditeľný len po prihlásení)
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
            cena_phm = st.number_input("Cena PHM (€/l)", value=1.62, step=0.01)
            amortizacia = st.number_input("Amortizácia (€/km)", value=0.265, format="%.3f")
            stravne_val = st.number_input("Stravné (€/deň)", value=8.30, step=0.10)

        st.markdown('<div style="margin-top:20px;"></div>', unsafe_allow_html=True)
        st.markdown('<div class="login-btn">', unsafe_allow_html=True) # Pre tmavé tlačidlo generovania
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

elif st.session_state["page"] == "O nás":
    st.title("O projekte AUTOCESTAK pro")
    st.markdown("""
        Tento systém vyvinul **Sebastián Štuller** pre zefektívnenie procesov v spoločnosti **jmcreditplus s.r.o.**
        
        Naším cieľom je digitalizácia tradičného účtovníctva a odstránenie chybovosti pri ručnom spracovávaní dát.
    """)
