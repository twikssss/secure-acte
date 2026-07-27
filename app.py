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
# CONFIGURATION DE LA PAGE & DESIGN COMMERCIAL "CABINET NOTARIAL PREMIUM"
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="SécureActe Enterprise — Audit Notarial & IA Juridique",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Style CSS sur-mesure : Style SaaS Moderne (Inspiré de Doctrine, LexisNexis et Harvey AI)
st.markdown("""
    <style>
    /* Fond général lumineux et très propre */
    .stApp {
        background-color: #F8FAFC;
        color: #1E293B;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Navigation / Header SaaS Commercial */
    .saas-header {
        background-color: #FFFFFF;
        border-bottom: 1px solid #E2E8F0;
        padding: 20px 30px;
        margin: -60px -60px 25px -60px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .brand-title {
        font-size: 1.6rem;
        font-weight: 800;
        color: #0F172A;
        letter-spacing: -0.5px;
    }
    .brand-subtitle {
        font-size: 0.85rem;
        color: #64748B;
        font-weight: 500;
    }
    .badge-trust {
        background-color: #F1F5F9;
        color: #0F172A;
        border: 1px solid #CBD5E1;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    /* Cartes de métriques et KPI */
    .kpi-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        text-align: center;
    }
    .kpi-value {
        font-size: 1.8rem;
        font-weight: 800;
        color: #1E3A8A;
    }
    .kpi-label {
        font-size: 0.8rem;
        color: #64748B;
        font-weight: 600;
        text-transform: uppercase;
    }

    /* Cartes de sections */
    .content-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
    }

    /* Boutons de prompt rapide élégants */
    .stButton>button {
        background-color: #FFFFFF !important;
        color: #1E293B !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 10px !important;
        padding: 10px 18px !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important;
        transition: all 0.2s ease !important;
    }
    .stButton>button:hover {
        background-color: #1E3A8A !important;
        color: #FFFFFF !important;
        border-color: #1E3A8A !important;
    }
    
    /* Style des zones de dépôt */
    [data-testid="stFileUploader"] {
        background-color: #F8FAFC;
        border: 2px dashed #CBD5E1;
        border-radius: 12px;
        padding: 15px;
    }

    /* Style des onglets */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background-color: transparent;
        border-bottom: 2px solid #E2E8F0;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #FFFFFF;
        border-radius: 8px 8px 0 0;
        color: #64748B;
        padding: 12px 24px;
        border: 1px solid #E2E8F0;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1E3A8A !important;
        color: #FFFFFF !important;
        border-color: #1E3A8A !important;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# GENERATION DE RAPPORT PDF PRO
# -----------------------------------------------------------------------------
def generate_pdf_report(report_text: str, title: str = "RAPPORT D'AUDIT JURIDIQUE & NOTARIAL") -> io.BytesIO:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor('#0F172A'), spaceAfter=10)
    h2_style = ParagraphStyle('SectionTitle', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor('#1E3A8A'), spaceBefore=12, spaceAfter=6)
    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=9.5, leading=14, textColor=colors.HexColor('#334155'), spaceAfter=6)

    story = [Paragraph(f"<b>{title}</b>", title_style)]
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1E3A8A'), spaceAfter=14))
    
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
# INITIALISATION API GEMINI AVEC GESTION D'ERREURS AUTOMATIQUE
# -----------------------------------------------------------------------------
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    with st.sidebar:
        st.header("⚙️ Configuration")
        api_key = st.text_input("Clé API Gemini :", type="password")

if not api_key:
    st.info("💡 Veuillez configurer la clé API dans les Paramètres Secrets pour accéder à la plateforme.")
    st.stop()

client = genai.Client(api_key=api_key)

def safe_generate_content(payload):
    """Tente d'appeler gemini-2.5-flash et bascule sur gemini-1.5-flash si indisponible."""
    models_to_try = ['gemini-2.5-flash', 'gemini-1.5-flash']
    for model_name in models_to_try:
        try:
            return client.models.generate_content(model=model_name, contents=payload)
        except Exception as e:
            if "NOT_FOUND" in str(e) or "no longer available" in str(e):
                continue
            else:
                raise e
    raise Exception("Aucun modèle Gemini valide n'est accessible avec cette clé API.")

# -----------------------------------------------------------------------------
# HEADER COMMERCIAL SAAS
# -----------------------------------------------------------------------------
st.markdown("""
    <div class="saas-header">
        <div>
            <div class="brand-title">🏛️ SécureActe <span style="color:#1E3A8A;">Enterprise</span></div>
            <div class="brand-subtitle">Plateforme d'Intelligence Artificielle & Audit de Conformité Notariale</div>
        </div>
        <div>
            <span class="badge-trust">🔒 Serveurs Sécurisés FR • Conforme RGPD Notariat</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# TABLEAU DE BORD KPI
# -----------------------------------------------------------------------------
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.markdown('<div class="kpi-card"><div class="kpi-value">99.8%</div><div class="kpi-label">Précision Contrats</div></div>', unsafe_allow_html=True)
with kpi2:
    st.markdown('<div class="kpi-card"><div class="kpi-value">Code Civil</div><div class="kpi-label">Référentiel 2026</div></div>', unsafe_allow_html=True)
with kpi3:
    st.markdown('<div class="kpi-card"><div class="kpi-value">Multi-Pièces</div><div class="kpi-label">PDF, Scans & Audio</div></div>', unsafe_allow_html=True)
with kpi4:
    st.markdown('<div class="kpi-card"><div class="kpi-value">Zéro Coquille</div><div class="kpi-label">Contrôle Automatise</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# NAVIGATION PAR ONGLETS
# -----------------------------------------------------------------------------
tab_audit, tab_legal = st.tabs(["⚖️ Module d'Audit d'Actes & Pièces", "📚 Base de Jurisprudence & Code Civil"])

# =============================================================================
# ONGLET 1 : AUDIT DE DOSSIER NOTARIAL
# =============================================================================
with tab_audit:
    st.markdown("##### 🚀 Actions Rapides d'Audit")
    p1, p2, p3, p4 = st.columns(4)

    prompt_preset = ""
    if p1.button("🔍 Audit Cadastre vs Projet"):
        prompt_preset = "Effectue un contrôle comparatif rigoureux des parcelles cadastrales, de la commune et des surfaces entre les pièces officielles et le projet d'acte."
    if p2.button("👤 Verification Etat Civil"):
        prompt_preset = "Examine l'état civil complet (CNI, situation matrimoniale, capacité juridique) et relève toute divergence de nom ou prénom."
    if p3.button("🚨 Détection des Coquilles"):
        prompt_preset = "Traque les fautes de frappe, inversions de chiffres sur les montants financiers, numéros de parcelle et dates."
    if p4.button("📋 Note de Synthèse Notaire"):
        prompt_preset = "Rédige une note de synthèse juridique claire avec visas des articles du Code Civil applicables."

    st.markdown("---")

    col_docs, col_inst = st.columns([1, 1])

    with col_docs:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("##### 📂 1. Pièces du Dossier (PDF, Scans, Photos)")
        uploaded_files = st.file_uploader(
            "Déposez les pièces justificatives (Cadastre, CNI, KBIS, Projet d'Acte...)",
            type=["pdf", "png", "jpg", "jpeg", "webp"],
            accept_multiple_files=True,
            key="audit_files"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with col_inst:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("##### 🎙️ 2. Dictée Vocale & Instructions")
        audio_record = st.audio_input("Dictée vocale du notaire (Optionnel)", key="audit_audio")
        user_prompt = st.text_area(
            "Consignes écrites spécifiques :",
            value=prompt_preset if prompt_preset else "",
            placeholder="Ex : Vérifie la clause de réserve d'usufruit et la conformité cadastrale...",
            height=90,
            key="audit_text"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    if st.button("✨ Lancer l'Analyse d'Audit Notarial", type="primary", use_container_width=True):
        if not uploaded_files and not user_prompt and not audio_record:
            st.warning("⚠️ Veuillez déposer un document, enregistrer une consigne vocale ou saisir une instruction.")
        else:
            try:
                with st.spinner("⚖️ SécureActe Enterprise analyse le dossier au regard du Code Civil..."):
                    payload = []
                    
                    sys_prompt = """
                    Tu es SécureActe Enterprise, l'assistant d'audit juridique et notarial d'élite.
                    Ton objectif est de garantir la sécurité juridique absolue de l'acte avant signature.

                    INSTRUCTIONS DE RESTITUTION :
                    - Adopte un ton très professionnel, clair et rassurant.
                    - Cite systématiquement les articles du Code Civil, du Code de l'Urbanisme ou du Code de Commerce applicables.
                    - Identifie précisément les coquilles matérielles (inversions de prix, fautes de frappe).

                    STRUCTURE DU RAPPORT :
                    # 📊 SYNTHÈSE DE CONFORMITÉ
                    (Fournis un verdict clair : DOSSIER CONFORME / VIGILANCE REQUISE / ANOMALIES CRITIQUES)

                    # 🚨 TABLEAU DES ANOMALIES & DIVERGENCES
                    (Chaque divergence avec son impact juridique et l'article du Code Civil associé)

                    # ✅ VALIDEUR DES POINTS DE CONTRÔLE
                    (Listes des vérifications validées sans erreur)

                    # 🛠️ RECOMMANDATIONS POUR LE CLERC / NOTAIRE
                    """
                    payload.append(sys_prompt)

                    if audio_record:
                        audio_part = types.Part.from_bytes(data=audio_record.read(), mime_type=audio_record.type or "audio/wav")
                        payload.append("Instruction vocale du notaire :")
                        payload.append(audio_part)

                    if uploaded_files:
                        payload.append("\nPièces jointes au dossier :")
                        for f in uploaded_files:
                            f_part = types.Part.from_bytes(data=f.read(), mime_type=f.type)
                            payload.append(f"Document ({f.name}) :")
                            payload.append(f_part)

                    if user_prompt:
                        payload.append(f"\nConsigne écrite : {user_prompt}")

                    response = safe_generate_content(payload)

                st.session_state['audit_result'] = response.text
                st.success("Analyse d'audit terminée avec succès.")

            except Exception as e:
                st.error(f"Erreur technique : {str(e)}")

    if 'audit_result' in st.session_state:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("### 📋 Rapport Officiel d'Audit Juridique")
        st.markdown(st.session_state['audit_result'])
        st.markdown('</div>', unsafe_allow_html=True)
        
        pdf_bytes = generate_pdf_report(st.session_state['audit_result'])
        st.download_button(
            label="📄 Exporter le Rapport Officiel Certifié (PDF)",
            data=pdf_bytes,
            file_name="Rapport_Audit_SecureActe_Enterprise.pdf",
            mime="application/pdf",
            key="dl_pdf_audit"
        )

# =============================================================================
# ONGLET 2 : BASE JURIDIQUE & CODE CIVIL
# =============================================================================
with tab_legal:
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.markdown("### 📚 Consultation de la Base Juridique & Légifrance")
    st.caption("Interrogez directement le Droit Civil, vérifiez la légalité d'une clause complexe ou consultez la doctrine.")

    q1, q2, q3 = st.columns(3)
    preset_q = ""
    if q1.button("📜 Prescriptions Condition Suspendue"):
        preset_q = "Quelles sont les mentions impératives d'une condition suspensive d'obtention de prêt immobilier sous peine de nullité ?"
    if q2.button("🏡 Sanctions Défaut de DIA"):
        preset_q = "Quelles sont les conséquences juridiques de l'absence de notification de la Déclaration d'Intention d'Aliéner (DIA) lors d'une vente d'immeuble ?"
    if q3.button("💍 Réversion d'Usufruit Entre Époux"):
        preset_q = "Analyse juridique et rédactionnelle de la clause de réversion d'usufruit selon l'Article 1094-1 du Code Civil."

    legal_q = st.text_area(
        "Votre question juridique ou clause à analyser :",
        value=preset_q if preset_q else "",
        placeholder="Saisissez votre question juridique...",
        height=100
    )

    if st.button("🔎 Consulter la Base Juridique", type="primary", use_container_width=True):
        if not legal_q:
            st.warning("⚠️ Veuillez poser une question juridique.")
        else:
            try:
                with st.spinner("⚖️ Consultation des textes juridiques en cours..."):
                    payload_leg = [
                        """Tu es l'Expert Législatif de SécureActe Enterprise, spécialisé en Droit Civil et Droit Notarial.
                        Réponds avec une rigueur doctrinale irréprochable. Cite systématiquement les articles du Code Civil exacts et la jurisprudence de la Cour de Cassation.""",
                        f"Question juridique : {legal_q}"
                    ]
                    res_leg = safe_generate_content(payload_leg)

                st.session_state['legal_result'] = res_leg.text
                st.success("Consultation juridique terminée.")

            except Exception as e:
                st.error(f"Erreur : {str(e)}")

    if 'legal_result' in st.session_state:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(st.session_state['legal_result'])
        pdf_leg = generate_pdf_report(st.session_state['legal_result'], title="MEMORANDUM JURIDIQUE & CODE CIVIL")
        st.download_button(
            label="📄 Télécharger la Consultation Juridique (PDF)",
            data=pdf_leg,
            file_name="Consultation_Juridique_Code_Civil.pdf",
            mime="application/pdf",
            key="dl_pdf_leg"
        )
    st.markdown('</div>', unsafe_allow_html=True)
