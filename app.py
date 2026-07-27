import io
import streamlit as st
from google import genai
from google.genai import types

# Bibliothèques pour le rapport PDF
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# -----------------------------------------------------------------------------
# CONFIGURATION DE LA PAGE & DESIGN SOMBRE MINIMALISTE (Style ChatGPT/Gemini)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="SécureActe Studio",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Style CSS sur-mesure : Design épuré Monochrome Noir / Gris / Blanc
st.markdown("""
    <style>
    /* Fond principal sombre et moderne */
    .stApp {
        background-color: #0d0d11;
        color: #e3e3e8;
        font-family: 'Inter', -apple-system, sans-serif;
    }
    
    /* En-tête sobre */
    .title-container {
        padding: 20px 0px 10px 0px;
        text-align: center;
    }
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        letter-spacing: -0.5px;
        color: #ffffff;
    }
    .sub-title {
        font-size: 0.95rem;
        color: #8e8e93;
        margin-top: -5px;
    }
    
    /* Boutons de prompt rapide (style puces ChatGPT/Gemini) */
    .stButton>button {
        background-color: #1a1a22 !important;
        color: #e3e3e8 !important;
        border: 1px solid #2e2e38 !important;
        border-radius: 12px !important;
        padding: 10px 16px !important;
        font-size: 0.88rem !important;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #2a2a35 !important;
        border-color: #ffffff !important;
        color: #ffffff !important;
    }
    
    /* Zones de dépôt de fichiers */
    [data-testid="stFileUploader"] {
        background-color: #14141a;
        border: 1px dashed #2e2e38;
        border-radius: 12px;
        padding: 15px;
    }
    
    /* Enregistreur vocal & Inputs */
    [data-testid="stAudioInput"] {
        background-color: #14141a;
        border-radius: 12px;
        border: 1px solid #2e2e38;
    }
    
    /* Cartes et conteneurs */
    .result-card {
        background-color: #14141a;
        border: 1px solid #2e2e38;
        border-radius: 16px;
        padding: 25px;
        margin-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# GENERATION DE RAPPORT PDF
# -----------------------------------------------------------------------------
def generate_pdf_report(report_text: str) -> io.BytesIO:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor('#000000'), spaceAfter=10)
    h2_style = ParagraphStyle('SectionTitle', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor('#1a1a1a'), spaceBefore=10, spaceAfter=4)
    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=9.5, leading=13, textColor=colors.HexColor('#2b2b2b'), spaceAfter=5)

    story = [Paragraph("<b>RAPPORT D'AUDIT JURIDIQUE SÉCUREACTE STUDIO</b>", title_style)]
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#000000'), spaceAfter=12))
    
    for line in report_text.split('\n'):
        clean = line.strip().replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        if not clean: continue
        if clean.startswith('# '): story.append(Paragraph(f"<b>{clean[2:]}</b>", h2_style))
        elif clean.startswith('## ') or clean.startswith('### '): story.append(Paragraph(f"<b>{clean.lstrip('#').strip()}</b>", h2_style))
        elif clean.startswith('- ') or clean.startswith('* '): story.append(Paragraph(f"• {clean[2:]}", body_style))
        else: story.append(Paragraph(clean, body_style))
            
    doc.build(story)
    buffer.seek(0)
    return buffer

# -----------------------------------------------------------------------------
# INITIALISATION DE L'API GEMINI
# -----------------------------------------------------------------------------
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    with st.sidebar:
        api_key = st.text_input("Clé API Gemini :", type="password")

if not api_key:
    st.info("💡 Veuillez configurer votre clé API Gemini dans les Secrets de Streamlit pour débloquer le Studio.")
    st.stop()

client = genai.Client(api_key=api_key)

# -----------------------------------------------------------------------------
# EN-TÊTE
# -----------------------------------------------------------------------------
st.markdown("""
    <div class="title-container">
        <div class="main-title">SécureActe Studio</div>
        <div class="sub-title">Assistant notarial multimodal : PDF, Photos, Audio Vocal & Analyse Texte</div>
    </div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# IDÉES DE PROMPTS RAPIDES (Style ChatGPT / Gemini)
# -----------------------------------------------------------------------------
st.markdown("##### 💡 Suggestions d'analyse rapide")
p_col1, p_col2, p_col3, p_col4 = st.columns(4)

selected_prompt_preset = ""

if p_col1.button("🔍 Audit Cadastre vs Acte"):
    selected_prompt_preset = "Effectue une comparaison ultra-rigoureuse entre la désignation cadastrale des pièces officielles et du projet d'acte."

if p_col2.button("👤 Contrôle CNI & Identités"):
    selected_prompt_preset = "Vérifie l'état civil complet (noms, prénoms, dates et lieux de naissance, régimes) entre les pièces justificatives et l'acte."

if p_col3.button("🚨 Détection des Coquilles"):
    selected_prompt_preset = "Repère toutes les coquilles typographiques, erreurs d'inversion de chiffres, ou fautes de frappe dans les documents."

if p_col4.button("💬 Résumé Exécutif Client"):
    selected_prompt_preset = "Rédige une note de synthèse claire, courtoise et professionnelle destinée au notaire et à son client."

# -----------------------------------------------------------------------------
# ENTRÉES MULTIMODALES (PDF, PHOTOS, VOCAL, TEXTE)
# -----------------------------------------------------------------------------
st.markdown("---")

col_files, col_input = st.columns([1, 1])

with col_files:
    st.markdown("##### 📂 Documents, Scans & Photos")
    uploaded_files = st.file_uploader(
        "Glissez tous vos fichiers (PDF, Photos PNG/JPG, CNI, Plan Cadastral...)",
        type=["pdf", "png", "jpg", "jpeg", "webp"],
        accept_multiple_files=True
    )

with col_input:
    st.markdown("##### 🎙️ Consigne Vocale & Instructions")
    
    # Composant Enregistreur Vocal Interactif
    audio_record = st.audio_input("Enregistrer une consigne vocale à la voix")
    
    # Zone de texte libre
    user_text_prompt = st.text_area(
        "Ou saisissez vos consignes écrites :",
        value=selected_prompt_preset if selected_prompt_preset else "",
        placeholder="Posez votre question ou décrivez ce que l'IA doit vérifier...",
        height=100
    )

# -----------------------------------------------------------------------------
# TRAITEMENT & EXECUTION PAR L'IA MULTIMODALE
# -----------------------------------------------------------------------------
st.markdown("<br>", unsafe_allow_html=True)
if st.button("✨ Lancer l'analyse multimodale Studio", type="primary", use_container_width=True):
    
    if not uploaded_files and not user_text_prompt and not audio_record:
        st.warning("⚠️ Veuillez déposer un document, enregistrer un message vocal ou saisir un texte.")
    else:
        try:
            with st.spinner("🧠 SécureActe Studio analyse vos données..."):
                payload = []
                
                # Directive système
                system_instruction = """
                Tu es SécureActe Studio, l'assistant d'IA juridique notarial le plus avancé.
                Examine avec une précision chirurgicale tous les éléments transmis (PDFs, images/photos, messages vocaux, instructions écrites).

                Si un message vocal ou du texte est fourni, réponds précisément à la demande exprimée.
                Si des documents/photos sont joints, effectue une vérification de conformité globale.

                Structure toujours ton rapport de manière lisible :
                # 🚦 VERDICT GLOBAL
                # 🚨 POINTS D'ATTENTION & ANOMALIES
                # ✅ ÉLÉMENTS VALIDÉS ET CONFORMES
                # 📝 RECOMMANDATIONS DIRECTES POUR LE CLERC
                """
                payload.append(system_instruction)

                # Ajout des fichiers audio vocaux
                if audio_record:
                    audio_part = types.Part.from_bytes(
                        data=audio_record.read(),
                        mime_type=audio_record.type or "audio/wav"
                    )
                    payload.append("Voici la consigne vocale enregistrée par l'utilisateur :")
                    payload.append(audio_part)

                # Ajout des images et PDF
                if uploaded_files:
                    payload.append("\nVoici les pièces justificatives et documents joints :")
                    for file in uploaded_files:
                        file_part = types.Part.from_bytes(
                            data=file.read(),
                            mime_type=file.type
                        )
                        payload.append(f"Fichier joint ({file.name}) :")
                        payload.append(file_part)

                # Ajout de la consigne textuelle
                if user_text_prompt:
                    payload.append(f"\nConsigne écrite de l'utilisateur : {user_text_prompt}")

                # Exécution Gemini 2.5 Flash
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=payload
                )

            # Stockage de la réponse
            st.session_state['studio_response'] = response.text
            st.success("Analyse terminée !")

        except Exception as e:
            st.error(f"Erreur technique : {str(e)}")

# -----------------------------------------------------------------------------
# AFFICHAGE DU RÉSULTAT
# -----------------------------------------------------------------------------
if 'studio_response' in st.session_state:
    st.markdown("---")
    st.markdown("### 📊 Rapport d'Analyse Studio")
    st.markdown(st.session_state['studio_response'])
    
    st.markdown("<br>", unsafe_allow_html=True)
    pdf_bytes = generate_pdf_report(st.session_state['studio_response'])
    
    st.download_button(
        label="📄 Imprimer le Rapport Officiel (PDF)",
        data=pdf_bytes,
        file_name="Rapport_Studio_SecureActe.pdf",
        mime="application/pdf"
    )
