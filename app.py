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
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CUSTOM CSS FOR PROFESSIONAL UI ---
st.markdown("""
<style>
    /* Hauptansicht verfeinern */
    .main {
        background-color: #f8f9fa;
    }
    
    /* Header Container Styling */
    .app-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 24px;
        border-radius: 16px;
        color: white;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        margin-bottom: 25px;
    }
    .app-header h1 {
        color: #ffffff !important;
        font-weight: 700;
        margin: 0;
        font-size: 2.2rem;
    }
    .app-header p {
        color: #e0e6ed !important;
        margin-top: 5px;
        font-size: 1.05rem;
    }

    /* Cards Styling */
    .custom-card {
        background-color: #ffffff;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border: 1px solid #e9ecef;
        margin-bottom: 20px;
    }
    
    /* Workflow Stepper */
    .workflow-stepper {
        display: flex;
        justify-content: space-between;
        background-color: #ffffff;
        padding: 14px 20px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        margin-bottom: 25px;
        border: 1px solid #e2e8f0;
        font-weight: 600;
        font-size: 0.95rem;
    }
    .step-active { color: #2a5298; border-bottom: 2px solid #2a5298; }
    .step-inactive { color: #94a3b8; }
    
    /* 2D Parking Simulation View */
    .parking-sim-box {
        background-color: #e2e8f0;
        border: 2px dashed #94a3b8;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        margin-top: 15px;
    }
    
    /* Hide Streamlit Default elements */
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

# --- HEADER BEREICH ---
st.markdown("""
<div class="app-header">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h1>🚗 KI Parkassistent</h1>
            <p>Smart Parking Guide & AI Space Recognition System</p>
        </div>
        <div style="font-size: 2rem;">🛡️ v1.0</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Modell laden (gecached)
model = load_parking_model()

# ==============================================================================
# 1. HOMEBILDSCHIRM (Fahrzeug- & Park-Einstellungen)
# ==============================================================================
if st.session_state.page == "home":
    
    st.markdown('<div class="workflow-stepper"><span class="step-active">1. Fahrzeugdaten eingeben</span> <span class="step-inactive">→ 2. Foto hochladen → 3. Analyse & Guide</span></div>', unsafe_allow_html=True)
    
    col_main, col_preview = st.columns([1.2, 0.8], gap="large")
    
    with col_main:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.subheader("⚙️ Fahrzeug & Park-Einstellungen")
        st.write("Bitte gib hier die Abmessungen deines Fahrzeugs ein. Diese Angaben werden für die Berechnung der Parklücke und den Einpark-Guide verwendet.")
        
        st.markdown("---")
        
        # Eingabe Autolänge
        car_length = st.slider(
            "📐 Autolänge (in Metern):",
            min_value=2.5,
            max_value=6.0,
            value=float(st.session_state.car_length),
            step=0.1,
            help="Standard-Kompaktklasse: ca. 4.3m - 4.5m"
        )
        
        # Eingabe Autobreite
        car_width = st.slider(
            "📐 Autobreite (in Metern):",
            min_value=1.4,
            max_value=2.5,
            value=float(st.session_state.car_width),
            step=0.1,
            help="Standard-Breite inkl. Außenspiegel: ca. 1.8m - 2.0m"
        )
        
        # Park-Typ Auswahl
        parking_type = st.selectbox(
            "🅿️ Gewünschter Park-Typ:",
            ["Längseinparken (Parallel)", "Querseinparken (Senkrecht)"],
            index=0 if "Parallel" in st.session_state.parking_type else 1
        )
        
        # Speichern im Session State
        st.session_state.car_length = car_length
        st.session_state.car_width = car_width
        st.session_state.parking_type = parking_type
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("🚀 EINPARKHILFE STARTEN", use_container_width=True, type="primary"):
            st.session_state.page = "function"
            st.rerun()
            
        st.markdown('</div>', unsafe_allow_html=True)

    with col_preview:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.subheader("📋 Zusammenfassung")
        
        st.info(f"""
        **Gespeicherte Maße:**
        * **Fahrzeuglänge:** `{car_length} m`
        * **Fahrzeugbreite:** `{car_width} m`
        * **Parkmodus:** `{parking_type}`
        """)
        
        st.markdown("### ℹ️ Funktionsweise der KI")
        st.write("""
        1. **Bildanalyse:** Unser Machine-Learning-Modell erkennt Fahrzeuge und Freiräume in Straßenfotos.
        2. **Geometrie-Abgleich:** Die App berechnet den benötigten Einparkpuffer anhand deiner eigegebenen Maße (`Länge + 1.0m`).
        3. **Schritt-für-Schritt Guide:** Erhalte exakte Anweisungen zum Lenkeinschlag und Ausrichten.
        """)
        st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# 2. & 3. FUNKTIONSBILDSCHIRM (Upload, Analyse & Guide)
# ==============================================================================
elif st.session_state.page == "function":
    
    st.markdown('<div class="workflow-stepper"><span class="step-inactive">1. Fahrzeugdaten</span> → <span class="step-active">2. Foto hochladen → 3. Analyse & Guide</span></div>', unsafe_allow_html=True)
    
    # Top Navigation / Zurück-Button
    if st.button("⬅️ Fahrzeugdaten ändern", type="secondary"):
        st.session_state.page = "home"
        st.rerun()
        
    col_upload, col_result = st.columns([1, 1], gap="large")
    
    with col_upload:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.subheader("📸 1. Foto der Parklücke hochladen")
        st.write("Lade hier ein Foto aus der Sicht des Fahrers oder von der Straße hoch.")
        
        uploaded_file = st.file_uploader(
            "Foto auswählen (JPG, PNG)...", 
            type=["jpg", "jpeg", "png"]
        )
        
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Hochgeladene Parklücke", use_container_width=True)
        else:
            st.warning("Bitte lade ein Foto hoch, um die KI-Analyse zu starten.")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_result:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.subheader("🔍 2. KI-Analyse & Auswertung")
        
        if uploaded_file is not None:
            with st.spinner("Analysiere Parklücke mit ML-Modell (YOLOv8 / Computer Vision)..."):
                
                # Aufruf der Bildanalyse-Logik
                gap_size, annotated_img, cars_count = model.analyze_parking_space(image)
                
                min_required = st.session_state.car_length + 1.0  # Puffer berechnen
                
                # Visualisiertes KI-Ergebnis-Bild anzeigen
                st.image(annotated_img, caption=f"KI-Erkennung ({cars_count} Begrenzungsfahrzeuge erkannt)", use_container_width=True)
                
                st.markdown("---")
                
                # Validierung der Lücke
                if gap_size >= min_required:
                    st.success(f"✅ **PASST PERFEKT!**\n\nErkannte Lücke: **{gap_size:.1f}m** | Benötigt: **{min_required:.1f}m** ({st.session_state.car_length}m Auto + Puffer)")
                elif gap_size >= st.session_state.car_length + 0.4:
                    st.warning(f"⚠️ **SEHR ENG!**\n\nErkannte Lücke: **{gap_size:.1f}m** | Benötigt eigentlich: **{min_required:.1f}m**. Nur für sehr geübte Fahrer!")
                else:
                    st.error(f"❌ **ZU ENG!**\n\nErkannte Lücke: **{gap_size:.1f}m** | Dein Auto benötigt mindestens **{min_required:.1f}m**.")

        else:
            st.info("Warte auf Foto-Upload...")
            
        st.markdown('</div>', unsafe_allow_html=True)

    # ==========================================================================
    # 3. ERWEITERTE ANALYSE & ANLEITUNG (Screen unten)
    # ==========================================================================
    if uploaded_file is not None:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.subheader("🧭 3. Schritt-für-Schritt Einpark-Guide")
        
        guide_col1, guide_col2 = st.columns([1, 1], gap="large")
        
        with guide_col1:
            st.markdown("### 🚘 2D-Trajektorie & Abstände")
            
            # 2D Simulation / Schema
            st.markdown(f"""
            <div class="parking-sim-box">
                <div style="font-weight: bold; color: #2a5298;">2D-Parkfeld-Schema</div>
                <div style="margin: 15px 0;">
                    🚗 <b>Dein Fahrzeug:</b> {st.session_state.car_length}m × {st.session_state.car_width}m<br>
                    📏 <b>Geschätzter Bordsteinabstand:</b> ~0.3m<br>
                    📐 <b>Erforderlicher Lenkwinkel:</b> 45°
                </div>
                <div style="background-color: #cbd5e1; height: 40px; border-radius: 6px; display: flex; align-items: center; justify-content: center;">
                    Bordstein / Fahrbahnmarkierung
                </div>
            </div>
            """, unsafe_allow_html=True)

        with guide_col2:
            st.markdown("### 📋 Schritt-für-Schritt-Anleitung")
            
            if "Parallel" in st.session_state.parking_type:
                st.markdown("""
                1. **Vorbeifahren & Ausrichten:**  
                   Fahre auf gleiche Höhe wie das vordere Begrenzungsfahrzeug (Abstand ca. 0.5–0.8 m).
                
                2. **Einlenken & Rückwärtsgang:**  
                   Lege den Rückwärtsgang ein, schlage das Lenkrad **voll nach rechts** ein und rolle langsam zurück.
                
                3. **Gegenlenken & Geradeziehen:**  
                   Sobald dein Fahrzeug in einem **45°-Winkel** zur Straße steht, stelle das Lenkrad gerade und setze weiter zurück.
                
                4. **Einparken Bestätigen:**  
                   Kurz vor dem Bordstein Lenkrad **voll nach links** einschlagen, parallel ausrichten und Abstand nach vorne/hinten mitteln.
                """)
            else:
                st.markdown("""
                1. **Positionierung:**  
                   Fahre im 90°-Winkel zur Parklücke vor und halte ca. 1.5–2 Meter Abstand zu den geparkten Autos.
                
                2. **Einlenken (Rückwärtsgang):**  
                   Setze den Blinker, schlage das Lenkrad voll in Richtung der Lücke ein und setze langsam zurück.
                
                3. **Gegenlenken:**  
                   Sobald das Fahrzeug parallel zu den Nachbarautos steht, Lenkrad gerade stellen.
                
                4. **Einparken Bestätigen:**  
                   Vorsichtig zurücksetzen, bis das Fahrzeug vollständig in der Lücke steht.
                """)

        st.markdown('</div>', unsafe_allow_html=True)
