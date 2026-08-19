"""
Application de Vérification d'AVI - Version Optimisée
Permet de vérifier les informations d'une AVI en entrant sa référence
"""

import streamlit as st
import mysql.connector
from datetime import datetime
import logging
from functools import lru_cache
import time

# Configuration de la page
st.set_page_config(
    page_title="Vérificateur AVI - Eco Capital",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration de la base de données
MYSQL_CONFIG = {
    'host': 'ecocapital-mbfdm.c.aivencloud.com',
    'user': 'avnadmin',
    'password': 'AVNS_3a2plzaevzttmJ4Tcs9',
    'database': 'ecocapital',
    'port': 14431,
    'connect_timeout': 10,  # Timeout de connexion réduit
    'pool_name': 'aviconnectionpool',
    'pool_size': 1,  # Une seule connexion
    'pool_reset_session': True,
}

# Configuration du logging
logging.basicConfig(level=logging.ERROR)  # Réduit les logs pour économiser CPU
logger = logging.getLogger(__name__)

# Cache pour les connexions à la base de données
@st.cache_resource
def get_db_connection():
    """Établit une connexion à la base de données MySQL avec cache"""
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        return conn
    except mysql.connector.Error as err:
        logger.error(f"Erreur de connexion à MySQL: {err}")
        return None

# Cache pour la vérification de la base de données - fait une seule fois
@st.cache_resource
def check_database():
    """Vérifie que la base de données existe - exécuté une seule fois"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM avis LIMIT 1")
        cursor.close()
        return True
    except:
        return False

@st.cache_data(ttl=3600)  # Cache pendant 1 heure
def verify_avi_cached(reference: str):
    """
    Vérifie une AVI par sa référence - Version avec cache
    """
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Requête optimisée avec UNION pour chercher dans les deux tables en une seule fois
        query = """
        SELECT 
            reference,
            nom_complet,
            code_banque,
            numero_compte,
            devise,
            iban,
            bic,
            montant,
            date_creation,
            date_expiration,
            statut,
            commentaires,
            'avis' as source
        FROM avis 
        WHERE reference = %s
        UNION ALL
        SELECT 
            reference,
            nom_complet,
            code_banque,
            numero_compte,
            devise,
            iban,
            bic,
            montant,
            date_creation,
            date_expiration,
            statut,
            commentaires,
            'info_avi' as source
        FROM info_avi 
        WHERE reference = %s
        LIMIT 1
        """
        
        cursor.execute(query, (reference.strip(), reference.strip()))
        result = cursor.fetchone()
        
        cursor.close()
        return result
        
    except mysql.connector.Error as e:
        logger.error(f"Erreur lors de la vérification: {str(e)}")
        return None

def format_iban(iban):
    """Formate un IBAN pour l'affichage (espaces tous les 4 caractères)"""
    if not iban:
        return iban
    iban_clean = iban.replace(' ', '')
    return ' '.join([iban_clean[i:i+4] for i in range(0, len(iban_clean), 4)])

def format_montant(montant, devise="XAF"):
    """Formate le montant avec la devise"""
    if not montant:
        return "0 FCFA"
    try:
        return f"{float(montant):,.2f} {devise}"
    except:
        return f"{montant} {devise}"

def format_date(date_value):
    """Formate une date pour l'affichage"""
    if not date_value:
        return "Non définie"
    if isinstance(date_value, datetime):
        return date_value.strftime('%d/%m/%Y')
    if isinstance(date_value, str):
        try:
            date_obj = datetime.strptime(date_value, '%Y-%m-%d')
            return date_obj.strftime('%d/%m/%Y')
        except ValueError:
            return date_value
    return str(date_value)

def display_avi_result(result):
    """Affiche les résultats de la vérification"""
    if not result:
        return
    
    # Badge de vérification
    st.markdown("""
    <div style="text-align: center; margin: 1rem 0;">
        <span class="verification-badge">✅ AVI VALIDE</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Carte des résultats
    st.markdown('<div class="result-card">', unsafe_allow_html=True)
    
    st.markdown("### 📄 Informations de l'AVI")
    
    # Informations principales
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="info-item">
            <span class="info-label">📌 Référence</span>
            <span class="info-value">{result.get('reference', 'N/A')}</span>
        </div>
        <div class="info-item">
            <span class="info-label">👤 Nom complet</span>
            <span class="info-value">{result.get('nom_complet', 'N/A')}</span>
        </div>
        <div class="info-item">
            <span class="info-label">🏦 Code Banque</span>
            <span class="info-value">{result.get('code_banque', 'N/A')}</span>
        </div>
        <div class="info-item">
            <span class="info-label">🔢 Numéro de Compte</span>
            <span class="info-value">{result.get('numero_compte', 'N/A')}</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="info-item">
            <span class="info-label">💱 Devise</span>
            <span class="info-value">{result.get('devise', 'XAF')}</span>
        </div>
        <div class="info-item">
            <span class="info-label">🔑 IBAN</span>
            <span class="info-value" style="font-family: monospace;">{format_iban(result.get('iban', 'N/A'))}</span>
        </div>
        <div class="info-item">
            <span class="info-label">🌐 BIC</span>
            <span class="info-value" style="font-family: monospace;">{result.get('bic', 'N/A')}</span>
        </div>
        <div class="info-item">
            <span class="info-label">💰 Montant</span>
            <span class="info-value" style="font-weight: 700; color: #28a745;">{format_montant(result.get('montant'), result.get('devise', 'XAF'))}</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Informations supplémentaires
    col1, col2, col3 = st.columns(3)
    
    with col1:
        date_creation = result.get('date_creation')
        date_creation_display = format_date(date_creation)
        st.metric(
            "📅 Date de création",
            date_creation_display
        )
    
    with col2:
        date_expiration = result.get('date_expiration')
        date_expiration_display = format_date(date_expiration) if date_expiration else 'Non définie'
        st.metric(
            "📅 Date d'expiration",
            date_expiration_display
        )
    
    with col3:
        statut = result.get('statut', 'N/A')
        statut_class = "status-valid" if statut in ["Etudiant", "Fonctionnaire"] else "status-invalid"
        st.markdown(f"""
        <div style="text-align: center;">
            <span style="font-size: 0.9rem; color: #666;">📋 Statut</span>
            <br>
            <span class="{statut_class}">{statut}</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Commentaires si présents
    if result.get('commentaires'):
        st.markdown(f"""
        <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; margin-top: 1rem;">
            <strong>📝 Commentaires:</strong>
            <p style="margin: 0.5rem 0 0 0;">{result.get('commentaires')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Pied de page du résultat
    st.markdown(f"""
    <div style="text-align: center; margin-top: 1.5rem; color: #888; font-size: 0.85rem;">
        Vérifié le {datetime.now().strftime('%d/%m/%Y à %H:%M')} · Document certifié par Eco Capital
    </div>
    """, unsafe_allow_html=True)

# CSS personnalisé - chargé une seule fois
@st.cache_data
def load_css():
    return """
    <style>
        .main-container {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 15px;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .main-container h1 {
            margin: 0;
            font-size: 2.5rem;
        }
        
        .main-container p {
            margin: 0.5rem 0 0 0;
            opacity: 0.9;
        }
        
        .result-card {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            margin-top: 1.5rem;
        }
        
        .info-item {
            display: flex;
            justify-content: space-between;
            padding: 0.75rem 0;
            border-bottom: 1px solid #eee;
        }
        
        .info-item:last-child {
            border-bottom: none;
        }
        
        .info-label {
            font-weight: 600;
            color: #555;
        }
        
        .info-value {
            color: #333;
            font-weight: 500;
        }
        
        .status-valid {
            background: #28a745;
            color: white;
            padding: 0.25rem 1rem;
            border-radius: 20px;
            font-weight: 600;
            display: inline-block;
        }
        
        .status-invalid {
            background: #dc3545;
            color: white;
            padding: 0.25rem 1rem;
            border-radius: 20px;
            font-weight: 600;
            display: inline-block;
        }
        
        .verification-badge {
            background: #ffc107;
            color: #333;
            padding: 0.5rem 1.5rem;
            border-radius: 30px;
            font-weight: 700;
            display: inline-block;
            font-size: 0.9rem;
        }

        .stTextInput > div > div > input {
            font-size: 1.1rem;
            padding: 0.75rem 1rem;
        }
    </style>
    """

def main():
    """Point d'entrée principal - Version optimisée"""
    
    # Chargement CSS une seule fois
    st.markdown(load_css(), unsafe_allow_html=True)
    
    # Vérification rapide de la base de données (une seule fois)
    db_ok = check_database()
    if not db_ok:
        st.warning("⚠️ Problème avec la base de données. Veuillez réessayer plus tard.")
        st.stop()
    
    # En-tête
    st.markdown("""
    <div class="main-container">
        <h1>🔍 Vérificateur d'AVI</h1>
        <p>Entrez la référence de l'AVI pour vérifier son authenticité</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Section de recherche
    st.markdown("### 📝 Recherche par référence")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        reference = st.text_input(
            "Référence de l'AVI",
            placeholder="Ex: AVI-20260119-1234",
            label_visibility="collapsed"
        )
        
        # Bouton de vérification avec gestion du throttling
        if st.button("🔍 Vérifier", type="primary", use_container_width=True):
            if not reference or not reference.strip():
                st.warning("⚠️ Veuillez entrer une référence d'AVI")
            else:
                # Simuler un délai pour éviter les requêtes trop fréquentes
                if 'last_request' not in st.session_state:
                    st.session_state.last_request = 0
                
                current_time = time.time()
                if current_time - st.session_state.last_request < 2:
                    st.warning("⏳ Veuillez attendre 2 secondes entre chaque vérification")
                else:
                    st.session_state.last_request = current_time
                    
                    with st.spinner("Vérification en cours..."):
                        result = verify_avi_cached(reference)
                        
                        if result:
                            st.markdown("---")
                            display_avi_result(result)
                        else:
                            st.markdown("---")
                            st.markdown("""
                            <div style="text-align: center; padding: 2rem; background: #fff3cd; border-radius: 10px; border: 1px solid #ffc107;">
                                <h3 style="color: #856404;">❌ AVI non trouvée</h3>
                                <p style="color: #856404;">Aucune attestation trouvée avec la référence <strong>{}</strong></p>
                                <p style="color: #856404; font-size: 0.9rem;">Vérifiez que la référence est correcte (format: AVI-YYYYMMDD-XXXX)</p>
                            </div>
                            """.format(reference.strip()), unsafe_allow_html=True)
    
    # Section d'information - Chargée une seule fois
    with st.expander("ℹ️ Comment utiliser le vérificateur", expanded=False):
        st.markdown("""
        **Instructions :**
        
        1. Entrez la **référence complète** de l'AVI dans le champ de recherche
        2. Cliquez sur le bouton **"Vérifier"**
        3. Les informations de l'AVI s'afficheront si elles existent dans la base de données
        
        **Format de référence attendu :** `AVI-YYYYMMDD-XXXX`
        - YYYYMMDD : Date de création (Année/Mois/Jour)
        - XXXX : Numéro aléatoire à 4 chiffres
        
        **Exemple :** `AVI-20260119-1234`
        """)

if __name__ == "__main__":
    main()
