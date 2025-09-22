import ollama
import requests                  
from bs4 import BeautifulSoup 

message = "You are a summarization assistant. I will give you the content of a website in text form, " \
"and your task is to carefully read through it and provide me with a complete summary. Focus on the main points, key arguments, " \
"and essential insights while omitting unnecessary details. Your summary should be clear, well-structured, and easy to understand, " \
"so that I can quickly grasp the overall meaning of the website."

headers = {
 "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}

class Website:
    def __init__(self, url):
        self.url = url
        try:
            response = requests.get(url, headers=headers, timeout=30)  
            response.raise_for_status()  
        except requests.exceptions.RequestException as e:
            print(f"[Error] Failed to fetch {url}: {e}")
            self.title = "No title"
            self.text = ""
            return
        
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
            self.title = soup.title.string.strip() if soup.title and soup.title.string else "No title found"

            body = soup.body
            if body:
                for irrelevant in body(["script", "style", "img", "input", "noscript"]):
                    irrelevant.decompose()
                self.text = body.get_text(separator="\n", strip=True)
            else:
                self.text = soup.get_text(separator="\n", strip=True)
        except Exception as e:
            print(f"[Error] Failed to parse HTML: {e}")
            self.title = "No title"
            self.text = ""

try:
    url = input("Enter a website URL: ").strip()
    ed = Website(url)

    if not ed.text:
        raise ValueError("No text extracted from website, cannot summarize.")
    messages = [
        {"role": "system", "content": message},
        {"role": "user", "content": f"WEBSITE TITLE: {ed.title}\n\nWEBSITE TEXT:\n{ed.text}"}
    ]

    try:
        response = ollama.chat(model="llama3.2", messages=messages)
        print(response['message']['content'])
    except Exception as e:
        print(f"[Error] Ollama summarization failed: {e}")

except Exception as e:
    print(f"[Error] {e}")
