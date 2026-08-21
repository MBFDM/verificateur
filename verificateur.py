"""
Application de Vérification d'AVI - Version Premium
Permet de vérifier les informations d'une AVI en entrant sa référence
"""

import streamlit as st
import mysql.connector
import pandas as pd
from datetime import datetime
import logging
import re
import time

# Configuration de la page
st.set_page_config(
    page_title="Vérificateur AVI - Eco Capital",
    page_icon="logo.png",
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
}

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================
# URL DE RETOUR - MODIFIEZ ICI L'URL DE DESTINATION
# ============================================================
RETURN_URL = "https://www.ecocapitale.com"  # Remplacez par l'URL de votre site

# Styles CSS personnalisés - Design Premium avec animations
st.markdown("""
<style>
    /* ===== ANIMATIONS GLOBALES ===== */
    @keyframes fadeInDown {
        from { opacity: 0; transform: translateY(-30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    @keyframes shimmer {
        0% { background-position: -200% center; }
        100% { background-position: 200% center; }
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    @keyframes rotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-30px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes slideInRight {
        from { opacity: 0; transform: translateX(30px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes borderGlow {
        0%, 100% { border-color: var(--primary-color); }
        50% { border-color: var(--secondary-color); }
    }

    @keyframes arrowBounce {
        0%, 100% { transform: translateX(0); }
        50% { transform: translateX(-5px); }
    }

    /* ===== BOUTON RETOUR ===== */
    .back-button-container {
        margin-bottom: 1.5rem;
        animation: fadeInDown 0.6s ease-out;
    }
    
    .back-button {
        display: inline-flex;
        align-items: center;
        gap: 10px;
        padding: 0.6rem 1.5rem;
        border-radius: 50px;
        text-decoration: none;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        background: var(--background-secondary);
        border: 2px solid var(--border-color);
        color: var(--text-primary);
        cursor: pointer;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    .back-button:hover {
        transform: translateX(-5px) scale(1.02);
        border-color: var(--gradient-start);
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.2);
        background: rgba(102, 126, 234, 0.05);
    }
    
    .back-button .arrow-icon {
        display: inline-block;
        font-size: 1.2rem;
        animation: arrowBounce 2s ease-in-out infinite;
        transition: transform 0.3s ease;
    }
    
    .back-button:hover .arrow-icon {
        animation: arrowBounce 0.5s ease-in-out infinite;
    }
    
    .back-button .button-text {
        font-size: 0.95rem;
    }

    /* ===== STYLES COMMUNS ===== */
    .main-container {
        padding: 2.5rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
        animation: fadeInDown 0.8s cubic-bezier(0.16, 1, 0.3, 1);
        border: 2px solid transparent;
        background: linear-gradient(135deg, var(--gradient-start), var(--gradient-end));
        position: relative;
        overflow: hidden;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
    }
    
    .main-container::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: rotate 20s linear infinite;
        pointer-events: none;
    }
    
    .main-container::after {
        content: '';
        position: absolute;
        top: -100%;
        left: -100%;
        width: 300%;
        height: 300%;
        background: linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.05) 50%, transparent 70%);
        animation: shimmer 6s ease-in-out infinite;
        pointer-events: none;
    }
    
    .main-container h1 {
        margin: 0;
        font-size: 2.8rem;
        font-weight: 700;
        position: relative;
        z-index: 1;
        text-shadow: 0 2px 10px rgba(0,0,0,0.2);
        letter-spacing: 1px;
    }
    
    .main-container p {
        margin: 0.8rem 0 0 0;
        opacity: 0.95;
        position: relative;
        z-index: 1;
        font-size: 1.1rem;
        font-weight: 300;
        letter-spacing: 0.5px;
    }
    
    .main-container .emoji-icon {
        display: inline-block;
        animation: float 3s ease-in-out infinite;
        margin-right: 10px;
    }
    
    @keyframes fadeInDown {
        from { opacity: 0; transform: translateY(-30px) scale(0.95); }
        to { opacity: 1; transform: translateY(0) scale(1); }
    }
    
    @keyframes slideUp {
        from { opacity: 0; transform: translateY(40px) scale(0.96); }
        to { opacity: 1; transform: translateY(0) scale(1); }
    }
    
    .result-card {
        padding: 2rem;
        border-radius: 16px;
        margin-top: 1.5rem;
        animation: slideUp 0.8s cubic-bezier(0.16, 1, 0.3, 1);
        border: 1px solid var(--border-color);
        background: var(--background-secondary);
        box-shadow: 0 8px 30px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .result-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.15);
    }
    
    .result-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, var(--gradient-start), var(--gradient-end), var(--gradient-start));
        background-size: 200% 100%;
        animation: shimmer 3s ease-in-out infinite;
    }
    
    .info-item {
        display: flex;
        justify-content: space-between;
        padding: 0.85rem 0;
        border-bottom: 1px solid var(--border-color);
        transition: all 0.3s ease;
        animation: fadeIn 0.5s ease-out;
        animation-fill-mode: both;
    }
    
    .info-item:nth-child(1) { animation-delay: 0.1s; }
    .info-item:nth-child(2) { animation-delay: 0.2s; }
    .info-item:nth-child(3) { animation-delay: 0.3s; }
    .info-item:nth-child(4) { animation-delay: 0.4s; }
    .info-item:nth-child(5) { animation-delay: 0.5s; }
    .info-item:nth-child(6) { animation-delay: 0.6s; }
    
    .info-item:last-child {
        border-bottom: none;
    }
    
    .info-item:hover {
        background: rgba(102, 126, 234, 0.05);
        padding-left: 10px;
        border-radius: 8px;
    }
    
    .info-label {
        font-weight: 600;
        color: var(--text-secondary);
        font-size: 0.95rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .info-label .label-icon {
        font-size: 1.1rem;
    }
    
    .info-value {
        font-weight: 500;
        color: var(--text-secondary);
        font-size: 0.95rem;
        transition: all 0.3s ease;
    }
    
    .info-value:hover {
        color: var(--gradient-start);
    }
    
    .status-valid {
        background: linear-gradient(135deg, #28a745, #20c997);
        color: white;
        padding: 0.3rem 1.2rem;
        border-radius: 25px;
        font-weight: 600;
        display: inline-block;
        animation: pulse 2s ease-in-out infinite;
        box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);
    }
    
    .status-invalid {
        background: linear-gradient(135deg, #dc3545, #e74c3c);
        color: white;
        padding: 0.3rem 1.2rem;
        border-radius: 25px;
        font-weight: 600;
        display: inline-block;
        box-shadow: 0 4px 15px rgba(220, 53, 69, 0.3);
    }
    
    .verification-badge {
        background: linear-gradient(135deg, #ffc107, #ff9800);
        color: #333;
        padding: 0.6rem 2rem;
        border-radius: 35px;
        font-weight: 700;
        display: inline-block;
        font-size: 1rem;
        animation: pulse 2s ease-in-out infinite;
        box-shadow: 0 4px 20px rgba(255, 193, 7, 0.4);
        letter-spacing: 1px;
    }

    .stTextInput > div > div > input {
        font-size: 1.1rem;
        padding: 0.85rem 1.2rem;
        border-radius: 12px;
        transition: all 0.3s ease;
        border: 2px solid var(--border-color);
        background: var(--background-primary);
        color: var(--text-primary);
    }
    
    .stTextInput > div > div > input:focus {
        border-color: var(--gradient-start);
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
        transform: scale(1.01);
    }

    /* ===== BOUTON AVEC ANIMATION ===== */
    .stButton > button {
        border-radius: 12px !important;
        padding: 0.7rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
        border: none !important;
        background: linear-gradient(135deg, var(--gradient-start), var(--gradient-end)) !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    .stButton > button::before {
        content: '' !important;
        position: absolute !important;
        top: -50% !important;
        left: -50% !important;
        width: 200% !important;
        height: 200% !important;
        background: linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.1) 50%, transparent 70%) !important;
        animation: shimmer 3s ease-in-out infinite !important;
        pointer-events: none !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 0 8px 30px rgba(102, 126, 234, 0.4) !important;
    }
    
    .stButton > button:active {
        transform: scale(0.98) !important;
    }

    /* ===== THÈME CLAIR ===== */
    [data-theme="light"] {
        --background-primary: #ffffff;
        --background-secondary: #f8f9fa;
        --text-primary: #262730;
        --text-secondary: #555555;
        --border-color: #e0e0e0;
        --gradient-start: #667eea;
        --gradient-end: #764ba2;
        --primary-color: #667eea;
        --secondary-color: #764ba2;
    }
    
    [data-theme="light"] .main-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    [data-theme="light"] .result-card {
        background: white;
        box-shadow: 0 8px 30px rgba(0,0,0,0.08);
    }
    
    [data-theme="light"] .info-item {
        border-bottom-color: #eee;
    }
    
    [data-theme="light"] .info-label {
        color: #555;
    }
    
    [data-theme="light"] .info-value {
        color: #333;
    }

    [data-theme="light"] .back-button {
        background: white;
        border-color: #ddd;
        color: #333;
    }
    
    [data-theme="light"] .back-button:hover {
        border-color: #667eea;
        background: rgba(102, 126, 234, 0.05);
    }

    /* ===== THÈME SOMBRE ===== */
    @media (prefers-color-scheme: dark) {
        [data-theme="dark"] {
            --background-primary: #0e1117;
            --background-secondary: #1e2130;
            --text-primary: #fafafa;
            --text-secondary: #a0a0a0;
            --border-color: #2d303a;
            --gradient-start: #4a6fa5;
            --gradient-end: #6c5b7b;
            --primary-color: #4a6fa5;
            --secondary-color: #6c5b7b;
        }
        
        [data-theme="dark"] .main-container {
            background: linear-gradient(135deg, #2d2d44 0%, #1a1a2e 100%);
            color: #f0f0f0;
            border-color: #3d3d55;
            box-shadow: 0 10px 40px rgba(0,0,0,0.4);
        }
        
        [data-theme="dark"] .result-card {
            background: #1e2130;
            box-shadow: 0 8px 30px rgba(0,0,0,0.3);
            border-color: #3d3d55;
        }
        
        [data-theme="dark"] .info-item {
            border-bottom-color: #3d3d55;
        }
        
        [data-theme="dark"] .info-label {
            color: #a0a0a0;
        }
        
        [data-theme="dark"] .info-value {
            color: #f0f0f0;
        }
        
        [data-theme="dark"] .verification-badge {
            background: linear-gradient(135deg, #ffc107, #ff9800);
            color: #1a1a2e;
        }
        
        [data-theme="dark"] .status-valid {
            background: linear-gradient(135deg, #2d8f47, #1a9c6f);
        }
        
        [data-theme="dark"] .status-invalid {
            background: linear-gradient(135deg, #b33c4a, #c0392b);
        }

        [data-theme="dark"] .back-button {
            background: #1e2130;
            border-color: #3d3d55;
            color: #f0f0f0;
        }
        
        [data-theme="dark"] .back-button:hover {
            border-color: #4a6fa5;
            background: rgba(74, 111, 165, 0.1);
        }
    }

    /* ===== VARIABLES CSS DYNAMIQUES ===== */
    :root {
        --background-primary: #ffffff;
        --background-secondary: #f8f9fa;
        --text-primary: #262730;
        --text-secondary: #555555;
        --border-color: #e0e0e0;
        --gradient-start: #667eea;
        --gradient-end: #764ba2;
        --primary-color: #667eea;
        --secondary-color: #764ba2;
    }
    
    @media (prefers-color-scheme: dark) {
        :root {
            --background-primary: #0e1117;
            --background-secondary: #1e2130;
            --text-primary: #fafafa;
            --text-secondary: #a0a0a0;
            --border-color: #2d303a;
            --gradient-start: #4a6fa5;
            --gradient-end: #6c5b7b;
            --primary-color: #4a6fa5;
            --secondary-color: #6c5b7b;
        }
    }
    
    /* ===== SECTION DE RECHERCHE ===== */
    .search-section {
        animation: fadeInUp 0.6s ease-out;
    }
    
    /* ===== BADGE DE STATUT ===== */
    .status-container {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 10px;
        margin: 1rem 0;
    }
    
    /* ===== RESPONSIVE ===== */
    @media (max-width: 768px) {
        .main-container {
            padding: 1.5rem;
        }
        
        .main-container h1 {
            font-size: 1.8rem;
        }
        
        .result-card {
            padding: 1rem;
        }
        
        .info-item {
            flex-direction: column;
            gap: 5px;
            padding: 0.6rem 0;
        }
        
        .back-button {
            padding: 0.5rem 1rem;
            font-size: 0.85rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# JavaScript pour détecter le thème avec animation de transition
st.markdown("""
<script>
    // Détection du thème
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const theme = prefersDark ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', theme);
    
    // Transition douce pour le changement de thème
    document.addEventListener('DOMContentLoaded', function() {
        document.body.style.transition = 'background-color 0.5s ease, color 0.5s ease';
    });
</script>
""", unsafe_allow_html=True)

def get_db_connection():
    """Établit une connexion à la base de données MySQL"""
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        return conn
    except mysql.connector.Error as err:
        logger.error(f"Erreur de connexion à MySQL: {err}")
        st.error(f"❌ Erreur de connexion à la base de données: {err}")
        return None

def init_database():
    """Vérifie et crée les tables nécessaires si elles n'existent pas"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Vérifier si la table avis existe
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_schema = %s AND table_name = 'avis'
        """, (MYSQL_CONFIG['database'],))
        
        table_exists = cursor.fetchone()[0] > 0
        
        if not table_exists:
            # Créer la table avis si elle n'existe pas
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS avis (
                id INT AUTO_INCREMENT PRIMARY KEY,
                reference VARCHAR(50) UNIQUE NOT NULL,
                nom_complet VARCHAR(255) NOT NULL,
                code_banque VARCHAR(50) NOT NULL,
                numero_compte VARCHAR(50) NOT NULL,
                devise VARCHAR(10) NOT NULL,
                iban VARCHAR(50) NOT NULL,
                bic VARCHAR(20) NOT NULL,
                montant DECIMAL(15,2) NOT NULL,
                date_creation DATE NOT NULL,
                date_expiration DATE,
                statut VARCHAR(50) NOT NULL,
                commentaires TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            conn.commit()
            st.success("✅ Table 'avis' créée avec succès")
        
        # Vérifier si la table info_avi existe
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_schema = %s AND table_name = 'info_avi'
        """, (MYSQL_CONFIG['database'],))
        
        info_table_exists = cursor.fetchone()[0] > 0
        
        if not info_table_exists:
            # Créer la table info_avi si elle n'existe pas
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS info_avi (
                id INT AUTO_INCREMENT PRIMARY KEY,
                reference VARCHAR(50) UNIQUE NOT NULL,
                nom_complet VARCHAR(255) NOT NULL,
                code_banque VARCHAR(50) NOT NULL,
                numero_compte VARCHAR(50) NOT NULL,
                devise VARCHAR(10) NOT NULL,
                iban VARCHAR(50) NOT NULL,
                bic VARCHAR(20) NOT NULL,
                montant DECIMAL(15,2) NOT NULL,
                date_creation DATE,
                date_expiration DATE,
                statut VARCHAR(50),
                commentaires TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            ''')
            conn.commit()
            st.success("✅ Table 'info_avi' créée avec succès")
        
        cursor.close()
        conn.close()
        return True
        
    except mysql.connector.Error as e:
        logger.error(f"Erreur lors de l'initialisation de la base de données: {str(e)}")
        st.error(f"❌ Erreur lors de l'initialisation de la base de données: {str(e)}")
        return False

def verify_avi(reference: str):
    """
    Vérifie une AVI par sa référence
    Retourne les informations de l'AVI si trouvée
    """
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Requête pour récupérer les informations de l'AVI
        # On cherche d'abord dans la table avis, puis dans info_avi
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
            commentaires
        FROM avis 
        WHERE reference = %s
        """
        
        cursor.execute(query, (reference.strip(),))
        result = cursor.fetchone()
        
        # Si pas trouvé dans avis, chercher dans info_avi
        if not result:
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
                commentaires
            FROM info_avi 
            WHERE reference = %s
            """
            cursor.execute(query, (reference.strip(),))
            result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return result
        
    except mysql.connector.Error as e:
        logger.error(f"Erreur lors de la vérification: {str(e)}")
        st.error(f"❌ Erreur lors de la vérification: {str(e)}")
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

def display_back_button():
    """Affiche le bouton retour en haut de la page"""
    st.markdown(f"""
    <div class="back-button-container">
        <a href="{RETURN_URL}" target="_blank" class="back-button">
            <span class="arrow-icon">←</span>
            <span class="button-text">Retour</span>
        </a>
    </div>
    """, unsafe_allow_html=True)

def display_avi_result(result):
    """Affiche les résultats de la vérification avec animations"""
    if not result:
        return
    
    # Badge de vérification
    st.markdown("""
    <div style="text-align: center; margin: 1.5rem 0;">
        <span class="verification-badge">✅ AVI VALIDE</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Carte des résultats
    st.markdown('<div class="result-card">', unsafe_allow_html=True)
    
    # Titre avec icône animée
    st.markdown("""
    <h3 style="display: flex; align-items: center; gap: 10px; margin-bottom: 1.5rem;">
        <span style="display: inline-block; animation: float 3s ease-in-out infinite;">📄</span>
        Informations de l'AVI
    </h3>
    """, unsafe_allow_html=True)
    
    # Informations principales
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="info-item">
            <span class="info-label"><span class="label-icon"></span> Référence : </span>
            <span class="info-value">{result.get('reference', 'N/A')}</span>
        </div>
        <div class="info-item">
            <span class="info-label"><span class="label-icon"></span> Nom : </span>
            <span class="info-value">{result.get('nom_complet', 'N/A')}</span>
        </div>
        <div class="info-item">
            <span class="info-label"><span class="label-icon"></span> Code Banque : </span>
            <span class="info-value">{result.get('code_banque', 'N/A')}</span>
        </div>
        <div class="info-item">
            <span class="info-label"><span class="label-icon"></span> Numéro de Compte : </span>
            <span class="info-value">{result.get('numero_compte', 'N/A')}</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="info-item">
            <span class="info-label"><span class="label-icon"></span> Devise : </span>
            <span class="info-value">{result.get('devise', 'XAF')}</span>
        </div>
        <div class="info-item">
            <span class="info-label"><span class="label-icon"></span> IBAN : </span>
            <span class="info-value" style="font-family: monospace;">{format_iban(result.get('iban', 'N/A'))}</span>
        </div>
        <div class="info-item">
            <span class="info-label"><span class="label-icon"></span> BIC : </span>
            <span class="info-value" style="font-family: monospace;">{result.get('bic', 'N/A')}</span>
        </div>
        <div class="info-item">
            <span class="info-label"><span class="label-icon"></span> Montant : </span>
            <span class="info-value" style="font-weight: 700; color: #28a745;">{format_montant(result.get('montant'), result.get('devise', 'XAF'))}</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Commentaires si présents
    if result.get('commentaires'):
        st.markdown(f"""
        <div style="background: var(--background-secondary); padding: 1.2rem; border-radius: 12px; margin-top: 1rem; border: 1px solid var(--border-color); animation: fadeInUp 0.6s ease-out;">
            <strong style="display: flex; align-items: center; gap: 8px;">
                <span>📝</span> Commentaires
            </strong>
            <p style="margin: 0.5rem 0 0 0; color: var(--text-primary);">{result.get('commentaires')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Pied de page du résultat avec icône animée
    st.markdown(f"""
    <div style="text-align: center; margin-top: 1.5rem; color: var(--text-secondary); font-size: 0.85rem; animation: fadeIn 1s ease-out;">
        <span style="display: inline-block; animation: float 3s ease-in-out infinite;">🔒</span>
        Vérifié le {datetime.now().strftime('%d/%m/%Y à %H:%M')} · Document certifié par Eco Capital
    </div>
    """, unsafe_allow_html=True)

def main():
    """Point d'entrée principal"""
    
    # Afficher le bouton retour en haut
    display_back_button()
    
    # Initialisation de la base de données avec animation
    with st.spinner("🔄 Vérification de la base de données..."):
        init_success = init_database()
        if not init_success:
            st.warning("⚠️ Problème avec la base de données. Certaines fonctionnalités peuvent être limitées.")
    
    # En-tête avec animation
    st.markdown("""
    <div class="main-container">
        <h1>
            <span class="emoji-icon">🔍</span>
            Vérificateur d'AVI
        </h1>
        <p>Entrez la référence de l'AVI pour vérifier son authenticité en temps réel</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Section de recherche
    st.markdown('<div class="search-section">', unsafe_allow_html=True)
    st.markdown("### 📝 Recherche par référence")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        reference = st.text_input(
            "Référence de l'AVI",
            placeholder="Ex: AVI-20260119-1234",
            label_visibility="collapsed"
        )
        
        # Bouton de vérification avec animation
        if st.button("🔍 Vérifier", type="primary", use_container_width=True):
            if not reference or not reference.strip():
                st.warning("⚠️ Veuillez entrer une référence d'AVI")
            else:
                with st.spinner("🔎 Vérification en cours..."):
                    # Simuler un temps de chargement pour l'effet
                    time.sleep(0.5)
                    result = verify_avi(reference)
                    
                    if result:
                        st.markdown("---")
                        display_avi_result(result)
                    else:
                        st.markdown("---")
                        st.markdown("""
                        <div style="text-align: center; padding: 2.5rem; background: #fff3cd; border-radius: 12px; border: 2px solid #ffc107; animation: fadeInUp 0.6s ease-out;">
                            <div style="font-size: 3rem; margin-bottom: 1rem;">❌</div>
                            <h3 style="color: #856404;">AVI non trouvée</h3>
                            <p style="color: #856404; font-size: 1.1rem;">
                                Aucune attestation trouvée avec la référence <strong>{}</strong>
                            </p>
                            <p style="color: #856404; font-size: 0.95rem; margin-top: 0.5rem;">
                                Vérifiez que la référence est correcte (format: AVI-YYYYMMDD-XXXX)
                            </p>
                        </div>
                        """.format(reference.strip()), unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Section d'information
    with st.expander("ℹ️ Comment utiliser le vérificateur", expanded=False):
        st.markdown("""
        <div style="padding: 0.5rem 0;">
            <p style="font-size: 1.05rem; margin-bottom: 1rem;">📋 <strong>Instructions :</strong></p>
            <ol style="font-size: 1rem; line-height: 2;">
                <li>Entrez la <strong>référence complète</strong> de l'AVI dans le champ de recherche</li>
                <li>Cliquez sur le bouton <strong>"Vérifier"</strong></li>
                <li>Les informations de l'AVI s'afficheront si elles existent dans la base de données</li>
            </ol>
            <div style="background: var(--background-secondary); padding: 1rem; border-radius: 8px; margin-top: 1rem; border-left: 4px solid var(--gradient-start);">
                <p style="margin: 0;"><strong>Format de référence attendu :</strong> <code style="background: var(--border-color); padding: 0.2rem 0.5rem; border-radius: 4px;">AVI-YYYYMMDD-XXXX</code></p>
                <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem; color: var(--text-secondary);">
                    • YYYYMMDD : Date de création (Année/Mois/Jour)<br>
                    • XXXX : Numéro aléatoire à 4 chiffres
                </p>
                <p style="margin: 0.5rem 0 0 0; font-weight: 500;">Exemple : <code style="background: var(--border-color); padding: 0.2rem 0.5rem; border-radius: 4px;">AVI-20260119-1234</code></p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Section des statistiques
    with st.expander("📊 Statistiques", expanded=False):
        st.markdown("""
        <div style="padding: 0.5rem 0;">
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
                <div style="background: var(--background-secondary); padding: 1rem; border-radius: 10px; text-align: center; border: 1px solid var(--border-color);">
                    <div style="font-size: 2rem;">🔒</div>
                    <p style="margin: 0.5rem 0 0 0; font-weight: 600;">Sécurisé</p>
                    <p style="margin: 0; font-size: 0.85rem; color: var(--text-secondary);">Vérification certifiée</p>
                </div>
                <div style="background: var(--background-secondary); padding: 1rem; border-radius: 10px; text-align: center; border: 1px solid var(--border-color);">
                    <div style="font-size: 2rem;">✅</div>
                    <p style="margin: 0.5rem 0 0 0; font-weight: 600;">Authentique</p>
                    <p style="margin: 0; font-size: 0.85rem; color: var(--text-secondary);">Documents validés</p>
                </div>
                <div style="background: var(--background-secondary); padding: 1rem; border-radius: 10px; text-align: center; border: 1px solid var(--border-color);">
                    <div style="font-size: 2rem;">🕒</div>
                    <p style="margin: 0.5rem 0 0 0; font-weight: 600;">Temps réel</p>
                    <p style="margin: 0; font-size: 0.85rem; color: var(--text-secondary);">Vérification instantanée</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Footer avec animation
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: var(--text-secondary); font-size: 0.8rem; padding: 1rem 0; animation: fadeIn 1s ease-out;">
        <span style="display: inline-block; animation: float 4s ease-in-out infinite;">©</span>
        2026 Eco Capital - Vérificateur d'AVI
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
