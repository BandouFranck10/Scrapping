import streamlit as st
import pandas as pd
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup
import os

# Configuration de l'email
EMAIL_SENDER = "tonemail@gmail.com"
EMAIL_PASSWORD = "tonmotdepasse"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# URL Amazon Bestsellers
url = "https://www.amazon.fr/gp/bestsellers/sports"


st.set_page_config(page_title="Moniteur de prix Amazon", page_icon="📈", layout="wide")
st.markdown("""
    <style>
    .big-title {
        font-size: 40px;
        font-weight: bold;
        color: #ff5733;
        text-align: center;
    }
    .small-text {
        font-size: 28px;
        color: #2c3e50;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<p class='big-title'>📊 Moniteur de prix Amazon</p>", unsafe_allow_html=True)
st.markdown("<p class='small-text'>Suivez les meilleures ventes des produits sportifs et soyez informé des variations de prix !</p>", unsafe_allow_html=True)

email_receiver = st.text_input("💌 Entrez l'adresse email pour les alertes :", "")

def send_email(product_name, old_price, new_price, email_receiver):
    if not email_receiver:
        st.warning("Veuillez entrer une adresse email valide.")
        return
    
    subject = "📢 Changement de prix détecté !"
    body = f"""
    Bonjour,

    Le prix du produit "{product_name}" a changé sur Amazon :

    - Ancien prix : {old_price} €
    - Nouveau prix : {new_price} €

    Vérifiez-le ici : {url}

    Cordialement,
    Amazon Price Tracker
    """

    msg = MIMEMultipart()
    msg["From"] = EMAIL_SENDER
    msg["To"] = email_receiver
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, email_receiver, msg.as_string())
        server.quit()
        st.success("📩 Email envoyé avec succès !")
    except Exception as e:
        st.error(f"⚠️ Erreur lors de l'envoi de l'email : {e}")

def scrapp(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return BeautifulSoup(response.content, "html.parser")
    except requests.exceptions.RequestException as e:
        st.error(f"Erreur lors de la récupération des données : {e}")
        return None

def extract_product(product_soup):
    try:
        # Extraction du titre
        title_element = product_soup.select_one("._cDEzb_p13n-sc-css-line-clamp-3_g3dy1") or \
                       product_soup.select_one("div[class*='p13n-sc-truncate-']")
        
        # Extraction du prix
        price_element = product_soup.select_one("._cDEzb_p13n-sc-price_3mJ9Z") or \
                       product_soup.select_one("span.a-price > span.a-offscreen")
        
        # Extraction de la note
        rating_element = product_soup.select_one(".a-icon-row .a-icon-alt")

        if title_element:
            title = title_element.text.strip()
            
            # Si le prix existe
            if price_element:
                price_text = price_element.text.strip()
                # Nettoyer le prix
                price_text = price_text.replace('€', '').replace(',', '.').strip()
                try:
                    price = float(price_text)
                except ValueError:
                    return None
            else:
                return None

            # Extraction de la note si elle existe
            rating = rating_element.text.strip() if rating_element else "Non noté"

            return {
                "Titre": title,
                "Prix": price,
                "Note": rating
            }
        return None
    except Exception as e:
        print(f"Erreur lors de l'extraction du produit : {e}")
        return None

def update_data():
    soup = scrapp(url)
    if not soup:
        return []
    
    # Utilisation d'un sélecteur plus précis pour les éléments de la grille
    products = soup.select("div.p13n-sc-uncoverable-faceout")
    
    # Debug: Afficher le nombre de produits trouvés
    print(f"Nombre de produits trouvés : {len(products)}")
    
    new_data = []
    for product in products:
        extracted = extract_product(product)
        if extracted:
            new_data.append(extracted)
            # Debug: Afficher chaque produit extrait
            print(f"Produit extrait : {extracted}")
    
    if new_data:
        new_df = pd.DataFrame(new_data)
        new_df.to_csv("historique_prix.csv", index=False)
        # Debug: Afficher le nombre total de produits extraits
        print(f"Nombre total de produits extraits : {len(new_data)}")
    
    return new_data

def load_previous_prices():
    if os.path.exists("historique_prix.csv"):
        try:
            df = pd.read_csv("historique_prix.csv")
            if df.empty:
                return pd.DataFrame(columns=["Titre", "Prix", "Note"])
            return df
        except (pd.errors.EmptyDataError, pd.errors.ParserError):
            return pd.DataFrame(columns=["Titre", "Prix", "Note"])
        except Exception as e:
            st.error(f"Erreur lors de la lecture du fichier CSV : {e}")
            return pd.DataFrame(columns=["Titre", "Prix", "Note"])
    return pd.DataFrame(columns=["Titre", "Prix", "Note"])




def calculate_price_variations(current_data, previous_data):
    variations = []
    
    for current_item in current_data:
        title = current_item["Titre"]
        current_price = current_item["Prix"]
        
        # Rechercher le produit dans les données précédentes
        previous_price = None
        if not previous_data.empty:
            product_history = previous_data[previous_data["Titre"] == title]
            if not product_history.empty:
                previous_price = product_history.iloc[-1]["Prix"]
        
        if previous_price is not None:
            variation = {
                "Titre": title,
                "Prix actuel": current_price,
                "Ancien prix": previous_price,
                "Variation": round(((current_price - previous_price) / previous_price) * 100, 2),
                "Date": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")
            }
            variations.append(variation)
    
    return variations

# Interface principale
col1, col2, col3 = st.columns(3)

with col1:
    update_button = st.button("🔄 Mettre à jour les données", help="Cliquez pour récupérer les dernières informations")

with col2:
    show_history = st.button("📈 Afficher l'historique des variations")

with col3:
    export_button = st.button("📤 Exporter en CSV")

if update_button:
    with st.spinner("⏳ Récupération des données en cours..."):
        data = update_data()
        if data:
            # Sauvegarder les données dans la session
            st.session_state.current_data = data
            
            # Affichage des données actuelles
            df = pd.DataFrame(data)
            st.subheader("📊 Prix actuels")
            st.dataframe(df)
            
            if "Prix" in df.columns and not df["Prix"].isnull().all():
                st.line_chart(df.set_index("Titre")["Prix"])

if show_history and hasattr(st.session_state, 'current_data'):
    previous_data = load_previous_prices()
    variations = calculate_price_variations(st.session_state.current_data, previous_data)
    
    if variations:
        st.subheader("📜 Historique des variations de prix")
        variations_df = pd.DataFrame(variations)
        
        def highlight_variations(val):
            if isinstance(val, float):
                if val > 0:
                    return 'color: red'
                elif val < 0:
                    return 'color: green'
                return ''
            return ''
        
        st.dataframe(variations_df.style.applymap(highlight_variations, subset=['Variation']))
        
        # Graphique des variations
        if len(variations) > 1:
            st.subheader("📈 Graphique des variations de prix")
            fig_data = pd.DataFrame(variations)
            st.line_chart(fig_data.set_index('Titre')['Variation'])
    else:
        st.info("Aucune variation de prix détectée pour le moment.")
elif show_history:
    st.warning("Veuillez d'abord mettre à jour les données avant d'afficher l'historique.")

if export_button and hasattr(st.session_state, 'current_data'):
    df = pd.DataFrame(st.session_state.current_data)
    df.to_csv("historique_prix.csv", index=False)
    st.success("✅ Fichier CSV exporté !")
elif export_button:
    st.warning("Veuillez d'abord mettre à jour les données avant d'exporter.")