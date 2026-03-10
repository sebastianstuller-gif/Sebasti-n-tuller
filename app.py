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

# --- JAZYKOVÝ SLOVNÍK (SK / EN) ---
if "lang" not in st.session_state:
    st.session_state["lang"] = "SK"

translations = {
    "SK": {
        "nav_home": "Domov", "nav_gen": "Generátor", "nav_about": "O systéme",
        "login_title": "Prístup k systému", "login_pass": "Prístupové heslo", "login_btn": "Vstúpiť do generátora", "login_err": "Nesprávne prístupové údaje.",
        "logout_btn": "Odhlásiť",
        "home_title": "Profesionálna automatizácia cestovných príkazov.", "home_sub": "Šetrite hodiny ručnej práce mesačne s naším inteligentným algoritmom.",
        "plan_title": "Vyberte si váš plán", "plan_mo": "Mesačne", "plan_mo_sub": "Ideálne pre jednotlivcov", "plan_yr": "Ročne", "plan_yr_sub": "Najlepšia hodnota", "btn_buy": "Aktivovať",
        "gen_title": "Generátor dokumentov", "tab_sk": "Slovensko", "tab_eu": "Zahraničie",
        "f_name": "Meno zamestnanca", "f_spz": "ŠPZ vozidla", "f_month": "Mesiac", "f_start": "Miesta štartu (oddelené čiarkou)",
        "f_dest": "Destinácie (oddelené čiarkou)", "f_target": "Cieľová suma (€)", "f_cons": "Spotreba (l/100km)", "f_phm": "Cena PHM (€/l)", 
        "f_amort": "Amortizácia (€/km)", "f_diet": "Stravné (€/deň)",
        "btn_gen": "Vygenerovať Excel dokument", "btn_dl": "Stiahnuť Excel dokument",
        "msg_prep": "Pripravujem dáta a generujem Excel...", "msg_done": "✅ Dokument bol úspešne vygenerovaný!",
        "eu_info": "Zahraničné cesťáky: Funkcia bude sprístupnená po implementácii aktuálnych sadzieb ECB.",
        "about_text": "Systém **AUTOCESTAK pro** vyvinul **Sebastián Štuller** pre zefektívnenie procesov v spoločnosti **jmcreditplus s.r.o.**<br><br>Naším cieľom je digitalizácia tradičného účtovníctva a odstránenie chybovosti pri ručnom spracovávaní dát."
    },
    "EN": {
        "nav_home": "Home", "nav_gen": "Generator", "nav_about": "About Us",
        "login_title": "System Access", "login_pass": "Access Password", "login_btn": "Enter Generator", "login_err": "Invalid credentials.",
        "logout_btn": "Log out",
        "home_title": "Professional Travel Expense Automation.", "home_sub": "Save hours of manual work every month with our smart algorithm.",
        "plan_title": "Choose your plan", "plan_mo": "Monthly", "plan_mo_sub": "Ideal for individuals", "plan_yr": "Yearly", "plan_yr_sub": "Best value", "btn_buy": "Activate",
        "gen_title": "Document Generator", "tab_sk": "Slovakia", "tab_eu": "Abroad",
        "f_name": "Employee Name", "f_spz": "Vehicle Plate (ŠPZ)", "f_month": "Month", "f_start": "Starting Locations (comma separated)",
        "f_dest": "Destinations (comma separated)", "f_target": "Target Amount (€)", "f_cons": "Fuel Consumption (l/100km)", "f_phm": "Fuel Price (€/l)", 
        "f_amort": "Amortization (€/km)", "f_diet": "Daily Allowance (€/day)",
        "btn_gen": "Generate Excel Document", "btn_dl": "Download Excel Document",
        "msg_prep": "Preparing data and generating Excel...", "msg_done": "✅ Document generated successfully!",
        "eu_info": "Foreign travel expenses: Feature will be unlocked after ECB rates implementation.",
        "about_text": "**AUTOCESTAK pro** was developed by **Sebastián Štuller** to streamline operations at **jmcreditplus s.r.o.**<br><br>Our goal is to digitize traditional accounting and eliminate manual data entry errors."
    }
}

# Skratka pre preklady
t = translations[st.session_state["lang"]]

# --- VÝBER JAZYKA (Vpravo hore) ---
col_space, col_lang = st.columns([9, 1])
with col_lang:
    selected_lang = st.selectbox("🌐", ["SK", "EN"], index=0 if st.session_state["lang"] == "SK" else 1, label_visibility="collapsed")
    if selected_lang != st.session_state["lang"]:
        st.session_state["lang"] = selected_lang
        st.rerun()

# --- HIGH-CONTRAST STYLING (Biely web, čierne polia) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    
    html, body, [class*="css"], .stApp {
        font-family: 'Inter', sans-serif;
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    
    /* Čierne kolónky (Input fields) s bielym textom */
    div[data-baseweb="input"] > div, 
    div[data-baseweb="select"] > div, 
    div[data-baseweb="textarea"] > div,
    input, textarea, select {
        background-color: #000000 !important;
        color: #ffffff !important;
        border-radius: 4px;
        border: 1px solid #333333 !important;
    }
    
    /* Farba textu (Label) nad kolónkami */
    label { color: #000000 !important; font-weight: 600 !important; }
    
    /* Hlavné čierne tlačidlo */
    .stButton>button {
        background-color: #000000 !important;
        color: white !important;
        border-radius: 2px !important;
        border: none !important;
        letter-spacing: 1px;
        text-transform: uppercase;
        font-weight: 600;
        height: 3.5em;
        width: 100%;
        transition: 0.3s;
    }
    .stButton>button:hover { background-color: #333333 !important; }
    
    /* Cenové boxy */
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
    
    /* Sidebar prefarbenie */
    [data-testid="stSidebar"] { background-color: #fafafa !important; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN LOGIKA ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

def check_password():
    if st.session_state["authenticated"]: return True
    
    st.markdown(f"<h2 style='text-align: center; margin-top: 50px;'>{t['login_title']}</h2>", unsafe_allow_html=True)
    col_a, col_b, col_c = st.columns([1, 1.5, 1])
    with col_b:
        password = st.text_input(t['login_pass'], type="password")
        if st.button(t['login_btn']):
            if password == "levice2026":
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error(t['login_err'])
    return False

# --- SIDEBAR ---
with st.sidebar:
    if os.path.exists("logo.png.png"): st.image("logo.png.png", use_container_width=True)
    elif os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
    else: st.markdown("<h1 style='font-size: 24px; text-align: center;'>AUTOCESTAK<br><span style='font-weight: 300;'>pro</span></h1>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    page = st.radio("Menu", [t["nav_home"], t["nav_gen"], t["nav_about"]], label_visibility="collapsed")
    st.markdown("---")
    st.markdown("""
        <div style='font-size: 12px; color: gray; line-height: 1.6;'>
            Founder: <b>Sebastián Štuller</b><br>
            Powered by: <b>jmcreditplus s.r.o.</b><br>
            Version: 1.1 Pro (Bilingual)
        </div>
    """, unsafe_allow_html=True)
    
    if st.session_state["authenticated"]:
        if st.button(t["logout_btn"]):
            st.session_state["authenticated"] = False
            st.rerun()

# --- OBSAH ---
if page == t["nav_home"]:
    st.title("AUTOCESTAK pro")
    st.subheader(t["home_title"])
    st.markdown(t["home_sub"])
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col_left, col_mid, col_right = st.columns([1, 2, 1])
    with col_mid:
        st.markdown(f"<h3 style='text-align: center;'>{t['plan_title']}</h3><br>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f'<div class="price-box"><h4>{t["plan_mo"]}</h4><p>{t["plan_mo_sub"]}</p><h2>9,99 €</h2></div>', unsafe_allow_html=True)
            if st.button(f"{t['btn_buy']} 9,99€", key="btn_mo"): st.info("Payment gateway in progress.")
        with c2:
            st.markdown(f'<div class="price-box" style="border: 2px solid #000;"><h4>{t["plan_yr"]}</h4><p>{t["plan_yr_sub"]}</p><h2>100 €</h2></div>', unsafe_allow_html=True)
            if st.button(f"{t['btn_buy']} 100€", key="btn_yr"): st.info("Payment gateway in progress.")

elif page == t["nav_gen"]:
    if check_password():
        st.title(t["gen_title"])
        t1, t2 = st.tabs([t["tab_sk"], t["tab_eu"]])
        
        with t1:
            col_x, col_y = st.columns(2)
            with col_x:
                meno = st.text_input(t["f_name"], value="Sebastián Štuller")
                spz = st.text_input(t["f_spz"], value="LV-000XX")
                # Mesiace nechávame zatiaľ slovenské, lebo sa viažu na slovenský kalendár sviatkov
                mesiac_nazov = st.selectbox(t["f_month"], ["Január", "Február", "Marec", "Apríl", "Máj", "Jún", "Júl", "August", "September", "Október", "November", "December"])
                start_miesta_input = st.text_area(t["f_start"], value="Mýtne Ludany, Levice")
                mesta_sk = st.text_area(t["f_dest"], value="Bratislava, Nitra, Trenčín, Poprad, Žilina")
                
            with col_y:
                cielova_suma = st.number_input(t["f_target"], value=1500.0, step=50.0)
                spotreba = st.number_input(t["f_cons"], value=6.5, step=0.1)
                cena_phm = st.number_input(t["f_phm"], value=1.62, step=0.01)
                st.markdown("<div style='margin-top: -10px; margin-bottom: 15px; font-size: 12px;'><a href='https://datacube.statistics.sk/#!/view/sk/VBD_INTERN/sp0202ms/v_sp0202ms_00_00_00_sk' target='_blank' style='color: #666; text-decoration: none;'>🔗 Zdroj: ŠÚ SR / Source: Stat. Office</a></div>", unsafe_allow_html=True)
                amortizacia = st.number_input(t["f_amort"], value=0.265, format="%.3f")
                st.markdown("<div style='margin-top: -10px; margin-bottom: 15px; font-size: 12px;'><a href='https://www.slov-lex.sk/pravne-predpisy/SK/ZZ/2024/73/' target='_blank' style='color: #666; text-decoration: none;'>🔗 Zdroj: MPSVR SR</a></div>", unsafe_allow_html=True)
                stravne_val = st.number_input(t["f_diet"], value=8.30, step=0.10)
                st.markdown("<div style='margin-top: -10px; margin-bottom: 15px; font-size: 12px;'><a href='https://www.slov-lex.sk/pravne-predpisy/SK/ZZ/2024/211/' target='_blank' style='color: #666; text-decoration: none;'>🔗 Zdroj: Slov-lex</a></div>", unsafe_allow_html=True)

            if st.button(t["btn_gen"]):
                with st.spinner(t["msg_prep"]):
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
                    for _ in range(pocet_ciest * 2):
                        i, j = random.randint(0, pocet_ciest - 1), random.randint(0, pocet_ciest - 1)
                        if i != j:
                            shift = random.randint(1, 20)
                            if km_list[i] - shift > 50:
                                km_list[i] -= shift
                                km_list[j] += shift
                    vybrane_dni = sorted(dni[:pocet_ciest])

                    wb = Workbook()
                    ws = wb.active
                    ws.title = f"{mesiac_nazov}_{rok}"
                    for col, width in zip(['A','B','C','D','E','F','G','H','I','J'], [12,30,25,15,22,15,12,12,22,15]):
                        ws.column_dimensions[col].width = width

                    # EXCEL ZOSTAJE V SLOVENČINE KVÔLI ÚČTOVNÍCTVU!
                    ws['A1'] = f"VYÚČTOVANIE PRACOVNEJ CESTY - {meno}"
                    ws['A1'].font = Font(bold=True)
                    hlavicka = ["Dátum", "ODCHOD-PRÍCHOD", "Použitý dopravný prostriedok", "Vzdialenosť v km", "Začiatok a koniec výkonu", "Cestovné", "Stravné", "Nocľažné", "Nutné vedľajšie výdavky", "Spolu"]
                    ws.append(hlavicka)
                    for cell in ws[2]: cell.font = Font(bold=True); cell.alignment = Alignment(wrap_text=True, horizontal="center", vertical="center")
                    ws.append([""] * 10)
                    ws.append([""] * 10)
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
                    ws.cell(row=sum_row, column=1, value="Spolu")
                    ws.cell(row=sum_row, column=1).font = Font(bold=True)
                    ws.cell(row=sum_row, column=6, value=f"=SUM(F6:F{current_row-1})").number_format = '#,##0.00'
                    ws.cell(row=sum_row, column=7, value=f"=SUM(G6:G{current_row-1})").number_format = '#,##0.00'
                    ws.cell(row=sum_row, column=10, value=f"=SUM(J6:J{current_row-1})").number_format = '#,##0.00'
                    for col in [6, 7, 10]: ws.cell(row=sum_row, column=col).font = Font(bold=True)

                    output = io.BytesIO()
                    wb.save(output)
                    output.seek(0)
                    
                    st.success(t["msg_done"])
                    st.download_button(label=t["btn_dl"], data=output, file_name=f"Cestak_{meno.replace(' ', '_')}_{mesiac_nazov}_2026.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        with t2:
            st.info(t["eu_info"])

elif page == t["nav_about"]:
    st.title(t["nav_about"])
    st.markdown(t["about_text"], unsafe_allow_html=True)
    st.markdown("<br>© 2026 jmcreditplus s.r.o.", unsafe_allow_html=True)
