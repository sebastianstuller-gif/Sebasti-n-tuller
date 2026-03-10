import streamlit as st
import random
import datetime
import calendar
import holidays
import io
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment

# --- NASTAVENIE STRÁNKY ---
st.set_page_config(page_title="AutoCesták PRO", page_icon="🚗", layout="centered")

st.title("🚗 AutoCesták PRO 2026")
st.markdown("Automatický generátor cestovných príkazov do Excelu (Presne podľa šablóny).")

# --- ZÁLOŽKY ---
tab_sk, tab_zahranicie = st.tabs(["🇸🇰 Slovenské cesťáky", "🌍 Zahraničné cesťáky"])

# ==========================================
# ZÁLOŽKA 1: SLOVENSKO
# ==========================================
with tab_sk:
    st.header("Parametre pre Slovensko")
    
    col1, col2 = st.columns(2)
    with col1:
        meno = st.text_input("Meno a Priezvisko:", value="Jozef Mrkvička")
        spz = st.text_input("ŠPZ Vozidla:", value="LV-123XY")
        mesiac_nazov = st.selectbox("Mesiac:", ["Január", "Február", "Marec", "Apríl", "Máj", "Jún", "Júl", "August", "September", "Október", "November", "December"])
        start_miesto = st.text_input("Miesto štartu:", value="Mýtne Ludany")
        
    with col2:
        cielova_suma = st.number_input("Cieľová suma mesačne (€):", min_value=100.0, max_value=5000.0, value=1500.0, step=50.0)
        spotreba = st.number_input("Spotreba (l/100km):", min_value=1.0, max_value=20.0, value=6.5, step=0.1)
        cena_phm = st.number_input("Cena PHM (€/l):", min_value=0.50, max_value=3.00, value=1.62, step=0.01)
        amortizacia = st.number_input("Amortizácia (€/km):", value=0.265, format="%.3f")
        stravne = st.number_input("Slovenské stravné (€/deň):", value=8.30, step=0.10)

    st.markdown("---")
    mesta_sk = st.text_area("Zoznam destinácií (oddeľte čiarkou):", value="Bratislava, Nitra, Trenčín, Poprad, Žilina, Mochovce")
    
    # Preklad mesiaca na číslo
    mesiace_dict = {"Január": 1, "Február": 2, "Marec": 3, "Apríl": 4, "Máj": 5, "Jún": 6, 
                    "Júl": 7, "August": 8, "September": 9, "Október": 10, "November": 11, "December": 12}
    mesiac_int = mesiace_dict[mesiac_nazov]
    rok = 2026

    # --- TLAČIDLO NA GENEROVANIE ---
    if st.button("🚀 Vygenerovať SK cesťák", type="primary"):
        with st.spinner('Počítam kilometre a generujem Excel...'):
            
            # 1. MATEMATIKA A SADZBY
            sadzba_km = amortizacia + ((spotreba / 100) * cena_phm)
            mesta_list = [m.strip() for m in mesta_sk.split(',')]
            priemer_km = 270 # Odhad na výpočet počtu ciest
            
            sk_holidays = holidays.Slovakia(years=rok)
            
            # Získanie pracovných dní
            pracovne_dni = []
            num_days = calendar.monthrange(rok, mesiac_int)[1]
            for day in range(1, num_days + 1):
                d = datetime.date(rok, mesiac_int, day)
                if d.weekday() < 5 and d not in sk_holidays:
                    pracovne_dni.append(d)
            
            random.shuffle(pracovne_dni)
            
            # 2. ROZDELENIE KILOMETROV A DNÍ
            cena_jednej_cesty = (priemer_km * sadzba_km) + stravne
            pocet_ciest = max(1, min(len(pracovne_dni), int(round(cielova_suma / cena_jednej_cesty))))
            
            celkove_km = int(round((cielova_suma - (pocet_ciest * stravne)) / sadzba_km))
            trips_km = [celkove_km // pocet_ciest] * pocet_ciest
            for i in range(celkove_km % pocet_ciest): trips_km[i] += 1
                
            for _ in range(pocet_ciest * 2):
                i, j = random.randint(0, pocet_ciest - 1), random.randint(0, pocet_ciest - 1)
                if i != j:
                    shift = random.randint(1, 20)
                    if trips_km[i] - shift > 50:
                        trips_km[i] -= shift
                        trips_km[j] += shift

            vybrane_dni = sorted(pracovne_dni[:pocet_ciest])
            
            # 3. TVORBA EXCELU (Originálna šablóna)
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
            
            for idx, datum in enumerate(vybrane_dni):
                km = trips_km[idx]
                mesto = dostupne_mesta[idx % len(dostupne_mesta)]
                cestovne = km * sadzba_km
                spolu = cestovne + stravne
                
                # Zápis do Excelu s ŠPZ vozidla
                dopravny_prostriedok = f"AUV ({spz})"
                ws.append([datum.strftime("%Y-%m-%d"), start_miesto, dopravny_prostriedok, km, "8.00", cestovne, stravne, "", "", spolu])
                ws.cell(row=current_row, column=6).number_format = '0.0000' 
                ws.cell(row=current_row, column=7).number_format = '0.00'   
                ws.cell(row=current_row, column=10).number_format = '0.0000' 
                
                ws.append(["", mesto, "", "", "16:30:00", "", "", "", "", ""])
                current_row += 2

            ws.append(["
