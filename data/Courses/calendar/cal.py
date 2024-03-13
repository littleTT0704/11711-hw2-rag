import pandas as pd
import re
from collections import defaultdict


def read_calendar(calendar_file: str, output_file: str):
    df = pd.read_excel(
        calendar_file, header=None, names=["date", "t", "date_to", "day", "event"]
    )

    def day_count(s: str, name: str) -> str:
        section, s = s.split(": (")
        if "Semester" in section:
            section = name

        s, t = s.split(") ")
        if "[" in t:
            tail = f"{section} is formally called {t.split('formerly ')[1][:-1]}. "
            t = t.split(" ")[0]
        else:
            tail = ""
        total = int(t.split("=")[1])

        m, t, w, th, f = (int(x.split("-")[1]) for x in s.split(", "))
        # F = 65 for F23 Mini-2
        if f > 50:
            f //= 10
        return f"There are {total} work days in {section} ({m} Mondays, {t} Tuesdays, {w} Wednesdays, {th} Thursdays, {f} Fridays). {tail}"

    l = []
    calendar_name = calendar_file.replace("-list-view.xlsx", "").replace("-", " ")
    i = 0
    while i < len(df):
        row = df.iloc[i]
        # empty row
        if pd.isna(row).all():
            i += 1

        # semester header
        elif not pd.isna(row["date"]) and pd.isna(row["day"]):
            # semester name
            semester_name = row["date"]
            name = row["date"].split(" (")[1].split(")")[0]

            # day counts
            j = i
            while not pd.isna(df.iloc[j]["event"]):
                s = f"{semester_name}\n{day_count(df.iloc[j]['event'], name)}\n"
                l.append(re.sub("(\*+)", r" (\1)", s))
                j += 1

            # skip to content
            i = j + 2
            header = False

        # notes in the end
        elif row["day"] == "Notes:":
            break

        # normal item
        else:
            event = row["event"].replace("  ", " ")
            date = row["date"].strftime("%Y-%m-%d (%A)")
            if pd.isna(row["date_to"]):
                s = f"{semester_name}\n{date}: {event}\n"
                l.append(re.sub("(\*+)", r" (\1)", s))
            else:
                date_to = row["date_to"].strftime("%Y-%m-%d (%A)")
                s = f"{semester_name}\n{date} to {date_to}: {event}\n"
                l.append(re.sub("(\*+)", r" (\1)", s))
            i += 1

        footnotes = {}
        for j in range(i + 1, len(df)):
            row = df.iloc[j]
            if not (pd.isna(row["event"]) or pd.isna(row["day"])):
                marker = row["day"]
                event = row["event"].replace("\n", "")
                footnotes[f" ({marker})"] = event

    d = defaultdict(list)
    for s in l:
        for marker, event in footnotes.items():
            if marker in s:
                s = s.replace(marker, "") + event + "\n"
        lines = s.split("\n")
        d[lines[0]].append("\n".join(lines[1:]))

    for semester, events in d.items():
        semester_file = (
            output_file.replace("list-view", semester.split(" (")[0])
            .replace(" ", "-")
            .replace("-", "_")
        )
        with open(semester_file, "w") as f:
            for event in events:
                if (
                    "Summer Semester includes semester-length courses, as well as mini-5 and mini-6. Courses previously offered as Summer Session One (6-weeks) correspond & follow the Mini-5 dates and deadlines.  Summer Semester Two courses (6-weeks) correspond & follow their separate dates."
                    in event
                ):
                    event = event.replace(
                        "Summer Semester includes semester-length courses, as well as mini-5 and mini-6. Courses previously offered as Summer Session One (6-weeks) correspond & follow the Mini-5 dates and deadlines.  Summer Semester Two courses (6-weeks) correspond & follow their separate dates. \n",
                        "",
                    )
                f.write(event + "\n")


if __name__ == "__main__":
    for c in [
        "2324-academic-calendar-list-view.xlsx",
        "2324-doctoral-academic-calendar-list-view.xlsx",
        # 2425 calendar's date and date_to columns are updated correctly
        "2425-academic-calendar-list-view.xlsx",
    ]:
        print(c)
        read_calendar(c, c.replace(".xlsx", ".txt"))
