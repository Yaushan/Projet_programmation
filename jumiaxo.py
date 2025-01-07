def scrape_jumia():
    import requests
    from bs4 import BeautifulSoup
    import re
    import pandas as pd

    # URL cible
    url = "https://www.jumia.ci/catalog/?q=smartphone"

    # Envoyer une requête HTTP GET avec un en-tête User-Agent
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)

    # Vérification du succès de la requête
    if response.status_code == 200:
        # Trouver le nombre total de pages
        soup = BeautifulSoup(response.text, "html.parser")
        try:
            last_page_link = soup.find_all('a', class_='pg')[-1].get('href')
            match = re.search(r'page=(\d+)', last_page_link)
            last_page_index = int(match.group(1)) if match else 1
        except IndexError:
            last_page_index = 1  # Valeur par défaut si aucune page n'est trouvée

        # Initialiser un DataFrame pour stocker les données
        df = pd.DataFrame(columns=["Description", "Prix (FCFA)", "Note", "Nombre_Evaluation", "Marque", "Lien", "Cat1", "Cat2", "Cat3"])

        # Parcourir toutes les pages
        for i in range(1, last_page_index + 1):
            page_url = f"https://www.jumia.ci/catalog/?q=smartphone&page={i}"
            response = requests.get(page_url, headers=headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                prods = soup.find_all('a', class_="core")

                for prod in prods:
                    try:
                        # Extraire les informations du produit
                        nom = prod.get("data-gtm-name")  # Description
                        price = prod.find('div', class_='prc').text.strip()
                        numeric_price = float(re.sub(r'[^\d.]', '', price))

                        rating = prod.get("data-gtm-dimension27")  # Note
                        rating = rating if rating else "0"  # Remplacer les valeurs vides

                        reviews = prod.get("data-gtm-dimension26")  # Nombre d'évaluations
                        reviews = reviews if reviews else "0"  # Remplacer les valeurs vides

                        brand = prod.get("data-ga4-item_brand")  # Marque
                        link = f"https://www.jumia.ci{prod.get('href')}"  # Lien complet
                        cat1 = prod.get("data-ga4-item_category")  # Catégorie 1
                        cat2 = prod.get("data-ga4-item_category2")  # Catégorie 2
                        cat3 = prod.get("data-ga4-item_category3")  # Catégorie 3

                        # Ajouter les données au DataFrame
                        df = pd.concat(
                            [df, pd.DataFrame([[nom, numeric_price, rating, reviews, brand, link, cat1, cat2, cat3]], columns=df.columns)],
                            ignore_index=True
                        )

                    except AttributeError as e:
                        print(f"Informations manquantes pour un produit : {e}")
            else:
                print(f"Erreur HTTP : {response.status_code}")

        # Convertir les colonnes nécessaires et sauvegarder en CSV
        df1 = df 
        df1["Prix (FCFA)"] = df1["Prix (FCFA)"].astype(str).str.replace(".", ",", regex=False)
        df1["Note"] = df1["Note"].astype(str).str.replace(".", ",", regex=False)
        df1.to_csv("produits_jumia.csv", index=False, encoding="utf-8")
        print("Données enregistrées dans le fichier produits_jumia.csv")
        return df

    else:
        print(f"Erreur HTTP : {response.status_code}")
        return pd.DataFrame()  # Retourne un DataFrame vide en cas d'erreur


# Exécuter le script
if __name__ == "__main__":
    data = scrape_jumia()
    print(data.head())

