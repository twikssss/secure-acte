import streamlit as st
from google import genai
from google.genai import types

# Configuration de l'interface
st.set_page_config(
    page_title="SécureActe IA - Audit Notarial",
    page_icon="⚖️",
    layout="wide"
)

# Style CSS personnalisé
st.markdown("""
    <style>
    .main-header { font-size: 2.3rem; color: #1E3A8A; font-weight: bold; }
    .stAlert { border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">⚖️ SécureActe IA — Contrôle d\'Acte Notarial</p>', unsafe_allow_html=True)
st.caption("Propulsé par Google Gemini 2.5 Flash • Analyse automatique multi-documents")
st.markdown("---")

# Récupération de la clé API (via Secrets Streamlit ou champ manuel)
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    with st.sidebar:
        st.warning("🔑 Clé API non configurée dans Secrets")
        api_key = st.text_input("Entrez votre clé API Gemini :", type="password")

if not api_key:
    st.info("👈 Veuillez ajouter votre clé API dans les paramètres Secrets de Streamlit ou dans le menu de gauche.")
    st.stop()

# Initialisation du client Gemini
client = genai.Client(api_key=api_key)

# Disposition en colonnes pour le dépôt des pièces
col1, col2 = st.columns(2)

with col1:
    st.subheader("📋 1. Documents Officiels de Référence")
    doc_ref = st.file_uploader(
        "Déposez les pièces officielles (Cadastre, Carte d'identité, Kbis...)",
        type=["pdf", "png", "jpg", "jpeg"],
        key="doc_ref"
    )

with col2:
    st.subheader("📄 2. Projet d'Acte à Contrôler")
    doc_acte = st.file_uploader(
        "Déposez le projet d'acte rédigé (Word/PDF)",
        type=["pdf", "png", "jpg", "jpeg"],
        key="doc_acte"
    )

# Options avancées d'audit
with st.expander("⚙️ Options avancées du contrôle"):
    type_acte = st.selectbox(
        "Type de dossier",
        ["Vente Immobilière", "Donation", "Succession", "Droit des Sociétés / Cession"]
    )
    rigueur = st.select_slider(
        "Niveau d'exigence de l'IA",
        options=["Standard", "Haute Rigueur (Notarial)", "Tolérance Zéro Coquille"]
    )

st.markdown("---")

# Prompt système ultra-spécifique pour clerc de notaire
SYSTEM_PROMPT = f"""
Tu es un Moteur d'IA expert en Audit Notarial Droit Français, agissant comme un clerc de notaire senior ultra-rigoureux.
Ton objectif est de comparer minutieusement le 'Document Officiel de Référence' avec le 'Projet d'Acte'.

Type de dossier : {type_acte}
Niveau d'exigence : {rigueur}

Effectue une analyse comparative exhaustive sur les points suivants :
1. **État Civil & Identités** (Noms, prénoms, dates/lieux de naissance, régimes matrimoniaux, adresses).
2. **Désignation Cadastrale & Immobilière** (Commune, Section, Numéro de parcelle, contenance/surface).
3. **Éléments Financiers** (Prix en chiffres et en lettres, modalités de paiement, honoraires).
4. **Coquilles & Typographie** (Inversions de chiffres, fautes de frappe sur les noms propres).

Format ta réponse en Markdown très structuré :
- 🚦 **RÉSUMÉ EXÉCUTIF** : Statut global (CONFORME, ATTENTION, ou RISQUE CRITIQUE).
- 🚨 **INCOHÉRENCES DÉTECTÉES** (Sous forme de tableau : Élément | Doc Officiel | Projet d'Acte | Gravité).
- ✅ **ÉLÉMENTS CONFORMES** (Liste à puces des points validés).
- 💡 **RECOMMANDATIONS DE CORRECTION** pour le clerc/notaire.
"""

# Bouton de lancement de l'analyse
if st.button("🚀 Lancer le Contrôle d'IA", type="primary", use_container_width=True):
    if doc_ref and doc_acte:
        try:
            with st.spinner("🔍 Analyse comparative approfondie en cours par Gemini 2.5 Flash..."):
                
                # Préparation des fichiers PDF/Images pour l'API Gemini
                part_ref = types.Part.from_bytes(
                    data=doc_ref.read(),
                    mime_type=doc_ref.type
                )
                
                part_acte = types.Part.from_bytes(
                    data=doc_acte.read(),
                    mime_type=doc_acte.type
                )
                
                # Appel de l'IA multimodale
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=[
                        SYSTEM_PROMPT,
                        "Voici le document officiel de référence :", part_ref,
                        "Voici le projet d'acte à vérifier :", part_acte
                    ]
                )

            # Affichage du rapport
            st.success("Analyse terminée avec succès !")
            st.markdown("### 📊 Rapport d'Audit Notarial")
            st.markdown(response.text)
            
            # Bouton pour télécharger le rapport au format texte
            st.download_button(
                label="📥 Télécharger le rapport (TXT)",
                data=response.text,
                file_name="rapport_audit_notarial.txt",
                mime="text/plain"
            )

        except Exception as e:
            st.error(f"❌ Une erreur est survenue lors de l'analyse : {str(e)}")
    else:
        st.warning("⚠️ Veuillez déposer simultanément le document officiel ET le projet d'acte pour pouvoir lancer la comparaison.")
