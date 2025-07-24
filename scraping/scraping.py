import polars as pl
import requests
from bs4 import BeautifulSoup

URL_BASE = "https://guiafarmaco.erastogaertner.com.br/antineoplasicos/protocolos"


def get_numero_protocolo():
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


def scraping_detalhes_protocolo(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    div_principal = soup.find("div", class_="col-md-12")
    if not div_principal:
        print("Container não encontrado.")
        return None

    tag_titulo = div_principal.find("h2", class_="title")
    nome_protocolo = (
        tag_titulo.get_text(strip=True)
        if tag_titulo
        else "Nome do protocolo não encontrado"
    )
    nome_protocolo = nome_protocolo.replace("\xa0", " ")

    secoes = {}
    for h3 in div_principal.find_all("h3", class_="subtitle"):
        titulo_secao = h3.get_text(strip=True).replace("\xa0", " ")
        conteudo_secao = []
        for sibling in h3.find_next_siblings():
            if sibling.name == "h3":
                break
            if sibling.name == "p":
                conteudo_secao.append(sibling.get_text(strip=True).replace("\xa0", " "))
            elif sibling.name == "ul":
                items = [
                    li.get_text(strip=True).replace("\xa0", " ")
                    for li in sibling.find_all("li")
                ]
                conteudo_secao.extend(items)
            elif sibling.name == "ol":
                items = [
                    li.get_text(strip=True).replace("\xa0", " ")
                    for li in sibling.find_all("li")
                ]
                conteudo_secao.extend(items)
        secoes[titulo_secao] = conteudo_secao

    return {"nome_protocolo": nome_protocolo, "secoes": secoes}


if __name__ == "__main__":
    qtd_protocolos = get_numero_protocolo()
    print(f"Encontrados {len(qtd_protocolos)} protocolos.")

    url_completa = [f"{URL_BASE}/{num}" for num in qtd_protocolos]

    linhas = []
    for url in url_completa:
        data = scraping_detalhes_protocolo(url)
        if data:
            nome_protocolo = data["nome_protocolo"]
            for secao, lista_conteudo in data["secoes"].items():
                for conteudo in lista_conteudo:
                    linhas.append(
                        {
                            "nome_protocolo": nome_protocolo,
                            "section": secao,
                            "content": conteudo,
                        }
                    )
    df = pl.DataFrame(linhas)
    df.write_csv("protocols.csv")
    print("Exportado para protocols.csv")
