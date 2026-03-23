
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

st.set_page_config(layout="wide")

# 1. Chargement et préparation des données (adapté de votre notebook)
@st.cache_data
def load_and_preprocess_data():
    # ATTENTION: Remplacez ce chemin par le chemin LOCAL de votre fichier Dataset.csv
    df = pd.read_csv('Dataset.csv') # Exemple: 'Dataset.csv' si dans le même dossier, ou 'C:/Users/VotreNom/Documents/Dataset.csv'
    df["TransactionStartTime"] = pd.to_datetime(df["TransactionStartTime"])
    df['Date'] = df['TransactionStartTime'].dt.date
    df['Hour'] = df['TransactionStartTime'].dt.hour
    df['Day'] = df['TransactionStartTime'].dt.day
    df['Month'] = df['TransactionStartTime'].dt.month # Kept for consistency, but will be dropped later

    # Set index and drop TransactionStartTime and Month as in notebook
    df.index = df['Date']
    df.drop(['TransactionStartTime', 'Month'], axis=1, inplace=True)

    # Calculate Marge_Brute
    df['Marge_Brute'] = df['Amount'] - df['Value']

    return df

df_original = load_and_preprocess_data()

st.title("Dashboard Interactif - Analyse des Transactions")

# 2. Sidebar - Filtres dynamiques
st.sidebar.header("Filtres")

df = df_original.copy() # Work on a copy for filtering

# Conversion Date si présente
if 'Date' in df.columns:
    # Ensure 'Date' column is datetime type for filtering
    df['Date'] = pd.to_datetime(df['Date'])
    date_min_available = df['Date'].min()
    date_max_available = df['Date'].max()

    date_range_selection = st.sidebar.date_input("Filtrer par Date",
                                                [date_min_available, date_max_available],
                                                min_value=date_min_available,
                                                max_value=date_max_available)

    if len(date_range_selection) == 2:
        start_date, end_date = date_range_selection
        df = df[(df['Date'] >= pd.to_datetime(start_date)) & (df['Date'] <= pd.to_datetime(end_date))]

# Filtres catégoriels multiples
colonnes_categorique = df.select_dtypes(include=['object', 'category']).columns.tolist()
# Remove 'Date' if it was treated as object before conversion to datetime
if 'Date' in colonnes_categorique: colonnes_categorique.remove('Date')

for col in colonnes_categorique:
    if col in df.columns: # Check if column still exists after date filtering
        valeurs = df[col].unique().tolist()
        selection = st.sidebar.multiselect(f"Filtrer par {col}", valeurs, default=valeurs)
        df = df[df[col].isin(selection)]

# Affichage des données brutes après filtrage
st.subheader("Aperçu des données brutes (filtrées)")
st.dataframe(df.head())

# --- Intégration des analyses spécifiques de votre notebook ---

st.header("Analyses du Notebook")

# 1. Moyenne des revenus par catégorie de produit
st.subheader("1. Moyenne des revenus par catégorie de produit")
revenue_per_category_m = df.groupby('ProductCategory')['Value'].mean().sort_values(ascending=False)
fig_rev_cat_m = px.bar(revenue_per_category_m,
                       x=revenue_per_category_m.index,
                       y='Value',
                       title="Moyenne des revenus par catégorie de produit",
                       labels={'index': 'Catégorie de Produit', 'Value': 'Moyenne des Revenus'})
st.plotly_chart(fig_rev_cat_m, use_container_width=True)

# 2. Marge brute totale par catégorie
st.subheader("2. Marge brute totale par catégorie")
marge_brute_cat_s = df.groupby('ProductCategory')['Marge_Brute'].sum().sort_values(ascending=True)
fig_marge_cat_s = px.bar(marge_brute_cat_s,
                         x=marge_brute_cat_s.index,
                         y='Marge_Brute',
                         title="Marge brute totale par catégorie",
                         labels={'index': 'Catégorie de Produit', 'Marge_Brute': 'Marge Brute Totale'})
st.plotly_chart(fig_marge_cat_s, use_container_width=True)

# 3. Nombre de transactions par jour
st.subheader("3. Nombre de transactions par jour")
transactions_per_day = df.groupby('Day').size().sort_values(ascending=False)
fig_trans_day = px.bar(transactions_per_day,
                       x=transactions_per_day.index,
                       y=transactions_per_day.values,
                       title="Nombre de transactions par jour",
                       labels={'x': 'Jour du mois', 'y': 'Nombre de Transactions'})
st.plotly_chart(fig_trans_day, use_container_width=True)

# 4. Nombre de remboursements par catégorie de produit
st.subheader("4. Nombre de remboursements par catégorie de produit")
remboursements = df[df['Amount'] < 0]
remboursements_by_category = remboursements.groupby('ProductCategory').size().sort_values(ascending=False)
st.dataframe(remboursements_by_category.reset_index().rename(columns={0: 'Nombre de Remboursements'}))

# 5. Marge moyenne par jour
st.subheader("5. Marge moyenne par jour")
marge_brute_jour_m = df.groupby('Day')['Marge_Brute'].mean().sort_values(ascending=True)
fig_marge_day_m = px.bar(marge_brute_jour_m,
                         x=marge_brute_jour_m.index,
                         y='Marge_Brute',
                         title="Marge moyenne par jour",
                         labels={'index': 'Jour du mois', 'Marge_Brute': 'Marge Brute Moyenne'})
st.plotly_chart(fig_marge_day_m, use_container_width=True)

# Informations supplémentaires
st.subheader("Informations Clés")
total_amount = df['Amount'].sum()
total_value = df['Value'].sum()

st.write(f"Montant total collecté (après filtres) : {total_amount:.2f} UGX")
st.write(f"Montant total des produits/services (après filtres) : {total_value:.2f} UGX")
st.write(f"Ratio Amount/Value (après filtres) : {(total_amount / total_value) * 100:.2f} %")

# --- Graphiques interactifs généraux (du fichier APP.PY original) ---

st.header("Graphiques Interactifs Généraux")

colonnes_numerique = df.select_dtypes(include=['float64', 'int64']).columns.tolist()

col_x = st.selectbox("Variable X (catégorique pour barplot, pie chart)", colonnes_categorique)
col_y = st.selectbox("Variable Y (numérique pour histogramme, barplot, line chart)", colonnes_numerique)
col_color = st.selectbox("Variable couleur (optionnel pour histogramme)", [None] + colonnes_categorique)

# Ligne de tendance par date (si la colonne Date est disponible et numérique)
if 'Date' in df.columns and col_y:
    st.subheader(f"Évolution temporelle de {col_y}")
    # Group by date and calculate mean of col_y
    line_data = df.groupby(df['Date'].dt.date)[col_y].mean().reset_index()
    line_data['Date'] = pd.to_datetime(line_data['Date']) # Convert back to datetime for plotly
    fig_line = px.line(line_data, x='Date', y=col_y, title=f"Moyenne de {col_y} au fil du temps")
    st.plotly_chart(fig_line, use_container_width=True)

# Histogramme
st.subheader("Histogramme interactif")
if col_y:
    fig_hist = px.histogram(df, x=col_y, color=col_color, nbins=30, title=f"Distribution de {col_y}")
    st.plotly_chart(fig_hist, use_container_width=True)

# Barplot (moyenne par catégorie)
st.subheader("Moyenne par catégorie (personnalisable)")
if col_x and col_y:
    agg_data = df.groupby(col_x)[col_y].mean().reset_index()
    fig_bar = px.bar(agg_data, x=col_x, y=col_y, color=col_x, title=f"Moyenne de {col_y} par {col_x}")
    st.plotly_chart(fig_bar, use_container_width=True)

# Heatmap de corrélation
st.subheader("Heatmap de Corrélation")
if len(colonnes_numerique) > 1:
    corr = df[colonnes_numerique].corr()
    fig_corr, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax)
    st.pyplot(fig_corr)
else:
    st.write("Pas assez de colonnes numériques pour générer une heatmap de corrélation.")

# Pie chart
st.subheader("Répartition des catégories (personnalisable)")
if col_x:
    fig_pie = px.pie(df, names=col_x, title=f"Répartition de {col_x}")
    st.plotly_chart(fig_pie, use_container_width=True)

# 5. Analyse tabulaire
st.subheader("Analyse Tabulaire")
# Ensure 'groupby_col' is available in the current filtered dataframe
available_groupby_cols = [col for col in colonnes_categorique if col in df.columns]
if available_groupby_cols:
    groupby_col_table = st.selectbox("Grouper par (pour le tableau)", available_groupby_cols)
    agg_col_table = st.multiselect("Colonnes à agréger (pour le tableau)", colonnes_numerique, default=colonnes_numerique[:1] if colonnes_numerique else [])
    if groupby_col_table and agg_col_table:
        st.dataframe(df.groupby(groupby_col_table)[agg_col_table].agg(['mean', 'sum', 'count']).round(2))
else:
    st.write("Aucune colonne catégorique disponible pour l'analyse tabulaire.")

# 6. Données brutes
with st.expander("Aperçu des données brutes complètes (après filtres)"):
    st.dataframe(df)

# 7. Téléchargement des données filtrées
csv = df.to_csv(index=False).encode('utf-8')
st.download_button("Télécharger les données filtrées", csv, "transactions_filtrees.csv", "text/csv")