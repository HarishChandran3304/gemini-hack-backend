import requests

URL = "https://harish3304-gemini-cook.hf.space/embeddings"

def get_embeddings(text: str) -> list[float]:
    response = requests.post(URL, json={"sentence": text})
    return response.json()["embedding"]

if __name__ == "__main__":
    print(get_embeddings("Hello, how are you doing?"))