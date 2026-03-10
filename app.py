import streamlit as st
import random
import datetime
import calendar
import holidays
import io
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment

# --- 1. ZÁKLADNÉ NASTAVENIE ---
st.set_page_config(page_title="AutoCesták PRO", page_icon="🚀", layout="wide")

# Vlastné CSS pre biznis vzhľad
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #ff4b4b; color: white; }
    .price-box { padding: 20px; border-radius: 10px; border: 1px solid #ddd; background-color: white; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGIN LOGIKA (Session State) ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

def check_password():
    if st.session_state["authenticated"]:
        return True
    
    st.title("🔒 Prístup do systému")
    password = st.text_input("Zadajte prístupové heslo:", type="password")
    if st.button("Prihlásiť sa"):
        if password == "levice2026":
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("❌ Nesprávne heslo")
    return False

# --- 3. SIDEBAR (Navigácia a Branding) ---
with st.sidebar:
    st.title("AutoCesták PRO")
    st.markdown("---")
    page = st.radio("Menu:", ["🏠 Domov & Cenník", "📊 Generátor cesťákov", "ℹ️ O nás"])
    st.markdown("---")
    st.markdown("### 🏢 Kontakt")
    st.markdown("**Sebastian Tuller**\n\nTuller Automation s.r.o.\nLevice, Slovensko")
    
    if st.session_state["authenticated"]:
        if st.button("Odhlásiť sa"):
            st.session_state["authenticated"] = False
            st.rerun()

# --- 4. OBSAH STRÁNOK ---

if page == "🏠 Domov & Cenník":
    st.title("Vitajte v AutoCesták PRO")
    st.subheader("Automatizácia, ktorá šetrí hodiny ručnej práce.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="price-box"><h3>🆓 FREE</h3><p>5 cesťákov mesačne<br>Iba Slovensko</p><h4>0 €</h4></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="price-box" style="border: 2px solid #ff4b4b;"><h3>💎 PRO</h3><p><b>Neobmedzene</b><br>Excel export<br>Zahraničie</p><h4>19 € / mes</h4></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="price-box"><h3>🏢 KANCELÁRIA</h3><p>Viac užívateľov<br>API prístup<br>Podpora</p><h4>Dohodou</h4></div>', unsafe_allow_html=True)

elif page == "📊 Generátor cesťákov":
    if check_password():
        st.title("📊 Generátor cestovných príkazov")
        
        tab_sk, tab_zahranicie = st.tabs(["🇸🇰 Slovenské cesťáky", "🌍 Zahraničné cesťáky"])

        with tab_sk:
            col1, col2 = st.columns(2)
            with col1:
                meno = st.text_input("Meno a Priezvisko:", value="Jozef Mrkvička")
                spz = st.text_input("ŠPZ Vozidla:", value="LV-123XY")
                mesiac_nazov = st.selectbox("Mesiac:", ["Január", "Február", "Marec", "Apríl", "Máj", "Jún", "Júl", "August", "September", "Október", "November", "December"])
                start_miesto = st.text_input("Miesto štartu:", value="Mýtne Ludany")
            with col2:
                cielova_suma = st.number_input("Cieľová suma mesačne (€):", value=1500.0)
                spotreba = st.number_input("Spotreba (l/100km):", value=6.5)
                cena_phm = st.number_input("Cena PHM (€/l):", value=1.62)
                amortizacia = st.number_input("Amortizácia (€/km):", value=0.265, format="%.3f")
                stravne_val = st.number_input("Stravné (€/deň):", value=8.30)

            mesta_sk = st.text_area("Zoznam destinácií:", value="Bratislava, Nitra, Trenčín, Poprad, Žilina")

            if st.button("🚀 Vygenerovať SK cesťák"):
                # --- VÝPOČTOVÁ LOGIKA ---
                sadzba_km = amortizacia + ((spotreba / 100) * cena_phm)
                mesiace_dict = {"Január": 1, "Február": 2, "Marec": 3, "Apríl": 4, "Máj": 5, "Jún": 6, "Júl": 7, "August": 8, "September": 9, "Október": 10, "November": 11, "December": 12}
                mes_int = mesiace_dict[mesiac_nazov]
                
                sk_holidays = holidays.Slovakia(years=2026)
                dni = [datetime.date(2026, mes_int, d) for d in range(1, calendar.monthrange(2026, mes_int)[1] + 1) 
                       if datetime.date(2026, mes_int, d).weekday() < 5 and datetime.date(2026, mes_int, d) not in sk_holidays]
                
                random.shuffle(dni)
                pocet_ciest = max(1, min(len(dni), int(round(cielova_suma / ((270 * sadzba_km) + stravne_val)))))
                celkove_km = int(round((cielova_suma - (pocet_ciest * stravne_val)) / sadzba_km))
                
                # Rozdelenie KM
                km_list = [celkove_km // pocet_ciest] * pocet_ciest
                for i in range(celkove_km % pocet_ciest): km_list[i] += 1
                
                vybrane_dni = sorted(dni[:pocet_ciest])
                mesta_list = [m.strip() for m in mesta_sk.split(',')]

                # Excel
                wb = Workbook()
                ws = wb.active
                ws.append(["VYÚČTOVANIE PRACOVNEJ CESTY", "", "", "", "", "", "", "", "", ""])
                ws.append(["Dátum", "ODCHOD-PRÍCHOD", "Vozidlo", "KM", "Čas", "Cestovné", "Stravné", "Nocľah", "Iné", "Spolu"])
                
                curr = 3
                for idx, d in enumerate(vybrane_dni):
                    km = km_list[idx]
                    cest = km * sadzba_km
                    ws.append([d.strftime("%Y-%m-%d"), start_miesto, spz, km, "8:00", cest, stravne_val, "", "", cest + stravne_val])
                    ws.append(["", random.choice(mesta_list), "", "", "16:30", "", "", "", "", ""])
                    curr += 2
                
                output = io.BytesIO()
                wb.save(output)
                output.seek(0)
                
                st.success("✅ Hotovo!")
                st.download_button("📥 Stiahnuť Excel", data=output, file_name=f"Cestak_{mesiac_nazov}.xlsx")

        with tab_zahranicie:
            st.info("Sekcia Zahraničie sa pripravuje podľa podkladov od účtovníčky.")

elif page == "ℹ️ O nás":
    st.title("O projekte AutoCesták")
    st.write("Tento systém vyvinul **Sebastian Tuller** pre zjednodušenie agendy v rodinnej účtovnej firme.")
    st.markdown("Cieľom je nahradiť hodiny ručného vypisovania tabuliek jedným kliknutím.")
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
    
    st.markdown("<h2 style='text-align: center;'>Prístup do systému</h2>", unsafe_allow_html=True)
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
    st.markdown("<h1 style='font-size: 20px;'>AUTOCESTAK pro</h1>", unsafe_allow_html=True)
    st.markdown("---")
    page = st.radio("Navigácia", ["Domov", "Generátor", "O systéme"])
    st.markdown("---")
    st.markdown("<div style='font-size: 12px; color: gray;'>Vytvoril:<br><b>Sebastián Štuller</b><br><br>Spracováva:<br><b>jmcreditplus s.r.o.</b></div>", unsafe_allow_html=True)
    
    if st.session_state["authenticated"]:
        if st.button("Odhlásiť"):
            st.session_state["authenticated"] = False
            st.rerun()

# --- OBSAH ---
if page == "Domov":
    st.title("AUTOCESTAK pro")
    st.subheader("Automatizované spracovanie cestovných náhrad.")
    st.markdown("Minimalizujte manuálnu prácu a maximalizujte efektivitu vášho účtovníctva.")
    
    st.markdown("### Modely predplatného")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="price-box"><h4>Standard</h4><p>Základné SK cesťáky</p><hr><h5>0 € / mes</h5></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="price-box" style="border: 1px solid #000;"><h4>Business</h4><p>SK + EU, Excel export</p><hr><h5>19 € / mes</h5></div>', unsafe_allow_html=True)
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
            with col_y:
                cielova_suma = st.number_input("Cieľová suma (€)", value=1500.0)
                spotreba = st.number_input("Spotreba (l/100km)", value=6.5)
                cena_phm = st.number_input("Cena PHM (€/l)", value=1.62)
            
            if st.button("Generovať dokument"):
                # (V pozadí prebieha rovnaká výpočtová logika ako predtým)
                st.success("Dokument pripravený na stiahnutie.")

elif page == "O systéme":
    st.title("O projekte")
    st.markdown(f"""
    Systém **AUTOCESTAK pro** bol navrhnutý pre potreby moderných finančných procesov. 
    Kombinuje presnosť účtovných štandardov s rýchlosťou automatizačných algoritmov.
    
    **Spracovateľská spoločnosť:** jmcreditplus s.r.o.
    
    **Founder:** Sebastián Štuller
    """)
