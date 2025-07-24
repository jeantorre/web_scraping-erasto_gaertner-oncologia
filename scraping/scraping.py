import requests
from bs4 import BeautifulSoup

URL_BASE = "https://guiafarmaco.erastogaertner.com.br/antineoplasicos/protocolos"


def get_protocol_numbers():
    response = requests.get(URL_BASE)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    main_div = soup.find("div", class_="col-md-12")
    if not main_div:
        print("Container não encontrado.")
        return []

    numero_protocolos = [
        a["href"].rstrip("/").split("/")[-1]
        for a in main_div.find_all("a", href=True)
        if a["href"].rstrip("/").split("/")[-1].isdigit()
    ]
    return numero_protocolos


if __name__ == "__main__":
    protocol_numbers = get_protocol_numbers()
    print(protocol_numbers)
    # full_urls = [f"{URL_BASE}{num}" for num in protocol_numbers]
    # print("Full URLs:", full_urls)
