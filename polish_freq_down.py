import requests
from bs4 import BeautifulSoup
import re

def download_polish_words(n=1000):
    url = "https://en.wiktionary.org/wiki/Wiktionary:Frequency_lists/Polish_wordlist"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the specific ol element containing the word list
    word_list = soup.find('ol')
    print(f"word_list: {word_list}")
    words = []
    if word_list:
        for li in word_list.find_all('li'):
            a_tag = li.find('a')
            if a_tag and 'title' in a_tag.attrs:
                word = a_tag['title']
                words.append(word)
            if len(words) >= n:
                break
    
    with open('polish_frequent_words.txt', 'w', encoding='utf-8') as f:
        for word in words:
            f.write(f"{word}\n")
        print(f"Downloaded {len(words)} most frequent Polish words to polish_frequent_words.txt")

if __name__ == "__main__":
    download_polish_words(6000)
    


