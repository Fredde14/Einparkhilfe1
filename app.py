import streamlit as st
from PIL import Image
import numpy as np
import os
import sys

# Füge Root-Verzeichnis zum Pfad hinzu
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
    /* Hintergrund und globale Schrift */
    .main {
        background: linear-gradient(135deg, #f4f7f6 0%, #e9ecef 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Edler Header mit Farbverlauf */
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
    
    /* App Logo Badge */
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

    /* Container Karten */
    .custom-card {
        background-color: #ffffff;
        border-radius: 16px;
        padding: 28px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.06);
        border: 1px solid #e2e8f0;
        margin-bottom: 24px;
    }
    
    /* Workflow Stepper */
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
    
    /* 2D Parking Simulation View */
    .parking-sim-box {
        background: linear-gradient(135deg, #ebf8ff 0%, #e2e8f0 100%);
        border: 2px dashed #3182ce;
        border-radius: 14px;
        padding: 24px;
        text-align: center;
        margin-top: 15px;
    }

    /* Streamlit Button Overrides für professionellen Look */
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

# --- EIGENES APP-LOGO & HEADER ---
st.markdown("""
<div class="app-header">
    <div>
        <h1>KI Parkassistent</h1>
        <p>Smart Parking Guide & Advanced AI Analysis System</p>
    </div>
    <div class="app-logo-badge">
        <span>🅿️</span> ParkAI Pro
    </div>
</div>
""", unsafe_allow_html=True)

# Modell laden (gecached)
model = load_parking_model()

# ==============================================================================
# 1. HOMEBILDSCHIRM (Fahrzeug- & Park-Einstellungen - Direkt beim Start)
# ==============================================================================
if st.session_state.page == "home":
    
    st.markdown('<div class="workflow-stepper"><span class="step-active">1. Fahrzeugdaten eingeben</span> <span class="step-inactive">→ 2. Foto hochladen → 3. Analyse & Guide</span></div>', unsafe_allow_html=True)
    
    col_main, col_preview = st.columns([1.2, 0.8], gap="large")
    
    with col_main:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.subheader("⚙️ Fahrzeug- & Park-Einstellungen")
        st.write("Bitte lege hier zu Beginn die exakten Abmessungen deines Fahrzeugs fest. Diese Werte fließen in die gesamte KI-Berechnung ein.")
        
        st.markdown("---")
        
        # Eingabe Autolänge
        car_length = st.slider(
            "📐 Autolänge (in Metern):",
            min_value=2.5,
            max_value=6.0,
            value=float(st.session_state.car_length),
            step=0.1
        )
        
        # Eingabe Autobreite
        car_width = st.slider(
            "📐 Autobreite (in Metern):",
            min_value=1.4,
            max_value=2.5,
            value=float(st.session_state.car_width),
            step=0.1
        )
        
        # Park-Typ Auswahl
        parking_type = st.selectbox(
            "🅿️ Bevorzugter Park-Typ:",
            ["Längseinparken (Parallel)", "Querseinparken (Senkrecht)"],
            index=0 if "Parallel" in st.session_state.parking_type else 1
        )
        
        # Speichern im Session State
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
        1. **Home:** Maße einmalig einstellen & starten.
        2. **Funktionsbildschirm:** Foto der Parklücke hochladen.
        3. **Analyse & Guide:** Maßgeschneiderte Einpark-Anleitung erhalten.
        """)
        st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# 2. & 3. FUNKTIONSBILDSCHIRM (Upload, KI-Analyse & Anleitung)
# ==============================================================================
elif st.session_state.page == "function":
    
    st.markdown('<div class="workflow-stepper"><span class="step-inactive">1. Fahrzeugdaten</span> → <span class="step-active">2. Foto hochladen → 3. Analyse & Guide</span></div>', unsafe_allow_html=True)
    
    # Navigation zurück zum Homebildschirm
    if st.button("⬅️ Zurück zu den Fahrzeugeinstellungen"):
        st.session_state.page = "home"
        st.rerun()
        
    col_upload, col_result = st.columns([1, 1], gap="large")
    
    with col_upload:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.subheader("📸 1. Foto der Parklücke hochladen")
        st.write("Lade ein Foto der Parklücke hoch, um die automatische Raum- und Lückenanalyse zu starten.")
        
        uploaded_file = st.file_uploader(
            "Wähle eine Bilddatei aus...", 
            type=["jpg", "jpeg", "png"]
        )
        
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Hochgeladenes Parklücken-Foto", use_container_width=True)
        else:
            st.warning("Warte auf Foto-Upload...")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_result:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.subheader("🔍 2. KI-Analyseergebnis")
        
        if uploaded_file is not None:
            with st.spinner("KI analysiert Parklücke und Begrenzungen..."):
                
                gap_size, annotated_img, cars_count = model.analyze_parking_space(image)
                min_required = st.session_state.car_length + 1.0  # Inklusive Sicherheits-Puffer
                
                st.image(annotated_img, caption=f"Erkannte Objekte: {cars_count} Begrenzungsfahrzeuge", use_container_width=True)
                
                st.markdown("---")
                
                if gap_size >= min_required:
                    st.success(f"✅ **PASST PERFEKT!**\n\nErkannte Lücke: **{gap_size:.1f}m** | Benötigt: **{min_required:.1f}m** (inkl. Puffer)")
                elif gap_size >= st.session_state.car_length + 0.4:
                    st.warning(f"⚠️ **SEHR ENG!**\n\nErkannte Lücke: **{gap_size:.1f}m** | Benötigt: **{min_required:.1f}m**. Nur für geübte Fahrer!")
                else:
                    st.error(f"❌ **ZU ENG!**\n\nErkannte Lücke: **{gap_size:.1f}m** | Dein Auto benötigt mind. **{min_required:.1f}m**.")

        else:
            st.info("Bitte zuerst links ein Foto hochladen, um die Analyse zu aktivieren.")
            
        st.markdown('</div>', unsafe_allow_html=True)

    # ==========================================================================
    # ERWEITERTE ANALYSE & SCHRITT-FÜR-SCHRITT GUIDELINE (Unten)
    # ==========================================================================
    if uploaded_file is not None:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.subheader("🧭 3. Erweiterte Analyse & Einpark-Guide")
        
        guide_col1, guide_col2 = st.columns([1, 1], gap="large")
        
        with guide_col1:
            st.markdown("### 📐 Geometrische 2D-Vorschau")
            st.markdown(f"""
            <div class="parking-sim-box">
                <div style="font-weight: 700; color: #2b6cb0; font-size: 1.1rem; margin-bottom: 8px;">Berechneter Park-Pfad</div>
                <div style="font-size: 0.95rem; color: #4a5568; line-height: 1.6;">
                    🚗 <b>Fahrzeugmaße:</b> {st.session_state.car_length}m × {st.session_state.car_width}m<br>
                    📏 <b>Optimaler Lenkwinkel:</b> 45 Grad<br>
                    🛡️ <b>Kalkulierter Bordsteinabstand:</b> 0.3m
                </div>
            </div>
            """, unsafe_allow_html=True)

        with guide_col2:
            st.markdown("### 📋 Schritt-für-Schritt-Anleitung")
            
            if "Parallel" in st.session_state.parking_type:
                st.markdown("""
                1. **Vorbeifahren & Ausrichten:** Parallel zum vorderen Begrenzungsauto positionieren.
                2. **Einlenken:** Rückwärtsgang einlegen, Lenkrad **voll nach rechts** drehen.
                3. **Gegenlenken:** Bei Erreichen des 45°-Winkels Lenkrad gerade stellen und zurücksetzen.
                4. **Abschluss:** Kurz vor dem Bordstein **voll nach links** einlenken und parallel ausrichten.
                """)
            else:
                st.markdown("""
                1. **Positionierung:** Im 90°-Winkel vor der Lücke in Position bringen.
                2. **Rückwärtsgang:** Kontrolliert und langsam in die Senkrechtlücke rollen.
                3. **Geradeziehen:** Sobald das Auto mittig steht, Lenkrad zentrieren.
                4. **Bestätigen:** Endposition prüfen und Einparkvorgang abschließen.
                """)

        st.markdown('</div>', unsafe_allow_html=True)
