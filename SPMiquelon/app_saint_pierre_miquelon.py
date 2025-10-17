import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
from scraper.europe_direct_saint_pierre_miquelon import scrape_europe_direct_saint_pierre_miquelon
from scraper.data_gouv_saint_pierre_miquelon import scrape_data_gouv_saint_pierre_miquelon
from scraper.region_saint_pierre_miquelon import scrape_region_saint_pierre_miquelon
from utils.data_processor import process_funds_data
import time

# Configuration de la page
st.set_page_config(
    page_title="Fonds Européens - Saint-Pierre et Miquelon",
    page_icon="🇪🇺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #003399;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #003399;
    }
    .program-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    .section-header {
        color: #003399;
        border-bottom: 2px solid #003399;
        padding-bottom: 0.5rem;
        margin: 2rem 0 1rem 0;
    }
    .data-source {
        background-color: #e8f4fd;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.5rem 0;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=3600)  # Cache pour 1 heure
def load_real_time_data():
    """Charge les données en temps réel depuis les sources officielles"""
    
    st.sidebar.info("🔄 Chargement des données en cours...")
    
    all_data = []
    
    try:
        # Scraping Europe Direct Saint-Pierre et Miquelon
        with st.spinner("Récupération des données Europe Direct..."):
            europe_direct_data = scrape_europe_direct_saint_pierre_miquelon()
            if europe_direct_data:
                all_data.extend(europe_direct_data)
                st.sidebar.success(f"✅ Europe Direct: {len(europe_direct_data)} projets")
            else:
                st.sidebar.warning("❌ Europe Direct: Données temporairement indisponibles")
    except Exception as e:
        st.sidebar.error(f"❌ Erreur Europe Direct: {str(e)}")
    
    try:
        # Scraping data.gouv.fr
        with st.spinner("Récupération des données data.gouv.fr..."):
            data_gouv_data = scrape_data_gouv_saint_pierre_miquelon()
            if data_gouv_data:
                all_data.extend(data_gouv_data)
                st.sidebar.success(f"✅ data.gouv.fr: {len(data_gouv_data)} projets")
            else:
                st.sidebar.warning("❌ data.gouv.fr: Données temporairement indisponibles")
    except Exception as e:
        st.sidebar.error(f"❌ Erreur data.gouv.fr: {str(e)}")
    
    try:
        # Scraping Collectivité de Saint-Pierre et Miquelon
        with st.spinner("Récupération des données Collectivité de Saint-Pierre et Miquelon..."):
            region_data = scrape_region_saint_pierre_miquelon()
            if region_data:
                all_data.extend(region_data)
                st.sidebar.success(f"✅ Collectivité SPM: {len(region_data)} projets")
            else:
                st.sidebar.warning("❌ Collectivité SPM: Données temporairement indisponibles")
    except Exception as e:
        st.sidebar.error(f"❌ Erreur Collectivité SPM: {str(e)}")
    
    if not all_data:
        st.error("Aucune donnée n'a pu être récupérée. Utilisation des données de démonstration.")
        return generate_fallback_data()
    
    return process_funds_data(all_data)

def generate_fallback_data():
    """Génère des données de démonstration si le scraping échoue"""
    programmes = ["FEDER", "FSE", "FEADER", "FSE+", "INTERREG"]
    secteurs = ["Agriculture", "Tourisme", "Recherche", "Formation", "Environnement", "Transport", "Santé", "Numérique", "Énergie", "Pêche"]
    
    data = []
    for i in range(150):
        programme = np.random.choice(programmes)
        secteur = np.random.choice(secteurs)
        montant = np.random.uniform(50000, 3000000)
        
        date_debut = datetime.now() - timedelta(days=np.random.randint(1, 1095))
        date_fin = date_debut + timedelta(days=np.random.randint(180, 720))
        
        if date_fin < datetime.now():
            statut = "Terminé"
            taux_realisation = 1.0
        elif date_fin > datetime.now() + timedelta(days=180):
            statut = "En cours"
            taux_realisation = np.random.uniform(0.3, 0.8)
        else:
            statut = "En finalisation"
            taux_realisation = np.random.uniform(0.8, 0.95)
        
        data.append({
            "id": f"SPM_{2021 + i//50}_{i%50:04d}",
            "programme": programme,
            "secteur": secteur,
            "montant_total": round(montant, 2),
            "montant_paye": round(montant * taux_realisation, 2),
            "statut": statut,
            "taux_realisation": round(taux_realisation * 100, 1),
            "beneficiaire": f"Bénéficiaire {i}",
            "date_debut": date_debut.strftime("%Y-%m-%d"),
            "date_fin_prevue": date_fin.strftime("%Y-%m-%d"),
            "commune": np.random.choice(["Saint-Pierre", "Miquelon-Langlade"]),
            "source": "Données de démonstration"
        })
    
    return pd.DataFrame(data)

def main():
    # Titre principal
    st.markdown('<h1 class="main-header">🇪🇺 Fonds Européens - Saint-Pierre et Miquelon - Temps Réel</h1>', unsafe_allow_html=True)
    
    # Information sur la dernière mise à jour
    last_update = datetime.now().strftime("%d/%m/%Y à %H:%M")
    st.sidebar.markdown(f"**🕒 Dernière mise à jour :** {last_update}")
    
    # Bouton de rafraîchissement manuel
    if st.sidebar.button("🔄 Actualiser les données"):
        st.cache_data.clear()
        st.rerun()
    
    # Chargement des données
    df = load_real_time_data()
    
    # Sidebar pour les filtres
    st.sidebar.markdown("---")
    st.sidebar.title("🔍 Filtres")
    
    # Filtres
    programmes_selection = st.sidebar.multiselect(
        "Programmes",
        options=df['programme'].unique(),
        default=df['programme'].unique()
    )
    
    secteurs_selection = st.sidebar.multiselect(
        "Secteurs",
        options=df['secteur'].unique(),
        default=df['secteur'].unique()
    )
    
    statuts_selection = st.sidebar.multiselect(
        "Statuts",
        options=df['statut'].unique(),
        default=df['statut'].unique()
    )
    
    # Application des filtres
    df_filtre = df[
        (df['programme'].isin(programmes_selection)) &
        (df['secteur'].isin(secteurs_selection)) &
        (df['statut'].isin(statuts_selection))
    ]
    
    # Métriques principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        montant_total = df_filtre['montant_total'].sum()
        st.metric(
            label="💰 Montant Total Engagé",
            value=f"{montant_total:,.0f} €".replace(",", " "),
            delta=f"{len(df_filtre)} projets"
        )
    
    with col2:
        montant_paye = df_filtre['montant_paye'].sum()
        taux_paiement = (montant_paye / montant_total * 100) if montant_total > 0 else 0
        st.metric(
            label="💳 Montant Déjà Payé",
            value=f"{montant_paye:,.0f} €".replace(",", " "),
            delta=f"{taux_paiement:.1f}%"
        )
    
    with col3:
        projets_termines = len(df_filtre[df_filtre['statut'] == 'Terminé'])
        st.metric(
            label="✅ Projets Terminés",
            value=projets_termines,
            delta=f"{projets_termines/len(df_filtre)*100:.1f}%" if len(df_filtre) > 0 else "0%"
        )
    
    with col4:
        taux_moyen = df_filtre['taux_realisation'].mean()
        st.metric(
            label="📊 Taux de Réalisation Moyen",
            value=f"{taux_moyen:.1f}%" if not np.isnan(taux_moyen) else "0%",
            delta="Avancement global"
        )
    
    # Indicateur de données en temps réel
    sources_utilisees = df['source'].unique()
    st.markdown(f"**Sources des données :** {', '.join(sources_utilisees)}")
    
    st.markdown("---")
    
    # Graphiques
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<h3 class="section-header">📈 Répartition par Programme</h3>', unsafe_allow_html=True)
        
        programme_stats = df_filtre.groupby('programme').agg({
            'montant_total': 'sum',
            'id': 'count'
        }).reset_index()
        
        if not programme_stats.empty:
            fig_programmes = px.pie(
                programme_stats,
                values='montant_total',
                names='programme',
                title="Répartition du budget par programme",
                hole=0.4
            )
            fig_programmes.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_programmes, use_container_width=True)
        else:
            st.info("Aucune donnée à afficher pour les filtres sélectionnés")
    
    with col2:
        st.markdown('<h3 class="section-header">🏗️ Répartition par Secteur</h3>', unsafe_allow_html=True)
        
        secteur_stats = df_filtre.groupby('secteur').agg({
            'montant_total': 'sum',
            'id': 'count'
        }).reset_index()
        
        if not secteur_stats.empty:
            secteur_stats = secteur_stats.sort_values('montant_total', ascending=True)
            fig_secteurs = px.bar(
                secteur_stats,
                y='secteur',
                x='montant_total',
                orientation='h',
                title="Montant total par secteur",
                color='montant_total',
                color_continuous_scale='Blues'
            )
            st.plotly_chart(fig_secteurs, use_container_width=True)
        else:
            st.info("Aucune donnée à afficher pour les filtres sélectionnés")
    
    # Tableau détaillé
    st.markdown('<h3 class="section-header">📋 Projets des Fonds Européens à Saint-Pierre et Miquelon</h3>', unsafe_allow_html=True)
    
    # Options d'affichage
    col1, col2 = st.columns([1, 3])
    with col1:
        nb_lignes = st.selectbox("Nombre de projets à afficher", [10, 25, 50, 100])
    
    # Formatage pour l'affichage
    df_affichage = df_filtre.copy()
    df_affichage['montant_total'] = df_affichage['montant_total'].apply(lambda x: f"{x:,.0f} €".replace(",", " "))
    df_affichage['montant_paye'] = df_affichage['montant_paye'].apply(lambda x: f"{x:,.0f} €".replace(",", " "))
    df_affichage['taux_realisation'] = df_affichage['taux_realisation'].apply(lambda x: f"{x}%")
    
    colonnes_a_afficher = ['id', 'programme', 'secteur', 'beneficiaire', 'commune', 
                          'montant_total', 'montant_paye', 'taux_realisation', 'statut', 'source']
    
    st.dataframe(
        df_affichage[colonnes_a_afficher].head(nb_lignes),
        use_container_width=True,
        height=400
    )
    
    # Téléchargement
    st.markdown("---")
    st.markdown("### 📥 Télécharger les données")
    
    csv = df_filtre.to_csv(index=False, sep=';').encode('utf-8')
    st.download_button(
        label="💾 Télécharger les données (CSV)",
        data=csv,
        file_name=f"fonds_europeens_spm_reel_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv"
    )

if __name__ == "__main__":
    main()