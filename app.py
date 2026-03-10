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
    if os.path.exists("logo.png.png"):
        st.image("logo.png.png", use_container_width=True)
    elif os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    else:
        st.markdown("<h1 style='font-size: 24px; text-align: center;'>AUTOCESTAK<br><span style='font-weight: 300;'>pro</span></h1>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    page = st.radio("Navigácia", ["Domov", "Generátor", "O systéme"])
    st.markdown("---")
    st.markdown("""
        <div style='font-size: 12px; color: gray; line-height: 1.6;'>
            Founder: <b>Sebastián Štuller</b><br>
            Spracovateľ: <b>jmcreditplus s.r.o.</b><br>
            Verzia: 1.0.3 Pro
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
            """, unsafe_allow_html=True)
            if st.button("Aktivovať ročne", key="btn_yr"):
                st.info("Platobná brána sa pripravuje.")

elif page == "Generátor":
    if check_password():
        st.title("Generátor dokumentov")
        
        # TOTO JE TEN RIADOK, KTORÝ CHÝBAL (t1, t2 = st.tabs)
        t1, t2 = st.tabs(["Slovensko", "Zahraničie"])
        
        with t1:
            col_x, col_y = st.columns(2)
            with col_x:
                meno = st.text_input("Meno zamestnanca", value="Sebastián Štuller")
                spz = st.text_input("ŠPZ vozidla", value="LV-000XX")
                mesiac_nazov = st.selectbox("Mesiac", ["Január", "Február", "Marec", "Apríl", "Máj", "Jún", "Júl", "August", "September", "Október", "November", "December"])
                start_miesto = st.text_input("Miesto štartu", value="Mýtne Ludany")
                mesta_sk = st.text_area("Destinácie (oddelené čiarkou)", value="Bratislava, Nitra, Trenčín, Poprad, Žilina")
                
            with col_y:
                cielova_suma = st.number_input("Cieľová suma (€)", value=1500.0, step=50.0)
                
                spotreba = st.number_input("Spotreba (l/100km)", value=6.5, step=0.1)
                st.caption("ℹ️ *Údaj z technického preukazu (kombinovaná spotreba).*")
                
                cena_phm = st.number_input("Cena PHM (€/l)", value=1.62, step=0.01)
                st.markdown("<div style='margin-top: -10px; margin-bottom: 15px; font-size: 12px;'><a href='https://datacube.statistics.sk/' target='_blank' style='color: #666; text-decoration: none;'>🔗 Zdroj: Štatistický úrad SR</a></div>", unsafe_allow_html=True)
                
                amortizacia = st.number_input("Amortizácia (€/km)", value=0.265, format="%.3f")
                st.markdown("<div style='margin-top: -10px; margin-bottom: 15px; font-size: 12px;'><a href='https://www.slov-lex.sk/pravne-predpisy/SK/ZZ/2024/73/' target='_blank' style='color: #666; text-decoration: none;'>🔗 Zdroj: Zákonná sadzba MPSVR SR</a></div>", unsafe_allow_html=True)
                
                stravne_val = st.number_input("Stravné (€/deň)", value=8.30, step=0.10)
                st.markdown("<div style='margin-top: -10px; margin-bottom: 15px; font-size: 12px;'><a href='https://www.slov-lex.sk/pravne-predpisy/SK/ZZ/2024/211/' target='_blank' style='color: #666; text-decoration: none;'>🔗 Zdroj: Opatrenie o stravnom</a></div>", unsafe_allow_html=True)

            if st.button("Vygenerovať Excel dokument"):
                with st.spinner('Pripravujem dáta a generujem Excel...'):
                    # --- VÝPOČTOVÁ LOGIKA ---
                    sadzba_km = amortizacia + ((spotreba / 100) * cena_phm)
                    mesiace_dict = {"Január": 1, "Február": 2, "Marec": 3, "Apríl": 4, "Máj": 5, "Jún": 6, "Júl": 7, "August": 8, "September": 9, "Október": 10, "November": 11, "December": 12}
                    mes_int = mesiace_dict[mesiac_nazov]
                    rok = 2026
                    
                    sk_holidays = holidays.Slovakia(years=rok)
                    dni = [datetime.date(rok, mes_int, d) for d in range(1, calendar.monthrange(rok, mes_int)[1] + 1) 
                           if datetime.date(rok, mes_int, d).weekday() < 5 and datetime.date(rok, mes_int, d) not in sk_holidays]
                    
                    random.shuffle(dni)
                    
                    cena_jednej_cesty = (270 * sadzba_km) + stravne_val
                    pocet_ciest = max(1, min(len(dni), int(round(cielova_suma / cena_jednej_cesty))))
                    celkove_km = int(round((cielova_suma - (pocet_ciest * stravne_val)) / sadzba_km))
                    
                    km_list = [celkove_km // pocet_ciest] * pocet_ciest
                    for i in range(celkove_km % pocet_ciest): km_list[i] += 1
                    
                    # Jemné rozhádzanie KM pre rôznorodosť
                    for _ in range(pocet_ciest * 2):
                        i, j = random.randint(0, pocet_ciest - 1), random.randint(0, pocet_ciest - 1)
                        if i != j:
                            shift = random.randint(1, 20)
                            if km_list[i] - shift > 50:
                                km_list[i] -= shift
                                km_list[j] += shift

                    vybrane_dni = sorted(dni[:pocet_ciest])
                    mesta_list = [m.strip() for m in mesta_sk.split(',')]

                    # --- EXCEL GENERÁCIA ---
                    wb = Workbook()
                    ws = wb.active
                    ws.title = f"{mesiac_nazov}_{rok}"

                    ws.column_dimensions['A'].width = 12  
                    ws.column_dimensions['B'].width = 30  
                    ws.column_dimensions['C'].width = 25  
                    ws.column_dimensions['D'].width = 15  
                    ws.column_dimensions['E'].width = 22  
                    ws.column_dimensions['F'].width = 15  
                    ws.column_dimensions['G'].width = 12  
                    ws.column_dimensions['H'].width = 12  
                    ws.column_dimensions['I'].width = 22  
                    ws.column_dimensions['J'].width = 15  

                    ws['A1'] = f"VYÚČTOVANIE PRACOVNEJ CESTY - {meno}"
                    ws['A1'].font = Font(bold=True)
                    
                    hlavicka = ["Dátum", "ODCHOD-PRÍCHOD", "Použitý dopravný prostriedok", "Vzdialenosť v km", 
                                "Začiatok a koniec výkonu", "Cestovné", "Stravné", "Nocľažné", "Nutné vedľajšie výdavky", "Spolu"]
                    ws.append(hlavicka)
                    
                    for cell in ws[2]:
                        cell.font = Font(bold=True)
                        cell.alignment = Alignment(wrap_text=True, horizontal="center", vertical="center")

                    ws.append([""] * 10)
                    ws.append([""] * 10)
                    ws.append(["", "", "", "", "", "EUR", "EUR", "EUR", "EUR", "EUR"])
                    for cell in ws[5]: cell.alignment = Alignment(horizontal="right")

                    current_row = 6
                    dostupne_mesta = mesta_list.copy()
                    random.shuffle(dostupne_mesta)
                    
                    for idx, d in enumerate(vybrane_dni):
                        km = km_list[idx]
                        mesto = dostupne_mesta[idx % len(dostupne_mesta)]
                        cestovne = km * sadzba_km
                        spolu = cestovne + stravne_val
                        dopravny_prostriedok = f"AUV ({spz})"
                        
                        ws.append([d.strftime("%Y-%m-%d"), start_miesto, dopravny_prostriedok, km, "8.00", cestovne, stravne_val, "", "", spolu])
                        ws.cell(row=current_row, column=6).number_format = '0.0000' 
                        ws.cell(row=current_row, column=7).number_format = '0.00'   
                        ws.cell(row=current_row, column=10).number_format = '0.0000' 
                        
                        ws.append(["", mesto, "", "", "16:30:00", "", "", "", "", ""])
                        current_row += 2

                    ws.append([""] * 10) 
                    sum_row = current_row + 1
                    ws.cell(row=sum_row, column=1, value="Spolu")
                    ws.cell(row=sum_row, column=1).font = Font(bold=True)
                    
                    ws.cell(row=sum_row, column=6, value=f"=SUM(F6:F{current_row-1})").number_format = '#,##0.00'
                    ws.cell(row=sum_row, column=7, value=f"=SUM(G6:G{current_row-1})").number_format = '#,##0.00'
                    ws.cell(row=sum_row, column=10, value=f"=SUM(J6:J{current_row-1})").number_format = '#,##0.00'
                    
                    for col in [6, 7, 10]:
                        ws.cell(row=sum_row, column=col).font = Font(bold=True)

                    output = io.BytesIO()
                    wb.save(output)
                    output.seek(0)
                    
                    st.success("✅ Dokument bol úspešne vygenerovaný!")
                    st.download_button(
                        label="Stiahnuť Excel dokument",
                        data=output,
                        file_name=f"Cestak_{meno.replace(' ', '_')}_{mesiac_nazov}_2026.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

        with t2:
            st.info("Zahraničné cesťáky: Funkcia bude sprístupnená po implementácii aktuálnych sadzieb ECB.")

elif page == "O systéme":
    st.title("O projekte")
    st.markdown("""
        Systém **AUTOCESTAK pro** vyvinul **Sebastián Štuller** pre zefektívnenie procesov v spoločnosti **jmcreditplus s.r.o.**
        
        Naším cieľom je digitalizácia tradičného účtovníctva a odstránenie chybovosti pri ručnom spracovávaní dát. 
        Tento nástroj využíva moderné štatistické metódy na rovnomerné rozdelenie nákladov pri dodržaní všetkých legislatívnych noriem SR.
        
        <br><br>
        © 2026 jmcreditplus s.r.o.
    """, unsafe_allow_html=True)
