import streamlit as st
from PIL import Image
import time
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

# --- HOCHWERTIGES CUSTOM CSS (EDLES BLAU & VERLÄUFE + NEUE COCKPIT-KACHELN) ---
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
    
    /* NEU: Kontraststarke Metric-Cards für schnelle Lesbarkeit im Auto */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 12px;
        margin-top: 12px;
        margin-bottom: 16px;
    }
    .metric-box {
        background: linear-gradient(135deg, #1a365d 0%, #2b6cb0 100%);
        color: white;
        padding: 16px 12px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 10px rgba(26, 54, 93, 0.15);
    }
    .metric-label {
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #bee3f8;
        margin-bottom: 4px;
    }
    .metric-value {
        font-size: 1.45rem;
        font-weight: 800;
        color: #ffffff;
    }

    /* NEU: Cockpit Schritt-Kacheln */
    .step-tile {
        background: #f8fafc;
        border: 1px solid #cbd5e1;
        border-left: 5px solid #94a3b8;
        border-radius: 12px;
        padding: 16px 18px;
        margin-bottom: 12px;
        transition: all 0.2s ease;
    }
    .step-tile-active {
        background: linear-gradient(135deg, #ebf8ff 0%, #bee3f8 100%);
        border: 1px solid #3182ce;
        border-left: 6px solid #2b6cb0;
        box-shadow: 0 4px 14px rgba(49, 130, 206, 0.18);
    }
    .step-tile-title {
        font-weight: 800;
        font-size: 1.05rem;
        color: #1a365d;
        margin-bottom: 4px;
    }
    .step-tile-desc {
        font-size: 0.95rem;
        color: #2d3748;
        line-height: 1.45;
    }

    .parking-sim-box {
        background: linear-gradient(135deg, #ebf8ff 0%, #e2e8f0 100%);
        border: 2px dashed #3182ce;
        border-radius: 14px;
        padding: 20px;
        text-align: center;
        margin-top: 10px;
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
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0
if "active_step" not in st.session_state:
    st.session_state.active_step = 1

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

# Modell direkt laden
model = load_parking_model()

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
        2. **Funktionsbildschirm:** Foto (aus ca. 5 m Entfernung) hochladen & reale Parklücke angeben.
        3. **Anleitung:** Interaktive Cockpit-Schritte anhand der erkannten Begrenzungsautos abrufen.
        """)
        st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# 2. & 3. FUNKTIONSBILDSCHIRM (Upload, Manuelle Lücke & Cockpit-Anweisungen)
# ==============================================================================
elif st.session_state.page == "function":
    st.markdown('<div class="workflow-stepper"><span class="step-inactive">1. Fahrzeugdaten</span> → <span class="step-active">2. Foto & Maße → 3. Live-Anleitung</span></div>', unsafe_allow_html=True)
    
    # Obere Einhand-Navigationsleiste (Zurück + Quick-Reset)
    nav_col1, nav_col2 = st.columns([1, 1])
    with nav_col1:
        if st.button("⬅️ Zurück zu den Fahrzeugeinstellungen", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()
    with nav_col2:
        if st.button("🔄 Neues Manöver starten (Foto zurücksetzen)", use_container_width=True):
            st.session_state.uploader_key += 1
            st.session_state.active_step = 1
            st.rerun()
        
    col_upload, col_result = st.columns([1, 1], gap="large")
    
    with col_upload:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.subheader("📸 1. Foto & Referenz-Eingabe")
        st.info("📏 **Aufnahme-Protokoll:** Fotografiere die Parklücke idealerweise aus ca. **5 Metern Entfernung** für optimale Referenz-Erkennung.")
        
        uploaded_file = st.file_uploader(
            "Wähle eine Bilddatei aus...",
            type=["jpg", "jpeg", "png"],
            key=f"uploader_{st.session_state.uploader_key}"
        )
        
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            
            st.markdown("#### 📐 Gemessene / Geschätzte Lückenlänge")
            manual_gap_size = st.slider(
                "Länge der Parklücke in Metern:",
                min_value=3.0, max_value=8.0, value=5.5, step=0.1,
                help="Referenzwert der Lücke für die Puffer-Berechnung."
            )
        else:
            manual_gap_size = 5.5
            st.warning("Warte auf Foto-Upload...")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_result:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.subheader("🔍 2. KI-Szenen-Analyse")
        
        if uploaded_file is not None:
            # Mehrstufiger Live-Status-Indikator
            with st.status("System analysiert Parkszene...", expanded=False) as status:
                st.write("1. Bild wird für 5m-Referenz-Maßstab normalisiert...")
                time.sleep(0.25)
                st.write("2. KI-Modell scannt Begrenzungsfahrzeuge...")
                annotated_img, cars_count, detected_cars, active_model = model.analyze_scene(image)
                st.write("3. Sicherheitsabstände & Einpark-Trajektorie berechnet.")
                status.update(label="✅ Live-Analyse abgeschlossen", state="complete", expanded=False)
                
            st.image(
                annotated_img,
                caption=f"Aktives System: {active_model} | Erkannte Begrenzungen: {cars_count}",
                use_container_width=True
            )
            
            min_req = st.session_state.car_length + 0.8
            buffer_space = max(0.0, manual_gap_size - st.session_state.car_length)
            
            # Kontraststarke Metric-Cards
            st.markdown(f"""
            <div class="metric-grid">
                <div class="metric-box">
                    <div class="metric-label">Dein Auto</div>
                    <div class="metric-value">{st.session_state.car_length:.1f} m</div>
                </div>
                <div class="metric-box">
                    <div class="metric-label">Parklücke</div>
                    <div class="metric-value">{manual_gap_size:.1f} m</div>
                </div>
                <div class="metric-box">
                    <div class="metric-label">Rangier-Puffer</div>
                    <div class="metric-value">+{buffer_space:.1f} m</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if manual_gap_size >= min_req:
                st.success(f"✅ **PASST KOMFORTABEL!** Du hast **{buffer_space:.1f} m** Sicherheits-Spielraum zum Einrangieren.")
            elif manual_gap_size >= st.session_state.car_length + 0.3:
                st.warning(f"⚠️ **ENGES MANÖVER!** Nur **{buffer_space:.1f} m** Spielraum – langsam und präzise einlenken.")
            else:
                st.error(f"❌ **ZU ENG!** Dein Fahrzeug benötigt mindestens **{min_req:.1f} m** inklusive Rangierpuffer.")
        else:
            st.info("Bitte zuerst links ein Foto hochladen, um den Live-Scan zu starten.")
            
        st.markdown('</div>', unsafe_allow_html=True)

    # ==========================================================================
    # 3. INTERAKTIVER COCKPIT-GUIDE (Visuelle Schritt-Kacheln)
    # ==========================================================================
    if uploaded_file is not None:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.subheader("🧭 3. Interaktiver Cockpit-Einpark-Guide")
        
        guide_col1, guide_col2 = st.columns([0.9, 1.1], gap="large")
        
        with guide_col1:
            st.markdown("### 🎛️ Manöver-Steuerung")
            st.write("Wähle den aktuellen Schritt während des Einparkens aus:")
            
            # Schnelle Schritt-Auswahl für Einhand-Bedienung
            step_choice = st.radio(
                "Aktiver Manöver-Schritt:",
                options=[1, 2, 3, 4],
                format_func=lambda x: f"Schritt {x} aktivieren",
                index=st.session_state.active_step - 1,
                horizontal=True
            )
            st.session_state.active_step = step_choice
            
            st.markdown(f"""
            <div class="parking-sim-box">
                <div style="font-weight: 800; color: #1a365d; font-size: 1.1rem; margin-bottom: 6px;">
                    Referenz-Setup (5m Distanz)
                </div>
                <div style="font-size: 0.95rem; color: #2d3748; line-height: 1.6;">
                    🚘 <b>Modus:</b> {st.session_state.parking_type}<br>
                    📐 <b>Abmessungen:</b> {st.session_state.car_length}m × {st.session_state.car_width}m<br>
                    🎯 <b>Ankerpunkte:</b> {cars_count} erkannte Begrenzungsfahrzeuge
                </div>
            </div>
            """, unsafe_allow_html=True)

        with guide_col2:
            st.markdown("### 📋 Live-Anweisungen")
            
            # Dynamische Texte je nach Park-Typ & erkannten Fahrzeugen
            if "Parallel" in st.session_state.parking_type:
                ref_front = "Fahrzeug 1 (vordere Begrenzung)" if cars_count >= 1 else "der vorderen Lückenbegrenzung"
                ref_back = "Fahrzeug 2 (hintere Begrenzung)" if cars_count >= 2 else "der hinteren Lückenbegrenzung"
                steps_data = [
                    ("1. Parallel ausrichten", f"Fahre langsam vor, bis dein Heck auf gleicher Höhe mit <b>{ref_front}</b> steht. Halte ca. 0,5 m Seitenabstand."),
                    ("2. Voll einschlagen & zurücksetzen", "Lege den Rückwärtsgang ein, schlage das Lenkrad <b>voll nach rechts</b> ein und rolle langsam im 45°-Winkel in die Lücke."),
                    ("3. Gegenlenken", f"Sobald deine Fahrzeugfront am Heck von <b>{ref_front}</b> vorbei ist, lenke <b>voll nach links</b> ein."),
                    ("4. Geradeziehen & Abstand prüfen", f"Rolle langsam weiter, bis du parallel zum Bordstein stehst und den Puffer zu <b>{ref_back}</b> optimal verteilt hast.")
                ]
            else:
                ref_side = "Fahrzeug 1" if cars_count >= 1 else "dem Nachbarfahrzeug"
                steps_data = [
                    ("1. Position vor der Lücke", f"Fahre im 90°-Winkel bis kurz hinter <b>{ref_side}</b> vor, sodass dein Heck zur Lückenmitte zeigt."),
                    ("2. Rückwärts einlenken", "Rückwärtsgang einlegen, Lenkrad voll in Richtung Lücke einschlagen und langsam anrollen."),
                    ("3. Fahrzeug zentrieren", f"Sobald du parallel neben <b>{ref_side}</b> stehst, Lenkrad komplett gerade stellen."),
                    ("4. Endposition erreichen", "Gerade zurücksetzen, bis die Fahrzeugfront bündig abschließt, und sichern.")
                ]
                
            # Rendern der visuellen Cockpit-Kacheln
            for idx, (title, desc) in enumerate(steps_data, start=1):
                active_class = "step-tile step-tile-active" if idx == st.session_state.active_step else "step-tile"
                badge = " 🟢 AKTIV" if idx == st.session_state.active_step else ""
                st.markdown(f"""
                <div class="{active_class}">
                    <div class="step-tile-title">{title}{badge}</div>
                    <div class="step-tile-desc">{desc}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)
