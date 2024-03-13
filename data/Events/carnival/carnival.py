from bs4 import BeautifulSoup
import json

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

with open(input_file.replace(".html", ".txt"), "w") as f:
    f.write(
        """A few notes about 2024 Spring Carnival schedule:
Use Tracks to filter events by category, including student, reunion, virtual, family friendly and school/college. You may use the search function to find a specific day, category or event.
Check out the first draft of the Carnival map.
Additional events will be added up through Carnival, so be sure to bookmark this page. Below are just a few of the events that are in the works:
Spring Carnival Committee weekend entertainment schedule
Tartan Tuba
Yarnivores Pop-up Shop
Songkran: Thai New Year Celebration
CMU Feminists Engaged in Multicultural Matters and Education Panel (FEMME)
Street Styles performances


Weekend Highlights
Booth, Rides and Dog Houses
Thursday: 3-11 p.m.
Friday & Saturday: 11 a.m.-11 p.m. 


Weekend Highlights
Carnival Headquarters Tent
Check-In & Registration
Thursday, Friday and Saturday: 8 a.m.-7 p.m.


Weekend Highlights
Activities, Wellness and Kidzone tents
Thursday: 3-7 p.m.
Friday and Saturday: 8 a.m.-7 p.m.


Weekend Highlights
Buggy Races and Donut Tent
Friday's Preliminary Sweepstakes Race: 8 a.m.-Noon
Saturday's Final Sweepstakes Race: 8 a.m.-Noon


Weekend Highlights
Scotch'n'Soda Performance of The Little Mermaid
Thursday: 7-9:30 p.m.
Friday: 6-8:30 p.m. and 10 p.m.-12:30 a.m.
Saturday: 3-5:30 p.m. and 7-9:30 p.m.


"""
    )
    for event in res:
        date = event["date"]
        for e in event["events"]:
            f.write(f"{e['title']}\n")
            if "span_date" in e:
                f.write(f"{e['span_date']}\n")
            else:
                f.write(f"{date}\n")
            f.write(f"{e['time']}\n")
            f.write(f"{e['permission']}\n")
            f.write(f"{e['description']}\n")
            f.write("\n\n")
