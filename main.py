from bs4 import BeautifulSoup
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
        card_type = card_data['type_line'].split(' — ')[0]  # Prend la partie avant le '—' si présent

        # Gérer les cartes à double face qui n'ont pas 'image_uris' mais 'card_faces'
        if 'image_uris' not in card_data:
            # Vérifiez s'il s'agit d'une carte à double face avec 'card_faces'
            if 'card_faces' in card_data:
                image_url = card_data['card_faces'][0]['image_uris']['border_crop']  # Prend l'image du premier côté
            else:
                # Si 'card_faces' n'est pas présent non plus, il y a un problème avec la carte
                print(f"La carte {card_name} n'a pas d'images disponibles.")
                return None
        else:
            image_url = card_data['image_uris']['border_crop']
        return {
            'Scryfall URL': card_data['scryfall_uri'],
            'Image URL': image_url,
            'Prix': card_data['prices']['eur'],  # Prix en euros, si disponible
            'Type': card_type  # Ajout du type de la carte
        }
    else:
        print(f"Erreur lors de la recherche de la carte : {card_name} sur Scryfall.")
        return None


def update_csv_with_card_details(input_csv_path, output_csv_path):
    df = pd.read_csv(input_csv_path)
    # Trier le DataFrame par la colonne 'Name' ou par la colonne appropriée contenant le nom des cartes
    df_sorted = df.sort_values(by='Name', ascending=True)

    # Ajouter les nouvelles colonnes au DataFrame si elles n'existent pas
    if 'Type' not in df.columns:
        df['Type'] = ''
    if 'Scryfall URL' not in df.columns:
        df['Scryfall URL'] = ''
    if 'Image URL' not in df.columns:
        df['Image URL'] = ''
    if 'Prix' not in df.columns:
        df['Prix'] = ''

    for index, row in df.iterrows():
        card_name = row['Name']
        print(card_name)
        # Obtenir les détails de la carte de Scryfall
        card_details = get_card_details_from_scryfall(card_name)
        if card_details:
            # Mettre à jour le DataFrame avec les détails récupérés
            df.at[index, 'Type'] = card_details['Type']
            df.at[index, 'Scryfall URL'] = card_details['Scryfall URL']
            df.at[index, 'Image URL'] = card_details['Image URL']
            df.at[index, 'Prix'] = card_details['Prix']
        else:
            print(f"Détails non trouvés pour la carte : {card_name}")

    # Écrire le DataFrame mis à jour dans un nouveau fichier CSV
    df.to_csv(output_csv_path, index=False)
    print(f"CSV updated and saved to {output_csv_path}")


def generate_html_file_from_Manabox(csv_path, deckname, decklist, deck_icons, deck_commander="None", html_filename="Manabox_Collection.html", css_filename="style.css"):
    # génère un fichier HTML à partir d'un extract ManaBox
    df = pd.read_csv(csv_path)
    # Trier le DataFrame par la colonne 'Name' ou par la colonne appropriée contenant le nom des cartes
    df_sorted = df.sort_values(by='Name', ascending=True)

    # Compter le nombre total de cartes et organiser par type
    total_cards = len(df)
    card_types = df['Name'].value_counts()  # Assurez-vous que vous avez une colonne 'Type' dans votre CSV

    # Regrouper les cartes par type
    grouped_df = df.groupby('Type')

    # Générer le HTML pour le menu de navigation
    nav_menu_html = '<nav><ul>\n'
    nav_menu_html += '            <li><a href="index.html"><i class="fas fa-home"></i> Accueil</a></li>'  # Icône maison

    for i, deck in enumerate(decklist):
        deck_icon = deck_icons[i]
        nav_menu_html += f"""
        <li><a href="{deck}.html"><i class="{deck_icon}"></i> {deck.capitalize()}</a></li>"""
    nav_menu_html += '\n        </ul></nav>'

    # Obtenir les détails de la carte commandant
    if deck_commander != "None":
        commander_details = get_card_details_from_scryfall(deck_commander)

    # Le début du contenu HTML
    html_content = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <title>{deckname} - Collection Magic: The Gathering</title>
        <link href="https://fonts.googleapis.com/css2?family=Belleza&family=Cinzel&family=MedievalSharp&display=swap" rel="stylesheet">
        <link rel="stylesheet" href="{css_filename}">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.1/css/all.min.css">
        <style>
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
    """
    if deck_commander == "None":
        html_content += f"""
        <h1>Magic : The Gathering - Ma {deckname}</h1>
        <center><h2>Total de cartes : {total_cards}</h2></center>
        {nav_menu_html}
    """
    else:
        html_content += f"""
        <h1>Mon deck Magic : The Gathering - {deckname}</h1>
        <center><h2>Total de cartes : {total_cards}</h2></center>
        {nav_menu_html}
        <h2>Commandant : {deck_commander}</h2>
        <div class="cards-container">
            <div class="card">
                <img src="{commander_details['Image URL']}" alt="{deck_commander}" onclick="openPopup('{commander_details['Image URL']}')"/>
                <a href='{commander_details['Scryfall URL']}'>Voir sur Scryfall</a><br>
            </div>
        </div>
    """

    # Boucle sur chaque groupe de types de cartes
    for card_type, group in grouped_df:
        type_count = len(group)  # Obtenez le nombre de cartes de ce type

        if type_count > 1:
            if card_type == "Sorcery":
                card_type_plural = "Sorceries"
            else :
                card_type_plural = card_type + 's'    # Ajouter un "s" si nécessaire
        else:
            card_type_plural = card_type


        html_content += f'''
        <h2>{card_type_plural} ({type_count})</h2>
        <div class="cards-container">'''
        for _, card in group.iterrows():
            html_content += f'''
            <div class="card">
                <h3>{card['Name']}</h3>
                <img src="{card['Image URL']}" alt="{card['Name']}" onclick="openPopup('{card['Image URL']}')"/>
                <p>Edition : {card['Set name']} ({card['Set code']}) <br>
                Rareté : {card['Rarity'][0].upper()}{card['Rarity'][1:]}<br>
                <a href='{card['Scryfall URL']}'>Voir sur Scryfall</a><br>
                Prix : {card['Purchase price']} € | Prix Play-in : {card['Prix']} €</p>
                <p>Carte n° {card['Collector number']}<br>
                Quantité : {card['Quantity']}</p>
            </div>
            '''
        html_content += f'''
        </div>
        '''

    html_content += """
    </div>
    <div id="popup-img-container" onclick="closePopup()">
        <img id="popup-img" src="" alt="Image agrandie" />
    </div>
    <button onclick="topFunction()" id="myBtn" title="Retour en haut">
        <i class="fas fa-chevron-up"></i>
    </button>
    <script>
    //Quand l'utilisateur scroll vers le bas de 20px depuis le haut du document, afficher le bouton
    window.onscroll = function() {scrollFunction()};

    function scrollFunction() {
      if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
        document.getElementById("myBtn").style.display = "block";
      } else {
        document.getElementById("myBtn").style.display = "none";
      }
    }

    // Quand l'utilisateur clique sur le bouton, scroll en haut du document
    function topFunction() {
    const scrollDuration = 600; // durée du scroll en ms
    const scrollStep = -window.scrollY / (scrollDuration / 15), // calcule la distance de chaque étape
        scrollInterval = setInterval(function(){
        if ( window.scrollY != 0 ) {
            window.scrollBy( 0, scrollStep );
        }
        else clearInterval(scrollInterval); 
    },15);
    }
    </script>
</body>
</html>
    """
    with open(html_filename, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"Le fichier HTML {html_filename} a été généré avec succès.")

# Chemin d'accès au CSV d'entrée et de sortie
deck_names = ["Arahbo", "Brille-Paume", "Ajani protecteur valeureux", "Nissa artisane de la nature", "ManaBox_Collection", "Wishlist Arahbo", "Wishlist Brille-Paume"]
deck_icons = ["fas fa-cat", "fas fa-star", "fas fa-shield-alt", "fas fa-leaf", "fas fa-book", "fas fa-star", "fas fa-star"]
deck_commanders = ["Arahbo, Roar of the World", "Bright-Palm, Soul Awakener", "Ajani, Valiant Protector", "Nissa, Nature's Artisan", "None", "None", "None"]


# Construction de la liste des dictionnaires
deck_list = []
for i in range(len(deck_names)) :
    deck = {
        "Nom" : deck_names[i],
        "Commander" : deck_commanders[i],
        "Icone" : deck_icons[i]
    }
    deck_list.append(deck)
    print(deck)
    # Mise à jour du CSV
    csv_input_path = 'Decks/' + deck['Nom'] + '.csv'
    csv_output_path = 'Decks/' + deck['Nom'] + '-updated.csv'
    update_csv_with_card_details(csv_input_path, csv_output_path)

    # Génération du fichier HTML à partir du CSV mis à jour
    generate_html_file_from_Manabox(csv_output_path, deck['Nom'], deck_names, deck_icons, deck['Commander'], deck['Nom'] + ".html")
