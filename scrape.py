import requests
from bs4 import BeautifulSoup


def get_greatthing():
    URL = "https://www.cs.cmu.edu/scs25/25things"
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find(id="region-content")
    # titile of the website
    title = results.find(id="page-title").text
    overview_elements = results.find("div", class_="collapse-text-text")

    # overview of the website
    overview = ""
    for o in overview_elements:
        overview += o.text

    # 25 thing
    thing = ""
    things_elements = results.find_all("fieldset", class_="collapse-text-fieldset")
    for thing_element in things_elements:
        thing_title = thing_element.find("span", class_="fieldset-legend").text
        if thing_title[-1] == '\n':
            thing += thing_title 
        else:
            thing += thing_title + '\n'
        #print(thing_title)
        thing_content_elements = thing_element.find_all("p")
        for thing_content_element in thing_content_elements:
            if thing_content_element is not None:
                thing_content = thing_content_element.text
                thing += thing_content + '\n'
                #print(thing_content)
        #print(thing_element.find("p"))
    #print(results)
    
    content = title + '\n' + overview + '\n' + thing

    with open(f'{title}.txt', 'w') as file:
        file.write(content)
 
def get_history():
    URL = "https://www.cs.cmu.edu/scs25/history"
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find(id="region-content").text
    #print(results.text)
    title = "A history of SCS"
    with open(f'{title}.txt', 'w') as file:
        file.write(results)

def get_history2():
    URL = "https://www.cmu.edu/about/history.html"
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find(id="content").text
    title = "A history of CMU"
    #print(results.text)
    with open(f'{title}.txt', 'w') as file:
        file.write(results)

def get_program():
    URL = "https://lti.cs.cmu.edu/learn"
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find(id="main").text
    # print(results)
    title = "program"
    with open(f'{title}.txt', 'w') as file:
        file.write(results)


def get_scotty():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    URL = 'https://athletics.cmu.edu/athletics/mascot/about'

    # Send a GET request to the page
    page = requests.get(URL, headers=headers)
    title = "scotty"
    # Make sure the request was successful
    if page.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(page.content, 'html.parser')
        results = soup.find(id="main-wrapper").text
        #print(results)
    
        # Process and save the data
        with open(f'{title}.txt', 'w') as file:
                file.write(results)

    else:
        print(f"Failed to retrieve the web page. Status code: {page.status_code}")

def get_tartan():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    URL = "https://athletics.cmu.edu/athletics/tartanfacts"
    page = requests.get(URL, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find(id="main-wrapper").text
    # print(results)
    title = "tartan"
    with open(f'{title}.txt', 'w') as file:
        file.write(results)

def get_kiltieBand():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    URL = "https://athletics.cmu.edu/athletics/kiltieband/index"
    page = requests.get(URL, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find(id="main-wrapper").text
    # print(results)
    title = "kiltieBand"
    with open(f'{title}.txt', 'w') as file:
        file.write(results)

def get_buggy():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    URL = "https://www.cmu.edu/news/stories/archives/2019/april/spring-carnival-buggy.html"
    page = requests.get(URL, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find(id="container").text
    # print(results)
    title = "buggy"
    with open(f'{title}.txt', 'w') as file:
        file.write(results)
get_buggy()