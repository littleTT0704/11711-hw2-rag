from bs4 import BeautifulSoup
import re

with open(
    "Diploma Ceremonies - Commencement - Carnegie Mellon University.html",
    "r",
) as f:
    soup = BeautifulSoup(f.read())
for elem in soup.find_all(["br"]):
    elem.append("\n")

with open("diploma_ceremonies.txt", "w") as f:
    header = soup.find_all("h1")[1]
    content = header.find_next()
    f.write(header.text)
    f.write(re.sub("\n+", "\n", content.text))
    f.write("\n\n")

    tab = soup.find_all("h2")[0].find_parent("div")
    while True:
        f.write("Diploma Ceremony")
        f.write(re.sub("\n+", "\n", tab.text))
        if "*" in tab.text:
            f.write("*off-campus location\n")
        f.write("\n\n")

        tab = tab.find_next("div")
        if "www.cmu.edu" in tab.text:
            break
