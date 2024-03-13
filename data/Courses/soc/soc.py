import pandas as pd
import json
import re


def read_soc(soc_file: str, output_file: str):
    with open(soc_file, "r") as f:
        html = f.read()
    semester = re.findall(r"<b>Semester: (.*?)</b>", html)[0]

    df = (
        pd.read_html(soc_file)[0]
        .iloc[2:, :-1]
        .set_axis(
            [
                "course",
                "title",
                "units",
                "lec_sec",
                "days",
                "begin",
                "end",
                "room",
                "location",
                "instructor",
            ],
            axis=1,
        )
    )

    i = 0
    res = []
    dep = None
    while i < len(df) - 1:
        row = df.iloc[i]
        if (
            not pd.isna(row["course"])
            and pd.isna(row["title"])
            and pd.isna(row["units"])
            and pd.isna(row["lec_sec"])
        ):
            if dep:
                dep["courses"] = courses
                res.append(dep)
            dep = dict()
            dep["department"] = row["course"]
            courses = []
            i += 1
        else:
            course = dict()
            course["number"] = row["course"]
            course["name"] = row["title"]
            course["units"] = row["units"]
            sections = []

            for j in range(i, len(df)):
                row = df.iloc[j]
                if j > i and not pd.isna(row["course"]):
                    break
                if not (
                    pd.isna(row["lec_sec"])
                    and pd.isna(row["days"])
                    and pd.isna(row["begin"])
                    and pd.isna(row["end"])
                    and pd.isna(row["room"])
                    and pd.isna(row["location"])
                    and pd.isna(row["instructor"])
                ):
                    section = dict()
                    section["lec_sec"] = row["lec_sec"]
                    section["days"] = row["days"]
                    section["begin"] = row["begin"]
                    section["end"] = row["end"]
                    section["room"] = row["room"]
                    section["location"] = row["location"]
                    section["instructor"] = row["instructor"]
                    sections.append(section)

            course["sections"] = sections
            courses.append(course)

            i = j

    final = {"semester": semester, "schedule": res}

    with open(f"{output_file}.json", "w") as f:
        json.dump(final, f, indent=4)

    with open(f"{output_file}.txt", "w") as f:
        for d in res:
            department = d["department"]
            for c in d["courses"]:
                t = [f"Department: {department} ({c['number'][:2]})"]
                t.append(f"Course: {c['number']}")
                t.append(f"Title: {c['name']}")
                t.append(f"Units: {c['units']}")
                t.append("Sections")
                for s in c["sections"]:
                    if s["lec_sec"] == "Lec":
                        t.append(f"Lecture/Section: Lecture")
                    else:
                        t.append(f"Lecture/Section: Section {s['lec_sec']}")
                    t.append(f"Days: {s['days']}")
                    t.append(f"Begin: {s['begin']}")
                    t.append(f"End: {s['end']}")
                    t.append(f"Room: {s['room']}")
                    t.append(f"Location: {s['location']}")
                    t.append(f"Instructor: {s['instructor']}")
                f.write("\n".join(t) + "\n\n")


if __name__ == "__main__":
    for soc in [
        "sched_layout_fall.html",
        "sched_layout_spring.html",
        "sched_layout_summer_1.html",
        "sched_layout_summer_2.html",
    ]:
        print(soc)
        read_soc(soc, soc.replace(".html", ""))
