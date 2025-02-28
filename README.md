
**README.md**  
# Moniteur de Prix Amazon 📈  

## Description  
Cette application permet de surveiller les meilleures ventes de produits sportifs sur Amazon et d'afficher les variations de prix. Une alerte par email peut être envoyée en cas de changement de prix.

## Fonctionnalités  
- Scraping des prix des produits Amazon Bestsellers (Sports, Jeux vidéo et Electronics)  
- Affichage des données actuelles et des historiques de prix  
- Graphique des variations de prix  
- Export des données en CSV  
- Envoi d'alertes par email en cas de changement de prix  

## Installation  
1. **Cloner le projet**  
   ```bash
   git clone https://github.com/BandouFranck10/Scrapping/
   cd monitor
   ```  

2. **Créer un environnement virtuel**  
   ```bash
   python -m venv venv
   source venv/bin/activate  # Sur macOS/Linux
   venv\Scripts\activate     # Sur Windows
   ```  

3. **Installer les dépendances**  
   ```bash
   pip install -r requirements.txt
   ```  

## Configuration de l'email  
Modifiez les variables suivantes dans le fichier de l'application pour utiliser votre adresse Gmail :
```python
EMAIL_SENDER = "tonemail@gmail.com"
EMAIL_PASSWORD = "tonmotdepasse"
```
⚠️ **Conseil** : Utilisez un mot de passe d'application Google pour éviter d'exposer votre mot de passe principal.

## Lancement de l'application  
```bash
streamlit run app.py
```
L'application sera accessible sur `http://localhost:8501/`.

## Export des données  
- Cliquez sur le bouton "📤 Exporter en CSV" pour sauvegarder les prix en local.

## Téléchargement  
Vous pouvez télécharger ce projet en format ZIP en cliquant [ici](https://github.com/BandouFranck10/Scrapping/archive/refs/heads/main.zip).

## Auteurs  
Développé par [BANDOU Franck; FARAITINI Justin; LOUSSINGUI Merveille]  

