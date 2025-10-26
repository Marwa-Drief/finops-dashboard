"""
FinOps Dashboard - Analyse des Coûts Cloud Multi-Compte
Dashboard interactif Streamlit pour visualiser et analyser les coûts cloud
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import glob
import os
import json

# Configuration de la page
st.set_page_config(
    page_title="FinOps Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé pour un design moderne
st.markdown("""
    <style>
    .main {
        background-color: #f5f7fa;
    }
    .stMetric {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    h1 {
        color: #1f77b4;
        font-weight: 700;
    }
    h2, h3 {
        color: #2c3e50;
    }
    .highlight-box {
        background-color: #e8f4f8;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_data
def load_latest_data():
    """Charge les dernières données transformées"""
    
    # Chercher le fichier le plus récent
    enriched_files = glob.glob('data/processed/costs_enriched_*.csv')
    if not enriched_files:
        return None, None, None
    
    latest_file = max(enriched_files, key=os.path.getctime)
    df = pd.read_csv(latest_file)
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Charger les KPIs
    kpi_files = glob.glob('data/processed/kpis_*.json')
    kpis = None
    if kpi_files:
        latest_kpi = max(kpi_files, key=os.path.getctime)
        with open(latest_kpi, 'r') as f:
            kpis = json.load(f)
    
    # Charger l'évolution mensuelle
    monthly_files = glob.glob('data/processed/monthly_evolution_*.csv')
    monthly_df = None
    if monthly_files:
        latest_monthly = max(monthly_files, key=os.path.getctime)
        monthly_df = pd.read_csv(latest_monthly)
    
    return df, kpis, monthly_df


def create_kpi_cards(df, kpis):
    """Affiche les cartes KPI en haut du dashboard"""
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_cost = df['Cost'].sum()
        st.metric(
            label="💰 Coût Total",
            value=f"${total_cost:,.2f}",
            delta=None
        )
    
    with col2:
        if kpis:
            avg_daily = kpis.get('avg_daily_cost', 0)
            st.metric(
                label="📊 Coût Moyen/Jour",
                value=f"${avg_daily:,.2f}",
                delta=None
            )
    
    with col3:
        if kpis:
            trend = kpis.get('trend_pct', 0)
            st.metric(
                label="📈 Tendance",
                value=f"{abs(trend):.1f}%",
                delta=f"{trend:+.1f}%" if trend != 0 else "Stable",
                delta_color="inverse"  # Rouge si hausse, vert si baisse
            )
    
    with col4:
        if kpis:
            anomalies = kpis.get('anomaly_count', 0)
            st.metric(
                label="⚠️ Anomalies Détectées",
                value=str(anomalies),
                delta="Jours atypiques"
            )


def plot_daily_costs(df):
    """Graphique de l'évolution journalière des coûts"""
    
    daily_costs = df.groupby('Date')['Cost'].sum().reset_index()
    
    fig = px.line(
        daily_costs,
        x='Date',
        y='Cost',
        title='📅 Évolution des Coûts Journaliers',
        labels={'Cost': 'Coût (USD)', 'Date': 'Date'}
    )
    
    fig.update_traces(
        line_color='#1f77b4',
        line_width=2,
        mode='lines+markers'
    )
    
    fig.update_layout(
        hovermode='x unified',
        plot_bgcolor='white',
        height=400,
        xaxis=dict(showgrid=True, gridcolor='lightgray'),
        yaxis=dict(showgrid=True, gridcolor='lightgray')
    )
    
    return fig


def plot_service_breakdown(df):
    """Graphique camembert de la répartition par service"""
    
    service_costs = df.groupby('Service')['Cost'].sum().sort_values(ascending=False).head(10)
    
    fig = px.pie(
        values=service_costs.values,
        names=service_costs.index,
        title='🔧 Top 10 Services par Coût',
        hole=0.4  # Donut chart
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Coût: $%{value:,.2f}<br>Part: %{percent}<extra></extra>'
    )
    
    fig.update_layout(height=400)
    
    return fig


def plot_category_costs(df):
    """Graphique en barres des coûts par catégorie"""
    
    category_costs = df.groupby('ServiceCategory')['Cost'].sum().sort_values(ascending=True)
    
    fig = px.bar(
        x=category_costs.values,
        y=category_costs.index,
        orientation='h',
        title='📦 Coûts par Catégorie de Service',
        labels={'x': 'Coût (USD)', 'y': 'Catégorie'},
        color=category_costs.values,
        color_continuous_scale='Blues'
    )
    
    fig.update_layout(
        showlegend=False,
        height=400,
        xaxis=dict(showgrid=True, gridcolor='lightgray'),
        plot_bgcolor='white'
    )
    
    return fig


def plot_account_comparison(df):
    """Comparaison des coûts entre comptes"""
    
    if 'AccountName' not in df.columns:
        return None
    
    account_costs = df.groupby(['Date', 'AccountName'])['Cost'].sum().reset_index()
    
    fig = px.area(
        account_costs,
        x='Date',
        y='Cost',
        color='AccountName',
        title='💼 Évolution des Coûts par Compte',
        labels={'Cost': 'Coût (USD)', 'Date': 'Date', 'AccountName': 'Compte'}
    )
    
    fig.update_layout(
        hovermode='x unified',
        plot_bgcolor='white',
        height=400,
        xaxis=dict(showgrid=True, gridcolor='lightgray'),
        yaxis=dict(showgrid=True, gridcolor='lightgray')
    )
    
    return fig


def plot_weekday_analysis(df):
    """Analyse des coûts par jour de la semaine"""
    
    weekday_costs = df.groupby('DayName')['Cost'].mean().reindex([
        'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
    ])
    
    fig = go.Figure(data=[
        go.Bar(
            x=weekday_costs.index,
            y=weekday_costs.values,
            marker_color=['#1f77b4', '#1f77b4', '#1f77b4', '#1f77b4', '#1f77b4', '#ff7f0e', '#ff7f0e'],
            text=[f'${v:.2f}' for v in weekday_costs.values],
            textposition='outside'
        )
    ])
    
    fig.update_layout(
        title='📅 Coût Moyen par Jour de la Semaine',
        xaxis_title='Jour',
        yaxis_title='Coût Moyen (USD)',
        plot_bgcolor='white',
        height=400,
        showlegend=False
    )
    
    return fig

def plot_cloud_comparison(df):
    """Comparaison des coûts entre clouds"""
    
    cloud_costs = df.groupby('Cloud')['Cost'].sum().reset_index()
    
    fig = px.pie(
        cloud_costs,
        values='Cost',
        names='Cloud',
        title='☁️ Répartition des Coûts par Cloud Provider',
        color='Cloud',
        color_discrete_map={'AWS': '#FF9900', 'Azure': '#0078D4'},
        hole=0.4
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label+value',
        hovertemplate='<b>%{label}</b><br>Coût: $%{value:,.2f}<br>Part: %{percent}<extra></extra>'
    )
    
    fig.update_layout(height=400)
    
    return fig

def plot_monthly_trend(monthly_df):
    """Graphique de tendance mensuelle"""
    
    if monthly_df is None:
        return None
    
    fig = go.Figure()
    
    # Ligne de tendance
    fig.add_trace(go.Scatter(
        x=monthly_df['Month'],
        y=monthly_df['TotalCost'],
        mode='lines+markers',
        name='Coût Mensuel',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=10)
    ))
    
    fig.update_layout(
        title='📈 Évolution Mensuelle des Coûts',
        xaxis_title='Mois',
        yaxis_title='Coût Total (USD)',
        plot_bgcolor='white',
        height=400,
        hovermode='x unified'
    )
    
    return fig


def show_top_services_table(df):
    """Tableau des top services avec détails"""
    
    top_services = df.groupby('Service').agg({
        'Cost': ['sum', 'mean', 'count']
    }).round(2)
    
    top_services.columns = ['Coût Total', 'Coût Moyen/Jour', 'Nb Jours']
    top_services = top_services.sort_values('Coût Total', ascending=False).head(10)
    top_services['Part (%)'] = (top_services['Coût Total'] / df['Cost'].sum() * 100).round(1)
    
    # Reformater pour l'affichage
    top_services['Coût Total'] = top_services['Coût Total'].apply(lambda x: f'${x:,.2f}')
    top_services['Coût Moyen/Jour'] = top_services['Coût Moyen/Jour'].apply(lambda x: f'${x:.2f}')
    top_services['Part (%)'] = top_services['Part (%)'].apply(lambda x: f'{x}%')
    
    return top_services


def main():
    """Fonction principale du dashboard"""
    
    # Header
    st.title("💰 FinOps Dashboard")
    st.markdown("### Analyse des Coûts Cloud Multi-Compte")
    
    # Charger les données
    with st.spinner('🔄 Chargement des données...'):
        df, kpis, monthly_df = load_latest_data()
    
    if df is None:
        st.error("❌ Aucune donnée trouvée. Veuillez d'abord exécuter les scripts d'extraction et de transformation.")
        st.info("💡 Exécutez : `python scripts/extract_costs.py` puis `python scripts/transform_costs.py`")
        return
    
    # Informations sur les données
    st.sidebar.header("📊 Informations")
    st.sidebar.info(f"""
    **Période analysée**  
    Du {df['Date'].min().strftime('%d/%m/%Y')}  
    Au {df['Date'].max().strftime('%d/%m/%Y')}
    
    **Total d'enregistrements**  
    {len(df):,} lignes
    """)
    
    # Filtres
    st.sidebar.header("🔍 Filtres")
    
    # Filtre par date
    date_range = st.sidebar.date_input(
        "Période",
        value=(df['Date'].min(), df['Date'].max()),
        min_value=df['Date'].min().date(),
        max_value=df['Date'].max().date()
    )
    
    # Filtre par compte
    if 'AccountName' in df.columns:
        accounts = ['Tous'] + sorted(df['AccountName'].unique().tolist())
        selected_account = st.sidebar.selectbox("Compte", accounts)
    else:
        selected_account = 'Tous'
    
    # Filtre par catégorie
    categories = ['Toutes'] + sorted(df['ServiceCategory'].unique().tolist())
    selected_category = st.sidebar.selectbox("Catégorie", categories)
    
    # Appliquer les filtres
    filtered_df = df.copy()
    
    if len(date_range) == 2:
        filtered_df = filtered_df[
            (filtered_df['Date'] >= pd.to_datetime(date_range[0])) &
            (filtered_df['Date'] <= pd.to_datetime(date_range[1]))
        ]
    
    if selected_account != 'Tous':
        filtered_df = filtered_df[filtered_df['AccountName'] == selected_account]
    
    if selected_category != 'Toutes':
        filtered_df = filtered_df[filtered_df['ServiceCategory'] == selected_category]
    # Dans la fonction main(), après les autres filtres (ligne ~350)

# Filtre par cloud
    clouds = ['Tous'] + sorted(df['Cloud'].unique().tolist())
    selected_cloud = st.sidebar.selectbox("☁️ Cloud Provider", clouds)

    # Appliquer le filtre
    if selected_cloud != 'Tous':
        filtered_df = filtered_df[filtered_df['Cloud'] == selected_cloud]
        
    # Vérifier si des données restent après filtrage
    if len(filtered_df) == 0:
        st.warning("⚠️ Aucune donnée ne correspond aux filtres sélectionnés.")
        return
    
    # Afficher les KPIs
    st.markdown("---")
    st.subheader("📊 Indicateurs Clés")
    create_kpi_cards(filtered_df, kpis)
    
    # Section graphiques principaux
    st.markdown("---")
    st.subheader("📈 Visualisations")
    
    # Ligne 1 : Évolution + Répartition services
    col1, col2 = st.columns(2)
    
    def main():
        
    # ... code existant jusqu'aux graphiques ...
    
    # Ligne 1 : Évolution + Répartition services
        col1, col2 = st.columns(2)
    # Après les KPIs, avant les graphiques existants

# Section Multi-Cloud
    if 'Cloud' in filtered_df.columns and len(filtered_df['Cloud'].unique()) > 1:
        st.markdown("---")
        st.subheader("☁️ Comparaison Multi-Cloud")
        
        col_cloud1, col_cloud2 = st.columns(2)
        
        with col_cloud1:
            fig_cloud = plot_cloud_comparison(filtered_df)
            st.plotly_chart(fig_cloud, width='stretch', key="cloud_comparison_chart")
        
        with col_cloud2:
            # Tableau de comparaison
            cloud_stats = filtered_df.groupby('Cloud').agg({
                'Cost': ['sum', 'mean', 'count']
            }).round(2)
            cloud_stats.columns = ['Coût Total ($)', 'Coût Moyen ($)', 'Nb Enregistrements']
            st.dataframe(cloud_stats, use_container_width=True)
        with col1:
            fig_daily = plot_daily_costs(filtered_df)
            st.plotly_chart(fig_daily, use_container_width=True, key="daily_costs_chart")
    
        with col2:
            fig_services = plot_service_breakdown(filtered_df)
            st.plotly_chart(fig_services, use_container_width=True, key="services_pie_chart")
        
        # Ligne 2 : Catégories + Comptes
        col3, col4 = st.columns(2)
        
        with col3:
            fig_categories = plot_category_costs(filtered_df)
            st.plotly_chart(fig_categories, use_container_width=True, key="categories_bar_chart")
        
        with col4:
            if 'AccountName' in filtered_df.columns:
                fig_accounts = plot_account_comparison(filtered_df)
                if fig_accounts:
                    st.plotly_chart(fig_accounts, use_container_width=True, key="accounts_area_chart")
            else:
                fig_weekday = plot_weekday_analysis(filtered_df)
                st.plotly_chart(fig_weekday, use_container_width=True, key="weekday_default_chart")
        
        # Ligne 3 : Analyse hebdomadaire + Tendance mensuelle
        col5, col6 = st.columns(2)
        
        with col5:
            fig_weekday = plot_weekday_analysis(filtered_df)
            st.plotly_chart(fig_weekday, use_container_width=True, key="weekday_analysis_chart")
        
        with col6:
            if monthly_df is not None:
                fig_monthly = plot_monthly_trend(monthly_df)
                if fig_monthly:
                    st.plotly_chart(fig_monthly, use_container_width=True, key="monthly_trend_chart")
        
    
    # Section tableau détaillé
    st.markdown("---")
    st.subheader("📋 Top 10 Services - Détails")
    
    top_services_table = show_top_services_table(filtered_df)
    st.dataframe(top_services_table, use_container_width=True)
    
    # Section téléchargement
    st.markdown("---")
    st.subheader("💾 Exporter les Données")
    
    col_export1, col_export2 = st.columns(2)
    
    with col_export1:
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Télécharger les données filtrées (CSV)",
            data=csv,
            file_name=f"finops_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    with col_export2:
        top_csv = top_services_table.to_csv().encode('utf-8')
        st.download_button(
            label="📥 Télécharger le top 10 services (CSV)",
            data=top_csv,
            file_name=f"top_services_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
        
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: gray;'>
            <p>FinOps Dashboard v1.0 | Données mises à jour le {}</p>
        </div>
    """.format(datetime.now().strftime('%d/%m/%Y à %H:%M')), unsafe_allow_html=True)


if __name__ == "__main__":
    main()