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
# CONFIGURATION DE LA PAGE & DESIGN COMMERCIAL SAAS
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="SécureActe Enterprise — Assistant Notarial Chat",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS pour une expérience Chat fluide & haut de gamme
st.markdown("""
    <style>
    .stApp {
        background-color: #F8FAFC;
        color: #1E293B;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* En-tête de la page */
    .saas-header {
        background-color: #FFFFFF;
        border-bottom: 1px solid #E2E8F0;
        padding: 15px 25px;
        margin: -60px -60px 20px -60px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .brand-title {
        font-size: 1.5rem;
        font-weight: 800;
        color: #0F172A;
    }
    .badge-trust {
        background-color: #F1F5F9;
        color: #0F172A;
        border: 1px solid #CBD5E1;
        padding: 5px 12px;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 600;
    }

    /* Style des bulles de Chat */
    [data-testid="stChatMessage"] {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 10px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.02);
    }

    /* Boutons d'action rapide */
    .stButton>button {
        background-color: #FFFFFF !important;
        color: #1E293B !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 8px !important;
        padding: 6px 14px !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }
    .stButton>button:hover {
        background-color: #1E3A8A !important;
        color: #FFFFFF !important;
        border-color: #1E3A8A !important;
    }
    
    /* Barre d'entrée du chat fixée */
    [data-testid="stChatInput"] {
        border-radius: 12px !important;
        border: 1px solid #CBD5E1 !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
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
    
    title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=15, textColor=colors.HexColor('#0F172A'), spaceAfter=10)
    h2_style = ParagraphStyle('SectionTitle', parent=styles['Heading2'], fontSize=11, textColor=colors.HexColor('#1E3A8A'), spaceBefore=10, spaceAfter=4)
    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=9, leading=13, textColor=colors.HexColor('#334155'), spaceAfter=5)

    story = [Paragraph(f"<b>{title}</b>", title_style)]
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#1E3A8A'), spaceAfter=12))
    
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
# INITIALISATION API GEMINI AVEC RETRY AUTOMATIQUE
# -----------------------------------------------------------------------------
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    with st.sidebar:
        st.header("⚙️ Clé API")
        api_key = st.text_input("Clé API Gemini :", type="password")

if not api_key:
    st.info("💡 Veuillez configurer la clé API dans les Paramètres Secrets pour démarrer.")
    st.stop()

client = genai.Client(api_key=api_key)

def safe_generate_content(payload):
    models_to_try = ['gemini-2.5-flash', 'gemini-1.5-flash']
    for model_name in models_to_try:
        try:
            return client.models.generate_content(model=model_name, contents=payload)
        except Exception as e:
            if "NOT_FOUND" in str(e) or "no longer available" in str(e):
                continue
            else:
                raise e
    raise Exception("Modèle d'IA indisponible pour le moment.")

# -----------------------------------------------------------------------------
# PANNEAU LATÉRAL : DÉPÔT DE DOCUMENTS ET CONTEXTE
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 📂 Pièces du Dossier")
    st.caption("Déposez vos documents une fois. Vous pourrez ensuite poser toutes vos questions dans le chat.")
    
    uploaded_files = st.file_uploader(
        "PDF, Scans CNI, Cadastre, Actes Word...",
        type=["pdf", "png", "jpg", "jpeg", "webp"],
        accept_multiple_files=True
    )
    
    st.markdown("---")
    st.markdown("### 🎙️ Dictée Vocale")
    audio_record = st.audio_input("Enregistrer une instruction vocale")
    
    if st.button("🗑️ Réinitialiser la discussion", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# -----------------------------------------------------------------------------
# HEADER PRINCIPAL
# -----------------------------------------------------------------------------
st.markdown("""
    <div class="saas-header">
        <div>
            <div class="brand-title">🏛️ SécureActe <span style="color:#1E3A8A;">Chat Assistant</span></div>
        </div>
        <div>
            <span class="badge-trust">🔒 Conforme RGPD & Code Civil</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# Initialisation de l'historique des messages
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Bonjour ! Je suis l'Assistant SécureActe. Posez-moi une question sur le Code Civil, ou déposez vos documents à gauche pour lancer un audit d'acte."
        }
    ]

# -----------------------------------------------------------------------------
# PROMPTS RAPIDES
# -----------------------------------------------------------------------------
st.markdown("##### 💡 Suggestions d'analyse instantanée")
q1, q2, q3, q4 = st.columns(4)

preset_query = ""
if q1.button("🔍 Contrôler le Cadastre"):
    preset_query = "Fais un contrôle complet des parcelles cadastrales entre les pièces officielles déposées et le projet d'acte."
if q2.button("👤 Vérifier l'État Civil"):
    preset_query = "Analyse l'état civil des parties (noms, prénoms, situation matrimoniale, CNI) et indique les erreurs s'il y en a."
if q3.button("🚨 Détecter les Coquilles"):
    preset_query = "Traque toutes les coquilles, erreurs de frappe et inversions de chiffres (montants, numéros de parcelle)."
if q4.button("📜 Prescriptions Prêt Immobilier"):
    preset_query = "Quelles sont les mentions légales obligatoires pour une condition suspensive de prêt selon le Code Civil et la loi ?"

# -----------------------------------------------------------------------------
# AFFICHAGE DE L'HISTORIQUE DES MESSAGES
# -----------------------------------------------------------------------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# -----------------------------------------------------------------------------
# ENTRÉE DE CHAT (Lancement automatique à l'appui sur Entrée !)
# -----------------------------------------------------------------------------
user_input = st.chat_input("Posez votre question juridique ou demandez un audit... (Appuyez sur Entrée pour envoyer)")

# Si l'utilisateur clique sur une suggestion ou tape un message
final_prompt = preset_query if preset_query else user_input

if final_prompt:
    # 1. Afficher la question de l'utilisateur
    st.session_state.messages.append({"role": "user", "content": final_prompt})
    with st.chat_message("user"):
        st.markdown(final_prompt)

    # 2. Préparation du payload pour Gemini
    with st.chat_message("assistant"):
        with st.spinner("⚖️ Recherche et analyse en cours..."):
            try:
                payload = []
                
                # Instruction système
                sys_prompt = """
                Tu es SécureActe Enterprise, l'assistant IA notarial d'élite.
                Réponds avec précision, clarté et professionnalisme.
                
                RÈGLES D'AUDIT & DE RÉPONSE :
                1. Si des documents sont joints, compare-les rigoureusement et relève la moindre coquille (inversion de chiffres, fautes de frappe sur les noms).
                2. Cite systématiquement les articles du Code Civil ou du Code de l'Urbanisme applicables.
                3. Propose des formulations exactes de correction pour le clerc de notaire.
                """
                payload.append(sys_prompt)

                # Ajout des fichiers déposés dans la barre latérale
                if uploaded_files:
                    payload.append("\n[DOCUMENTS DUS DOSSIER JOINTS] :")
                    for f in uploaded_files:
                        f_part = types.Part.from_bytes(data=f.getvalue(), mime_type=f.type)
                        payload.append(f"Fichier ({f.name}) :")
                        payload.append(f_part)

                # Ajout de l'audio si présent
                if audio_record:
                    audio_part = types.Part.from_bytes(data=audio_record.getvalue(), mime_type=audio_record.type or "audio/wav")
                    payload.append("Instruction vocale enregistrée :")
                    payload.append(audio_part)

                # Ajout du message de l'utilisateur
                payload.append(f"\nQuestion / Instruction de l'utilisateur : {final_prompt}")

                # Appel à l'IA
                response = safe_generate_content(payload)
                response_text = response.text

                # Affichage de la réponse
                st.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})

                # Proposer l'exportation PDF du dernier rapport généré
                pdf_bytes = generate_pdf_report(response_text)
                st.download_button(
                    label="📄 Télécharger cette réponse en PDF Officiel",
                    data=pdf_bytes,
                    file_name="Rapport_SecureActe.pdf",
                    mime="application/pdf"
                )

            except Exception as e:
                st.error(f"Désolé, une erreur est survenue : {str(e)}")
