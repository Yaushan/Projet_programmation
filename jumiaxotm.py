from jumiaxo import scrape_jumia
import requests
from bs4 import BeautifulSoup
import pandas as pd

#####Scrapping des commentaires des 5 produits les plus évalués


df = scrape_jumia()

df["Prix (FCFA)"] = pd.to_numeric(df["Prix (FCFA)"], errors="coerce").fillna(0)
df["Note"] = pd.to_numeric(df["Note"], errors="coerce").fillna(0)
df["Nombre_Evaluation"] = pd.to_numeric(df["Nombre_Evaluation"], errors="coerce").fillna(0).astype(int)
#df_filtered = df[df['Nombre_Evaluation'] != ""]

# Trier par "Nombre_Evaluation" en ordre décroissant
df_sorted = df.sort_values(by='Nombre_Evaluation', ascending=False)

# Sélectionner les 50 premières lignes
top_5 = df_sorted.head(5)

print(top_5["Lien"])
# Initialize the result list
l = []

# Loop through the top 5 links
for url in top_5["Lien"]:
    comments = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    # Fetch the main page
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch {url}")
        continue

    soup = BeautifulSoup(response.text, "html.parser")
    try:
        linkk = soup.find('a', class_='btn _def _ti -mhs -fsh0').get('href')
        link = f'https://www.jumia.ci{linkk}'

        # Fetch the linked page
        response2 = requests.get(link, headers=headers)
        if response2.status_code != 200:
            print(f"Failed to fetch {link}")
            continue

        soup2 = BeautifulSoup(response2.text, "html.parser")

        # Find the last page index
        last_page_links = soup2.find_all('a', class_="pg")
        last_page = 1
        for page_link in last_page_links:
            if page_link.get("aria-label") == "Dernière page":
                last_page = int(page_link.get("href").split('=')[-1])
                break

        # Loop through all pages
        for page in range(1, last_page + 1):
            paginated_url = f"{link}&page={page}"
            response3 = requests.get(paginated_url, headers=headers)
            if response3.status_code != 200:
                print(f"Failed to fetch {paginated_url}")
                continue

            soup3 = BeautifulSoup(response3.text, "html.parser")
            articles = soup3.find_all("article", class_="-pvs -hr _bet")

            # Extract comments
            for article in articles:
                comment = article.find("p", class_="-pvs")
                if comment:
                    comments.append(comment.text)

    except AttributeError as e:
        print(f"Error processing {url}: {e}")
        continue

    l.append(comments)

# Output the result
print(l)
