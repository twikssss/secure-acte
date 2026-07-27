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
    page_title="SécureActe Studio — Droit & Audit Notarial",
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
        padding: 15px 0px 5px 0px;
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
    
    /* Boutons de prompt rapide */
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
    
    /* Zone de dépôt */
    [data-testid="stFileUploader"] {
        background-color: #14141a;
        border: 1px dashed #2e2e38;
        border-radius: 12px;
        padding: 15px;
    }
    
    /* Entrées audio et texte */
    [data-testid="stAudioInput"], .stTextArea textarea, .stTextInput input {
        background-color: #14141a !important;
        color: #ffffff !important;
        border-radius: 12px !important;
        border: 1px solid #2e2e38 !important;
    }
    
    /* Style des Onglets */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background-color: #0d0d11;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #14141a;
        border-radius: 10px;
        color: #8e8e93;
        padding: 10px 20px;
        border: 1px solid #2e2e38;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2a2a35 !important;
        color: #ffffff !important;
        border-color: #ffffff !important;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# GÉNÉRATION DE RAPPORT PDF
# -----------------------------------------------------------------------------
def generate_pdf_report(report_text: str, title: str = "RAPPORT D'AUDIT JURIDIQUE SÉCUREACTE STUDIO") -> io.BytesIO:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=15, textColor=colors.HexColor('#000000'), spaceAfter=10)
    h2_style = ParagraphStyle('SectionTitle', parent=styles['Heading2'], fontSize=11, textColor=colors.HexColor('#1a1a1a'), spaceBefore=10, spaceAfter=4)
    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=9, leading=13, textColor=colors.HexColor('#2b2b2b'), spaceAfter=5)

    story = [Paragraph(f"<b>{title}</b>", title_style)]
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
# INITIALISATION API GEMINI
# -----------------------------------------------------------------------------
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    with st.sidebar:
        api_key = st.text_input("Clé API Gemini :", type="password")

if not api_key:
    st.info("💡 Veuillez configurer votre clé API Gemini dans les Secrets Streamlit pour utiliser le Studio.")
    st.stop()

client = genai.Client(api_key=api_key)

# -----------------------------------------------------------------------------
# EN-TÊTE PRINCIPAL
# -----------------------------------------------------------------------------
st.markdown("""
    <div class="title-container">
        <div class="main-title">SécureActe Studio</div>
        <div class="sub-title">Intelligence Artificielle Notariale • Analyse Multi-Pièces & Base du Code Civil</div>
    </div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# NAVIGATION PAR ONGLETS (STUDIO)
# -----------------------------------------------------------------------------
tab_audit, tab_legal_db = st.tabs(["⚖️ Audit d'Acte & Multimodal", "📚 Base de Données Juridique & Code Civil"])

# =============================================================================
# ONGLET 1 : AUDIT MULTIMODAL (PDF, PHOTOS, VOCAL, PROMPTS)
# =============================================================================
with tab_audit:
    st.markdown("##### 💡 Suggestions d'analyse rapide")
    p_col1, p_col2, p_col3, p_col4 = st.columns(4)

    selected_prompt_preset = ""
    if p_col1.button("🔍 Audit Cadastre vs Acte"):
        selected_prompt_preset = "Effectue une comparaison ultra-rigoureuse entre la désignation cadastrale des pièces officielles et du projet d'acte, au regard des règles du droit de la propriété."
    if p_col2.button("👤 Conformité État Civil"):
        selected_prompt_preset = "Contrôle l'état civil complet (CNI, mariage, régimes matrimoniaux) et vérifie la capacité juridique des parties selon le Code Civil."
    if p_col3.button("🚨 Contrôle des Coquilles & Chiffres"):
        selected_prompt_preset = "Repère toutes les coquilles, inversions de chiffres (prix, surface, numéros de parcelle) et erreurs d'orthographe."
    if p_col4.button("📋 Note de Synthèse Notaire"):
        selected_prompt_preset = "Rédige une note de synthèse juridique complète avec visas des articles du Code Civil applicables."

    st.markdown("---")

    col_files, col_input = st.columns([1, 1])

    with col_files:
        st.markdown("##### 📂 Documents, Scans & Photos")
        uploaded_files = st.file_uploader(
            "Déposez vos pièces (PDF, Photos CNI, Cadastre, Actes manuscrits...)",
            type=["pdf", "png", "jpg", "jpeg", "webp"],
            accept_multiple_files=True,
            key="audit_uploader"
        )

    with col_input:
        st.markdown("##### 🎙️ Consigne Vocale & Instructions Écrites")
        audio_record = st.audio_input("Dictée vocale des consignes (Optionnel)", key="audit_audio")
        user_text_prompt = st.text_area(
            "Instructions spécifiques pour l'IA :",
            value=selected_prompt_preset if selected_prompt_preset else "",
            placeholder="Posez votre question ou décrivez ce que l'IA doit vérifier...",
            height=100,
            key="audit_text"
        )

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("✨ Lancer l'Audit Multimodal & Juridique", type="primary", use_container_width=True, key="btn_audit"):
        if not uploaded_files and not user_text_prompt and not audio_record:
            st.warning("⚠️ Veuillez joindre un document, enregistrer un message vocal ou saisir une instruction.")
        else:
            try:
                with st.spinner("🧠 Analyse en cours par Gemini 2.5 Flash avec référentiel Code Civil..."):
                    payload = []
                    
                    system_prompt_audit = """
                    Tu es SécureActe Studio, Moteur d'IA Senior spécialisé en Droit Notarial et Droit Civil Français.
                    Ton rôle est d'analyser les pièces fournies (fichiers, photos, audio, textes) avec la rigueur d'un docteur en droit.

                    CONSIGNES OBLIGATOIRES :
                    1. Effectue un contrôle de conformité textuel et juridique.
                    2. CITE TOUJOURS LES ARTICLES DU CODE CIVIL OU DU CODE DE L'URBANISME APPLICABLES lorsque tu relèves une anomalie ou une clause à haut risque.
                    3. Signale les erreurs matérielles (prix, orthographe des noms, dates, références cadastrales).

                    STRUCTURE DU RAPPORT :
                    # 🚦 VERDICT GLOBAL & CONFORMITÉ
                    # 🚨 ANOMALIES, COQUILLES & RISQUES JURIDIQUES (avec visés des articles du Code Civil)
                    # ✅ POINTS CONFORMES VALIDÉS
                    # 🛠️ RECOMMANDATIONS EXACTES POUR LE CLERC / NOTAIRE
                    """
                    payload.append(system_prompt_audit)

                    if audio_record:
                        audio_part = types.Part.from_bytes(data=audio_record.read(), mime_type=audio_record.type or "audio/wav")
                        payload.append("Instruction vocale enregistrée par l'utilisateur :")
                        payload.append(audio_part)

                    if uploaded_files:
                        payload.append("\nDocuments et visuels joints :")
                        for file in uploaded_files:
                            file_part = types.Part.from_bytes(data=file.read(), mime_type=file.type)
                            payload.append(f"Pièce jointe ({file.name}) :")
                            payload.append(file_part)

                    if user_text_prompt:
                        payload.append(f"\nConsigne écrite : {user_text_prompt}")

                    response = client.models.generate_content(model='gemini-2.5-flash', contents=payload)

                st.session_state['audit_response'] = response.text
                st.success("Audit terminé avec succès !")

            except Exception as e:
                st.error(f"Erreur d'analyse : {str(e)}")

    if 'audit_response' in st.session_state:
        st.markdown("---")
        st.markdown("### 📊 Rapport d'Audit & Visas Juridiques")
        st.markdown(st.session_state['audit_response'])
        
        pdf_bytes = generate_pdf_report(st.session_state['audit_response'], title="RAPPORT D'AUDIT JURIDIQUE & NOTARIAL")
        st.download_button(
            label="📄 Télécharger le Rapport Officiel (PDF)",
            data=pdf_bytes,
            file_name="Rapport_Audit_SecureActe.pdf",
            mime="application/pdf",
            key="dl_audit_pdf"
        )

# =============================================================================
# ONGLET 2 : BASE DE DONNÉES JURIDIQUE & CODE CIVIL
# =============================================================================
with tab_legal_db:
    st.markdown("### 📚 Consultation de la Base Juridique (Code Civil & Doctrine)")
    st.caption("Interrogez directement le Droit Français, vérifiez la légalité d'une clause ou recherchez des jurisprudences.")

    # Exemples de questions juridiques notariales
    st.markdown("##### 💡 Requêtes juridiques récurrentes")
    q_col1, q_col2, q_col3 = st.columns(3)
    
    selected_legal_q = ""
    if q_col1.button("📜 Condition suspensive d'obtention de prêt"):
        selected_legal_q = "Quelles sont les mentions obligatoires d'une condition suspensive de prêt immobilier selon le Code de la Consommation (Art. L. 313-41) et la jurisprudence récente ?"
    if q_col2.button("🏡 Purge du droit de préemption urbain (DPU)"):
        selected_legal_q = "Quelles sont les sanctions légales et jurisprudentielles en cas de défaut de notification de la DIA à la commune avant une vente immobilière ?"
    if q_col3.button("💍 Donation entre époux & Réversion d'usufruit"):
        selected_legal_q = "Analyse juridique de la réversion d'usufruit au profit du conjoint survivant : fiscalité, articles du Code Civil applicables (Art. 1094-1) et rédaction recommandée."

    col_search, col_doc_law = st.columns([1.2, 0.8])

    with col_search:
        legal_query = st.text_area(
            "Saisissez votre question juridique ou collez une clause pour analyse :",
            value=selected_legal_q if selected_legal_q else "",
            placeholder="Ex : Analyse la validité de la clause de tontine face au droit des successions et à la réserve héréditaire (Art. 912 Code Civil)...",
            height=140,
            key="legal_query_input"
        )

    with col_doc_law:
        st.markdown("##### 📎 Support Juridique / Doctrine Personnalisée")
        legal_ref_files = st.file_uploader(
            "Joignez vos textes de doctrine (PDF, Arrêts de la C.Cass, Guides CRIDON...)",
            type=["pdf", "png", "jpg"],
            accept_multiple_files=True,
            key="legal_ref_uploader"
        )

    if st.button("🔎 Interroger la Base Juridique & le Code Civil", type="primary", use_container_width=True, key="btn_legal"):
        if not legal_query and not legal_ref_files:
            st.warning("⚠️ Veuillez poser une question juridique ou télécharger un document de doctrine.")
        else:
            try:
                with st.spinner("⚖️ Consultation des articles du Code Civil et des textes juridiques en cours..."):
                    legal_payload = []
                    
                    system_prompt_legal = """
                    Tu es un Juriste Senior et Docteur en Droit Notarial, expert incontesté du CODE CIVIL FRANÇAIS, du Code de l'Urbanisme, du Code de la Construction et de la jurisprudence Légifrance.

                    MISSION :
                    Répondre à la consultation juridique formulée avec une précision doctrinale absolue.

                    EXIGENCES DE RESTITUTION :
                    1. **VISAS DES TEXTES DE LOI** : Cite TOUJOURS les numéros d'articles précis du Code Civil (ex: Art. 1101, Art. 1582, Art. 544, Art. 912) et autres codes concernés.
                    2. **JURISPRUDENCE** : Fais référence aux principes arrêtés par la Cour de Cassation (Chambre Civile).
                    3. **ANALYSE PRATIQUE NOTARIALE** : Donne une conclusion claire sur la faisabilité juridique et propose une rédaction sécurisée de clause si demandé.
                    """
                    legal_payload.append(system_prompt_legal)

                    if legal_ref_files:
                        legal_payload.append("\nTextes juridiques / Doctrine transmis par le notaire :")
                        for ref_file in legal_ref_files:
                            ref_part = types.Part.from_bytes(data=ref_file.read(), mime_type=ref_file.type)
                            legal_payload.append(f"Document de référence ({ref_file.name}) :")
                            legal_payload.append(ref_part)

                    if legal_query:
                        legal_payload.append(f"\nQuestion juridique / Clause à analyser : {legal_query}")

                    response_legal = client.models.generate_content(model='gemini-2.5-flash', contents=legal_payload)

                st.session_state['legal_response'] = response_legal.text
                st.success("Consultation juridique terminée !")

            except Exception as e:
                st.error(f"Erreur lors de la recherche juridique : {str(e)}")

    if 'legal_response' in st.session_state:
        st.markdown("---")
        st.markdown("### 🏛️ Mémorandum Juridique & Visas Légifrance")
        st.markdown(st.session_state['legal_response'])
        
        pdf_bytes_legal = generate_pdf_report(st.session_state['legal_response'], title="CONSULTATION JURIDIQUE & CODE CIVIL — SÉCUREACTE")
        st.download_button(
            label="📄 Imprimer la Consultation Juridique (PDF)",
            data=pdf_bytes_legal,
            file_name="Consultation_Juridique_Code_Civil.pdf",
            mime="application/pdf",
            key="dl_legal_pdf"
        )
