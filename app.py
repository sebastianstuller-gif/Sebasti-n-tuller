import streamlit as st
import random
import datetime
import calendar
import holidays
import io
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
        height: 3em;
    }
    .stButton>button:hover {
        background-color: #333333;
        color: white;
    }
    .price-box {
        padding: 30px;
        border-radius: 5px;
        border: 1px solid #e0e0e0;
        background-color: #ffffff;
        text-align: center;
    }
    h1, h2, h3 {
        font-weight: 600 !important;
        letter-spacing: -0.5px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN LOGIKA ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

def check_password():
    if st.session_state["authenticated"]:
        return True
    
    st.markdown("<h2 style='text-align: center; margin-top: 50px;'>Prístup do systému</h2>", unsafe_allow_html=True)
    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_b:
        password = st.text_input("Heslo", type="password")
        if st.button("Vstúpiť"):
            if password == "levice2026":
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Nesprávne prístupové údaje.")
    return False

# --- SIDEBAR (Minimalizmus) ---
with st.sidebar:
    st.image("logo.png", use_container_width=True)
    st.markdown("---")
    st.markdown("---")
    page = st.radio("Navigácia", ["Domov", "Generátor", "O systéme"])
    st.markdown("---")
    st.markdown("<div style='font-size: 12px; color: gray;'>Vytvoril:<br><b>Sebastián Štuller</b><br><br>Spracováva:<br><b>jmcreditplus s.r.o.</b></div>", unsafe_allow_html=True)
    
    if st.session_state["authenticated"]:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Odhlásiť"):
            st.session_state["authenticated"] = False
            st.rerun()

# --- OBSAH ---
if page == "Domov":
    st.title("AUTOCESTAK pro")
    st.subheader("Automatizované spracovanie cestovných náhrad.")
    st.markdown("Minimalizujte manuálnu prácu a maximalizujte efektivitu vášho účtovníctva.")
    
    st.markdown("<br><h3>Modely predplatného</h3>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="price-box"><h4>Standard</h4><p>Základné SK cesťáky</p><hr><h5>0 € / mes</h5></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="price-box" style="border: 2px solid #000;"><h4>Business</h4><p>SK + EU, Excel export</p><hr><h5>19 € / mes</h5></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="price-box"><h4>Enterprise</h4><p>Pre účtovné kancelárie</p><hr><h5>Dohodou</h5></div>', unsafe_allow_html=True)

elif page == "Generátor":
    if check_password():
        st.title("Generátor dokumentov")
        t1, t2 = st.tabs(["Slovensko", "Zahraničie"])
        
        with t1:
            col_x, col_y = st.columns(2)
            with col_x:
                meno = st.text_input("Meno zamestnanca", value="Sebastián Štuller")
                spz = st.text_input("ŠPZ vozidla", value="LV-000XX")
                mesiac_nazov = st.selectbox("Mesiac", ["Január", "Február", "Marec", "Apríl", "Máj", "Jún", "Júl", "August", "September", "Október", "November", "December"])
                start_miesto = st.text_input("Miesto štartu:", value="Mýtne Ludany")
            with col_y:
                cielova_suma = st.number_input("Cieľová suma (€)", value=1500.0, step=50.0)
                spotreba = st.number_input("Spotreba (l/100km)", value=6.5, step=0.1)
                cena_phm = st.number_input("Cena PHM (€/l)", value=1.62, step=0.01)
                amortizacia = st.number_input("Amortizácia (€/km)", value=0.265, format="%.3f")
                stravne_val = st.number_input("Stravné (€/deň):", value=8.30, step=0.10)
            
            mesta_sk = st.text_area("Zoznam destinácií (oddeľte čiarkou):", value="Bratislava, Nitra, Trenčín, Poprad, Žilina")

            if st.button("Generovať dokument"):
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
                    
                    # Rozdelenie KM
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

                    # Šírky stĺpcov
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
                        
                        # Riadok odchodu
                        ws.append([d.strftime("%Y-%m-%d"), start_miesto, dopravny_prostriedok, km, "8.00", cestovne, stravne_val, "", "", spolu])
                        ws.cell(row=current_row, column=6).number_format = '0.0000' 
                        ws.cell(row=current_row, column=7).number_format = '0.00'   
                        ws.cell(row=current_row, column=10).number_format = '0.0000' 
                        
                        # Riadok príchodu
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

                    # --- PRÍPRAVA NA STIAHNUTIE ---
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
            st.info("Sekcia Zahraničie sa pripravuje podľa podkladov od účtovníčky.")

elif page == "O systéme":
    st.title("O projekte")
    st.markdown(f"""
    Systém **AUTOCESTAK pro** bol navrhnutý pre potreby moderných finančných procesov. 
    Kombinuje presnosť účtovných štandardov s rýchlosťou automatizačných algoritmov, 
    čím pomáha firmám dramaticky znižovať byrokratickú záťaž.
    
    <br><br>
    <b>Spracovateľská spoločnosť:</b> jmcreditplus s.r.o. <br>
    <b>Zodpovedný architekt:</b> Sebastián Štuller
    """, unsafe_allow_html=True)
