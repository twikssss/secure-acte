import io
import streamlit as st
from google import genai
from google.genai import types

# Bibliothèques pour la génération du PDF
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# -----------------------------------------------------------------------------
# CONFIGURATION DE LA PAGE
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="SécureActe Pro - Audit Notarial Bionique",
    page_icon="⚖️",
    layout="wide"
)

st.markdown("""
    <style>
    .main-title { font-size: 2.3rem; color: #1E3A8A; font-weight: 800; }
    .sub-title { font-size: 1rem; color: #4B5563; margin-bottom: 20px; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">⚖️ SécureActe Pro</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Audit juridique automatique & contrôle de conformité multi-pièces</p>', unsafe_allow_html=True)
st.markdown("---")

# -----------------------------------------------------------------------------
# FONCTION DE GÉNÉRATION DU RAPPORT PDF
# -----------------------------------------------------------------------------
def generate_pdf_report(report_text: str) -> io.BytesIO:
    """Transforme le texte du rapport en un document PDF professionnel."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    
    # Styles personnalisés pour le document PDF
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1E3A8A'),
        spaceAfter=10
    )
    
    h2_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=13,
        textColor=colors.HexColor('#1E3A8A'),
        spaceBefore=12,
        spaceAfter=6
    )
    
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#1F2937'),
        spaceAfter=6
    )

    story = []
    
    # En-tête du PDF
    story.append(Paragraph("<b>SÉCUREACTE PRO — RAPPORT D'AUDIT NOTARIAL</b>", title_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1E3A8A'), spaceAfter=15))
    
    # Conversion du texte Markdown simple en paragraphes PDF
    lines = report_text.split('\n')
    for line in lines:
        clean_line = line.strip().replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        
        if not clean_line:
            continue
            
        if clean_line.startswith('# '):
            story.append(Paragraph(f"<b>{clean_line[2:]}</b>", h2_style))
        elif clean_line.startswith('## ') or clean_line.startswith('### '):
            text_head = clean_line.lstrip('#').strip()
            story.append(Paragraph(f"<b>{text_head}</b>", h2_style))
        elif clean_line.startswith('- ') or clean_line.startswith('* '):
            story.append(Paragraph(f"• {clean_line[2:]}", body_style))
        else:
            story.append(Paragraph(clean_line, body_style))
            
    doc.build(story)
    buffer.seek(0)
    return buffer

# -----------------------------------------------------------------------------
# GESTION DE LA CLÉ API
# -----------------------------------------------------------------------------
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    with st.sidebar:
        st.header("🔑 Configuration")
        api_key = st.text_input("Clé API Gemini :", type="password")

if not api_key:
    st.info("👈 Veuillez configurer votre clé API Gemini dans le menu latéral ou dans les Secrets Streamlit pour commencer.")
    st.stop()

client = genai.Client(api_key=api_key)

# -----------------------------------------------------------------------------
# INTERFACE SÉLECTION DES DOCUMENTS
# -----------------------------------------------------------------------------
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("📂 1. Dossier de Référence (Pièces Officielle)")
    docs_ref = st.file_uploader(
        "Déposez les pièces justificatives (Cadastre, CNI, KBIS...)",
        type=["pdf", "png", "jpg", "jpeg"],
        accept_multiple_files=True,
        key="docs_ref"
    )

with col_right:
    st.subheader("📄 2. Projet d'Acte à Vérifier")
    doc_acte = st.file_uploader(
        "Déposez le projet d'acte rédigé (Word/PDF)",
        type=["pdf", "png", "jpg", "jpeg"],
        key="doc_acte"
    )

# -----------------------------------------------------------------------------
# CHECKLIST & PARAMÈTRES JURIDIQUES
# -----------------------------------------------------------------------------
st.markdown("### 🎯 Périmètre de l'Audit")
c1, c2, c3 = st.columns(3)

with c1:
    check_etat_civil = st.checkbox("État civil & Matrimonial", value=True)
    check_cadastre = st.checkbox("Désignation Cadastrale", value=True)
with c2:
    check_prix = st.checkbox("Prix & Financement", value=True)
    check_servitudes = st.checkbox("Servitudes & Urbanisme", value=False)
with c3:
    check_typo = st.checkbox("Coquilles / Inversions de chiffres", value=True)

st.markdown("---")

# -----------------------------------------------------------------------------
# EXECUTION ET AFFICHAGE
# -----------------------------------------------------------------------------
if st.button("🚀 Lancer l'Audit & Générer le PDF", type="primary"):
    if docs_ref and doc_acte:
        try:
            with st.spinner("🧠 Analyse en cours par Gemini 2.5 Flash..."):
                contents_payload = []
                
                prompt_consignes = f"""
                Tu es un clerc de notaire senior ultra-rigoureux.
                Compare les DOCUMENTS DE RÉFÉRENCE au PROJET D'ACTE.

                POINTS D'INSPECTION :
                - État civil : {check_etat_civil}
                - Cadastre : {check_cadastre}
                - Prix : {check_prix}
                - Servitudes : {check_servitudes}
                - Coquilles : {check_typo}

                FORMAT DE RESTITUTION EXIGÉ :
                # BILAN GLOBAL DE CONFORMITÉ
                (Verdict : CONFORME / ATTENTION REQUISE / ANOMALIE CRITIQUE)

                # ANOMALIES & DIVERGENCES DÉTECTÉES
                - Liste claire de chaque divergence trouvée avec sa gravité.

                # ÉLÉMENTS CONFORMES
                - Liste des points validés.

                # ACTIONS CORRECTIVES POUR LE CLERC
                - Corrections exactes à effectuer.
                """
                contents_payload.append(prompt_consignes)

                for doc in docs_ref:
                    part = types.Part.from_bytes(data=doc.read(), mime_type=doc.type)
                    contents_payload.append(f"Pièce officielle ({doc.name}) :")
                    contents_payload.append(part)

                part_acte = types.Part.from_bytes(data=doc_acte.read(), mime_type=doc_acte.type)
                contents_payload.append(f"Projet d'acte ({doc_acte.name}) :")
                contents_payload.append(part_acte)

                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=contents_payload
                )

            # Stockage du résultat dans la session
            st.session_state['report_text'] = response.text
            st.success("Audit terminé avec succès !")

        except Exception as e:
            st.error(f"Erreur technique : {str(e)}")
    else:
        st.warning("⚠️ Veuillez déposer au moins une pièce de référence et le projet d'acte.")

# Si un rapport a été généré, on l'affiche et on propose le téléchargement
if 'report_text' in st.session_state:
    st.markdown("### 📊 Rapport d'Audit")
    st.markdown(st.session_state['report_text'])
    
    # Génération du fichier PDF
    pdf_bytes = generate_pdf_report(st.session_state['report_text'])
    
    st.download_button(
        label="📄 Télécharger le Rapport Officiel (Format PDF)",
        data=pdf_bytes,
        file_name="Rapport_Audit_Notarial_SecureActe.pdf",
        mime="application/pdf"
    )
