import requests
import sys

server_url = "http://127.0.0.1/shorten"


def shorten_url(url):
    """Envia a URL ao servidor Flask e captura a resposta"""
    try:
        response = requests.post(server_url, json={"url": url})

        if response.status_code == 200:
            print(f"URL encurtada com sucesso: {response.json().get('short_url')}")
        else:
            print(f"Erro: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Erro ao enviar a URL: {e}")


if __name__ == "__main__":
   while True:
        r = input("Digite a URL para encurtar (ou digite 'sair' para encerrar): ")
        if r.lower() == "sair":
            print("Encerrando...")
            break
        shorten_url(r)
