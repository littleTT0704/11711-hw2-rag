from bs4 import BeautifulSoup
import json

# TODO: carnival description and weekend highlights?

input_file = "Schedule - Spring Carnival 2024.html"
with open(input_file, "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read())

table = soup.find_all(
    "div", {"class": "AgendaStyles__gridContainer___LLtWD grid__container___DIrBq"}
)[0]
res = []

for day in table.find_all("div", recursive=False):
    if "data-cvent-id" in day.attrs:
        d = {}
        d["date"] = day.attrs["data-cvent-id"].split("-")[-1]
        l = []
        for item in day.find_all("div", {"class": "AgendaStyles__panel___wmdLJ"}):
            header, permission, description = item.find_all(
                "div",
                {"class": "grid__row___UL8Yq"},
            )
            title, time = header.find_all(
                "div",
                {
                    "class": "grid__col___ogH35 grid__col-xs-offset-0___d70m9 grid__col-sm-6___gZTlF grid__col-sm-offset-0___e2LT6 grid__col-md-offset-0___ufJ5l grid__col-lg-offset-0___GOmcU"
                },
            )
            span_date = (
                time.find_next("div").find_next("div").find_next("div").find_next("div")
            )
            time = span_date.find_next("div")

            event = {}
            event["title"] = title.text
            if span_date.text != "":
                event["span_date"] = span_date.text.replace("\u2013", "-")
            event["time"] = time.text
            event["permission"] = permission.text
            event["description"] = description.text

            l.append(event)

        d["events"] = l
        res.append(d)

with open(input_file.replace(".html", ".json"), "w") as f:
    json.dump(res, f, indent=4)
