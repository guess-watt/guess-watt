import os
import requests
from datetime import datetime, timedelta

USERNAME = "guess-watt"
OUTPUT = "assets/contributions-30-days.svg"

query = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
  }
}
"""

headers = {
    "Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}"
}

response = requests.post(
    "https://api.github.com/graphql",
    json={
        "query": query,
        "variables": {"login": USERNAME}
    },
    headers=headers
)

response.raise_for_status()

data = response.json()

weeks = data["data"]["user"]["contributionsCollection"][
    "contributionCalendar"
]["weeks"]

days = []

for week in weeks:
    for day in week["contributionDays"]:
        days.append(day)

today = datetime.utcnow().date()
start = today - timedelta(days=29)

days = [
    d for d in days
    if start <= datetime.strptime(d["date"], "%Y-%m-%d").date() <= today
]

max_count = max((d["contributionCount"] for d in days), default=1)

width = 900
height = 260

left = 55
right = 20
top = 50
bottom = 55

chart_width = width - left - right
chart_height = height - top - bottom

bar_width = chart_width / len(days)

bars = []

for i, day in enumerate(days):

    count = day["contributionCount"]

    bar_height = (
        count / max_count * chart_height
        if max_count > 0
        else 0
    )

    x = left + i * bar_width
    y = top + chart_height - bar_height

    bars.append(
        f'''
        <rect
            x="{x:.2f}"
            y="{y:.2f}"
            width="{max(bar_width - 3, 2):.2f}"
            height="{bar_height:.2f}"
            rx="3"
            fill="#e53935">
            <title>{day["date"]}: {count} contributions</title>
        </rect>
        '''
    )

total = sum(d["contributionCount"] for d in days)

svg = f'''<svg
    xmlns="http://www.w3.org/2000/svg"
    width="{width}"
    height="{height}"
    viewBox="0 0 {width} {height}">

    <rect
        width="100%"
        height="100%"
        rx="10"
        fill="#0d1117"/>

    <text
        x="{left}"
        y="28"
        fill="#ffffff"
        font-family="Arial, sans-serif"
        font-size="18"
        font-weight="600">
        Contributions — Last 30 Days
    </text>

    <text
        x="{width - right}"
        y="28"
        text-anchor="end"
        fill="#8b949e"
        font-family="Arial, sans-serif"
        font-size="13">
        {total} contributions
    </text>

    <line
        x1="{left}"
        y1="{top + chart_height}"
        x2="{width - right}"
        y2="{top + chart_height}"
        stroke="#30363d"/>

    {''.join(bars)}

    <text
        x="{left}"
        y="{height - 18}"
        fill="#8b949e"
        font-family="Arial, sans-serif"
        font-size="12">
        {start.strftime("%b %d")}
    </text>

    <text
        x="{width - right}"
        y="{height - 18}"
        text-anchor="end"
        fill="#8b949e"
        font-family="Arial, sans-serif"
        font-size="12">
        {today.strftime("%b %d")}
    </text>

</svg>
'''

os.makedirs("assets", exist_ok=True)

with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write(svg)

print(f"Updated {OUTPUT}")
