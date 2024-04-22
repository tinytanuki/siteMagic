from bs4 import BeautifulSoup
import requests
import pandas as pd

def get_card_details_from_playin(card_name):
    """
    Effectue une recherche sur Play-in avec le nom de la carte et renvoie les détails.
    """
    search_url = f"https://www.play-in.com/fr/rech.php?search={card_name.replace(' ', '+')}"
    print(search_url)
    response = requests.get(search_url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        # Trouver l'élément avec le lien de la carte en supposant qu'il soit unique
        card_link_element = soup.find('a', text=card_name)  # Ce sélecteur est fictif
        if card_link_element:
            card_page_url = f"https://www.play-in.com{card_link_element['href']}"

            # Assumer que l'image est un voisin direct dans le DOM
            img_element = card_link_element.find_next('img')  # Ce sélecteur est fictif
            if img_element:
                img_url = img_element['src'] if img_element['src'].startswith(
                    'http') else f"https://www.play-in.com{img_element['src']}"

                # Assumer que le prix est proche dans le DOM
                price_element = card_link_element.find_next('span', class_='price')  # Ce sélecteur est fictif
                price = price_element.text.strip() if price_element else 'Prix non trouvé'

                return {
                    'Play-in URL': card_page_url,
                    'Image URL': img_url,
                    'Prix': price
                }

    return None


import requests
import pandas as pd


def get_card_details_from_scryfall(card_name):
    """
    Recherche les détails de la carte sur Scryfall à partir du nom de la carte.
    """
    api_url = f"https://api.scryfall.com/cards/named?exact={card_name}"
    response = requests.get(api_url)

    if response.status_code == 200:
        card_data = response.json()
        return {
            'Scryfall URL': card_data['scryfall_uri'],
            'Image URL': card_data['image_uris']['normal'],
            'Prix': card_data['prices']['eur']  # Prix en euros, si disponible
        }
    else:
        print(f"Erreur lors de la recherche de la carte : {card_name} sur Scryfall.")
        return None


def update_csv_with_card_details(input_csv_path, output_csv_path):
    df = pd.read_csv(input_csv_path)

    # Ajouter les nouvelles colonnes au DataFrame
    df['Scryfall URL'] = ''
    df['Image URL'] = ''
    df['Prix'] = ''

    for index, row in df.iterrows():
        card_name = row['Name']

        # Obtenir les détails de la carte de Scryfall
        card_details = get_card_details_from_scryfall(card_name)
        if card_details:
            # Mettre à jour le DataFrame avec les détails récupérés
            df.at[index, 'Scryfall URL'] = card_details['Scryfall URL']
            df.at[index, 'Image URL'] = card_details['Image URL']
            df.at[index, 'Prix'] = card_details['Prix']
        else:
            print(f"Détails non trouvés pour la carte : {card_name}")

    # Écrire le DataFrame mis à jour dans un nouveau fichier CSV
    df.to_csv(output_csv_path, index=False)
    print(f"CSV updated and saved to {output_csv_path}")



def update_csv_with_card_details_KO(input_csv_path, output_csv_path):
    df = pd.read_csv(input_csv_path)

    # Ajouter les nouvelles colonnes au DataFrame
    df['Play-in URL'] = ''
    df['Image URL'] = ''
    df['Prix'] = ''

    for index, row in df.iterrows():
        card_name = row['Name']

        # Obtenir les détails de la carte de Play-in
        card_details = get_card_details_from_playin(card_name)
        if card_details:
            # Mettre à jour le DataFrame avec les détails récupérés
            df.at[index, 'Play-in URL'] = card_details['Play-in URL']
            df.at[index, 'Image URL'] = card_details['Image URL']
            df.at[index, 'Prix'] = card_details['Prix']
        else:
            print(f"Détails non trouvés pour la carte : {card_name}")

    # Écrire le DataFrame mis à jour dans un nouveau fichier CSV
    df.to_csv(output_csv_path, index=False)
    print(f"CSV updated and saved to {output_csv_path}")

def generate_html_file_from_Manabox(csv_path, deckname, decklist, html_filename="manabox.html", css_filename="style.css"):
    '''
    :param csv_path:
    :param deckname:
    :param html_filename:
    :param css_filename:
    :return: génère un fichier HTML à partir d'un extract ManaBox
    '''
    df = pd.read_csv(csv_path)

    # Générer le HTML pour le menu de navigation
    nav_menu_html = '<nav><ul>'
    nav_menu_html += '<li><a href="index.html"><i class="fas fa-home"></i> Accueil</a></li>'  # Icône maison

    for deck in decklist:
        nav_menu_html += f'<li><a href="{deck}.html">{deck.capitalize()}</a></li>'  # Lien pour chaque deck

    nav_menu_html += '</ul></nav>'
    print(nav_menu_html)
    # Le début du contenu HTML
    html_content = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <title>{deckname} - Collection Magic: The Gathering</title>
        <link href="https://fonts.googleapis.com/css2?family=Gochi+Hand&family=Roboto:wght@400;700&display=swap" rel="stylesheet">
        <link rel="stylesheet" href="{css_filename}">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.1/css/all.min.css">
        <style>
            /* Votre CSS ici */
            #popup-img-container {{
                display: none; /* Caché par défaut */
                position: fixed; /* Pour s'afficher par-dessus tout */
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.8); /* Fond sombre semi-transparent */
                z-index: 1000; /* S'assurer qu'il est au-dessus des autres éléments */
                justify-content: center;
                align-items: center;
            }}
            #popup-img {{
                max-width: 80%; /* Ajustez en fonction de la taille souhaitée */
                max-height: 80%;
            }}
        </style>
        <script>
            function openPopup(src) {{
                document.getElementById('popup-img').src = src;
                document.getElementById('popup-img-container').style.display = 'flex';
            }}
            function closePopup() {{
                document.getElementById('popup-img-container').style.display = 'none';
            }}
        </script>
    </head>
    <body>
        <h1>Mon deck Magic : The Gathering - {deckname}</h1>
        {nav_menu_html}
        <div class="cards-container">
    """

    for _, row in df.iterrows():
        html_content += f'''
        <div class="card">
            <h2>{row['Name']}</h2>
            <img src='{row['Image URL']}' alt='{row['Name']}' onclick="openPopup('{row['Image URL']}')"/>
            <p>Edition : {row['Set name']} ({row['Set code']}) <br>
            <p>Carte n° {row['Collector number']} / {row['Rarity']}<br>
            <a href='{row['Scryfall URL']}'>Voir sur Scryfall</a><br>
            Prix : {row['Purchase price']} € | Prix Play-in : {row['Prix']}</p>
        </div>
        '''

    html_content += """
    </div>
    <div id="popup-img-container" onclick="closePopup()">
        <img id="popup-img" src="" alt="Image agrandie" />
    </div>
</body>
</html>
    """

    with open(html_filename, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"Le fichier HTML {html_filename} a été généré avec succès.")



# Chemin d'accès au CSV d'entrée et de sortie
deck_names = ["Arahbo", "Brille-Paume", "Ajani protecteur valeureux", "Nissa artisane de la nature"]
for deck in deck_names :
    # Mise à jour du CSV
    csv_input_path = 'Decks/' + deck + '.csv'
    csv_output_path = 'Decks/' + deck + '-updated.csv'
    update_csv_with_card_details(csv_input_path, csv_output_path)

    # Génération du fichier HTML à partir du CSV mis à jour
    generate_html_file_from_Manabox(csv_output_path, deck, deck_names, deck + ".html")
