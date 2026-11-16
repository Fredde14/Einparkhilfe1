import streamlit as st
from PIL import Image
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from models.parking_model import load_parking_model

# --- SEITEN-KONFIGURATION ---
st.set_page_config(
    page_title="KI Parkassistent | Smart Parking Guide",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- HOCHWERTIGES CUSTOM CSS (EDLES BLAU & VERLÄUFE) ---
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #f4f7f6 0%, #e9ecef 100%);
        font-family: 'Inter', sans-serif;
    }
    .app-header {
        background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
        padding: 28px 32px;
        border-radius: 16px;
        color: white;
        box-shadow: 0 10px 25px rgba(15, 32, 39, 0.2);
        margin-bottom: 30px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .app-header h1 {
        color: #ffffff !important;
        font-weight: 800;
        margin: 0;
        font-size: 2.2rem;
        letter-spacing: -0.5px;
    }
    .app-header p {
        color: #a0aec0 !important;
        margin: 5px 0 0 0;
        font-size: 1.05rem;
    }
    .app-logo-badge {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 10px 18px;
        border-radius: 12px;
        font-size: 1.2rem;
        font-weight: bold;
        color: #63b3ed;
        display: flex;
        align-items: center;
        gap: 8px;
        backdrop-filter: blur(5px);
    }
    .custom-card {
        background-color: #ffffff;
        border-radius: 16px;
        padding: 28px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.06);
        border: 1px solid #e2e8f0;
        margin-bottom: 24px;
    }
    .workflow-stepper {
        display: flex;
        justify-content: space-between;
        background-color: #ffffff;
        padding: 16px 24px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.04);
        margin-bottom: 28px;
        border: 1px solid #e2e8f0;
        font-weight: 600;
        font-size: 0.95rem;
    }
    .step-active { color: #3182ce; border-bottom: 2px solid #3182ce; padding-bottom: 2px; }
    .step-inactive { color: #a0aec0; }
    .parking-sim-box {
        background: linear-gradient(135deg, #ebf8ff 0%, #e2e8f0 100%);
        border: 2px dashed #3182ce;
        border-radius: 14px;
        padding: 24px;
        text-align: center;
        margin-top: 15px;
    }
    div.stButton > button {
        background: linear-gradient(135deg, #2b6cb0 0%, #2c5282 100%);
        color: white;
        border-radius: 10px;
        font-weight: 600;
        padding: 0.6rem 1.2rem;
        border: none;
        box-shadow: 0 4px 12px rgba(43, 108, 176, 0.3);
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        background: linear-gradient(135deg, #3182ce 0%, #2b6cb0 100%);
        box-shadow: 0 6px 16px rgba(43, 108, 176, 0.4);
        transform: translateY(-1px);
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE INITIALISIERUNG ---
if "page" not in st.session_state:
    st.session_state.page = "home"
if "car_length" not in st.session_state:
    st.session_state.car_length = 4.5
if "car_width" not in st.session_state:
    st.session_state.car_width = 1.8
if "parking_type" not in st.session_state:
    st.session_state.parking_type = "Längseinparken (Parallel)"

# --- APP HEADER & LOGO ---
st.markdown("""
<div class="app-header">
    <div>
        <h1>KI Parkassistent</h1>
        <p>Smart Parking Guide & Precision Assistant</p>
    </div>
    <div class="app-logo-badge">
        <span>🅿️</span> ParkAI Pro
    </div>
</div>
""", unsafe_allow_html=True)

@st.cache_resource
def get_model():
    return load_parking_model()

model = get_model()

# ==============================================================================
# 1. HOMEBILDSCHIRM (Fahrzeug- & Park-Einstellungen)
# ==============================================================================
if st.session_state.page == "home":
    st.markdown('<div class="workflow-stepper"><span class="step-active">1. Fahrzeugdaten eingeben</span> <span class="step-inactive">→ 2. Foto & Maße → 3. Live-Anleitung</span></div>', unsafe_allow_html=True)
    
    col_main, col_preview = st.columns([1.2, 0.8], gap="large")
    
    with col_main:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.subheader("⚙️ Fahrzeug- & Park-Einstellungen")
        st.write("Lege hier die Abmessungen deines Autos fest. Diese Daten bleiben für die gesamte Sitzung gespeichert.")
        st.markdown("---")
        
        car_length = st.slider(
            "📐 Autolänge (in Metern):",
            min_value=2.5, max_value=6.0, value=float(st.session_state.car_length), step=0.1
        )
        car_width = st.slider(
            "📐 Autobreite (in Metern):",
            min_value=1.4, max_value=2.5, value=float(st.session_state.car_width), step=0.1
        )
        parking_type = st.selectbox(
            "🅿️ Park-Typ:",
            ["Längseinparken (Parallel)", "Querseinparken (Senkrecht)"],
            index=0 if "Parallel" in st.session_state.parking_type else 1
        )
        
        st.session_state.car_length = car_length
        st.session_state.car_width = car_width
        st.session_state.parking_type = parking_type
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 EINPARKHILFE STARTEN", use_container_width=True):
            st.session_state.page = "function"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col_preview:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.subheader("📋 System-Übersicht")
        st.info(f"""
        **Aktives Setup:**
        * **Fahrzeuglänge:** `{car_length} m`
        * **Fahrzeugbreite:** `{car_width} m`
        * **Modus:** `{parking_type}`
        """)
        st.markdown("### 💡 Ablauf")
        st.write("""
        1. **Home:** Maße einmalig einstellen.
        2. **Funktionsbildschirm:** Foto hochladen & reale Parklücke manuell eingeben.
        3. **Anleitung:** Maßgeschneiderte Einpark-Schritte anhand der erkannten Begrenzungsautos erhalten.
        """)
        st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# 2. & 3. FUNKTIONSBILDSCHIRM (Upload, Manuelle Lücke & Anweisungen)
# ==============================================================================
elif st.session_state.page == "function":
    st.markdown('<div class="workflow-stepper"><span class="step-inactive">1. Fahrzeugdaten</span> → <span class="step-active">2. Foto & Maße → 3. Live-Anleitung</span></div>', unsafe_allow_html=True)
    
    if st.button("⬅️ Zurück zu den Fahrzeugeinstellungen"):
        st.session_state.page = "home"
        st.rerun()
        
    col_upload, col_result = st.columns([1, 1], gap="large")
    
    with col_upload:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.subheader("📸 1. Foto & Manuelle Lückeneingabe")
        st.write("Lade ein Foto der Situation hoch und gib die selbst gemessene Länge der Parklücke ein.")
        
        uploaded_file = st.file_uploader("Wähle eine Bilddatei aus...", type=["jpg", "jpeg", "png"])
        
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            
            st.markdown("#### 📏 Manuelle Lücken-Eingabe")
            manual_gap_size = st.slider(
                "Wie lang ist die Lücke in Metern? (geschätzt oder gemessen)",
                min_value=3.0, max_value=8.0, value=5.2, step=0.1,
                help="Gib hier den Wert ein, den du für die Lücke ermittelt hast."
            )
        else:
            manual_gap_size = 5.0
            st.warning("Warte auf Foto-Upload...")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_result:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.subheader("🔍 2. Szenen-Analyse")
        
        if uploaded_file is not None:
            with st.spinner("Erkenne Umgebung und Begrenzungsfahrzeuge..."):
                annotated_img, cars_count, detected_cars, active_model = model.analyze_scene(image)
                
                st.image(
                    annotated_img,
                    caption=f"Erkannte Begrenzungsfahrzeuge im Bild: {cars_count}",
                    use_container_width=True
                )
                
                st.markdown("---")
                
                min_req = st.session_state.car_length + 0.8
                
                if manual_gap_size >= min_req:
                    st.success(f"✅ **LÜCKE AUSREICHEND!**\n\nEingetragene Lücke: **{manual_gap_size:.1f}m** | Dein Auto: **{st.session_state.car_length}m** (Genug Puffer)")
                else:
                    st.error(f"❌ **LÜCKE ZU ENG!**\n\nEingetragene Lücke: **{manual_gap_size:.1f}m** | Benötigt: mind. **{min_req:.1f}m**.")
        else:
            st.info("Bitte zuerst links ein Foto hochladen.")
            
        st.markdown('</div>', unsafe_allow_html=True)

    # ==========================================================================
    # 3. SPEZIFISCHE ANWEISUNGEN (Objektbezogener Einpark-Guide)
    # ==========================================================================
    if uploaded_file is not None:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.subheader("🧭 3. Kontextbezogene Einpark-Anweisungen")
        
        guide_col1, guide_col2 = st.columns([1, 1], gap="large")
        
        with guide_col1:
            st.markdown("### 🎯 Situations-Check & Referenzen")
            st.markdown(f"""
            <div class="parking-sim-box">
                <div style="font-weight: 700; color: #2b6cb0; font-size: 1.1rem; margin-bottom: 8px;">Visueller Leitfaden</div>
                <div style="font-size: 0.95rem; color: #4a5568; line-height: 1.6;">
                    🚗 <b>Dein Auto:</b> {st.session_state.car_length}m Länge<br>
                    🅿️ <b>Lückengröße (Manuell):</b> {manual_gap_size:.1f}m<br>
                    🤖 <b>Erkannte Autos in Szene:</b> {cars_count} Fahrzeuge
                </div>
            </div>
            """, unsafe_allow_html=True)

        with guide_col2:
            st.markdown("### 📋 Schritt-für-Schritt Anweisungen für den Fahrer")
            
            # Dynamische Anweisungen basierend auf erkannten Objekten
            if cars_count >= 2:
                st.markdown(f"""
                1. **Ausrichten:** Fahre langsam vor, bis dein Heck auf Höhe des **ersten erkannten Autos (Fahrzeug 1)** steht. Halte ca. 0,5 m Seitenabstand.
                2. **Einlenken:** Lege den Rückwärtsgang ein, lenke das Lenkrad **voll nach rechts** und rolle langsam zurück.
                3. **Gegenlenken:** Sobald du im 45°-Winkel stehst, lenke **voll nach links** ein, um dich auf das **hintere Begrenzungsfahrzeug (Fahrzeug 2)** auszurichten.
                4. **Abschluss:** Ziehe das Auto gerade und halte an, sobald der Abstand nach hinten optimal verteilt ist.
                """)
            elif cars_count == 1:
                st.markdown(f"""
                1. **Positionierung:** Positioniere dich parallel direkt neben dem **erkannten Begrenzungsfahrzeug**.
                2. **Rückwärtsfahrt:** Lenkrad einschlagen und langsam zurücksetzen, bis dein Vorderrad auf Höhe des Hecks des Nachbarautos ist.
                3. **Einrollen:** Lenkrad in die entgegengesetzte Richtung einschlagen und komplett in die Lücke rollen.
                """)
            else:
                st.markdown(f"""
                1. **Anfahrt:** Positioniere das Fahrzeug parallel zur markierten Parkfläche.
                2. **Manöver:** Rückwärtsgang einlegen, kontrolliert einlenken und mithilfe der Spiegel einparken.
                """)

        st.markdown('</div>', unsafe_allow_html=True)
