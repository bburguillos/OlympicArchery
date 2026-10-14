
import csv
import html
import math
import hmac
import secrets
import time
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Olympic Archery | Sports by the Numbers",
    page_icon="🏹",
    layout="wide",
)

DATA_FILE = Path(__file__).with_name("athletes.csv")
ASSET_DIR = Path(__file__).parent / "assets"
MATCH_ARROWS = 10


# ======================================================
# OLYMPIC ATHLETE DATABASE
# ======================================================

@st.cache_data
def load_athletes():
    with DATA_FILE.open(encoding="utf-8", newline="") as file:
        records = list(csv.DictReader(file))

    for athlete in records:
        athlete["perfect_10s"] = int(athlete["perfect_10s"])
        athlete["arrows"] = int(athlete["arrows"])
        athlete["p"] = (
            athlete["perfect_10s"] / athlete["arrows"]
        )

    return records


ATHLETES = load_athletes()
BY_CODE = {a["code"]: a for a in ATHLETES}


def athlete_label(a):
    return f'{a["flag"]} {a["country"]} — {a["athlete"]}'


def simulate(a, count=1):
    rng = secrets.SystemRandom()
    return [rng.random() < a["p"] for _ in range(count)]


# ======================================================
# VISUAL STYLING
# ======================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700;800;900&family=DM+Sans:wght@400;500;700&display=swap');

.block-container {
    max-width: 1250px;
    padding-top: 1rem;
}

h1, h2, h3 {
    font-family: 'Barlow Condensed', sans-serif;
}

.stButton > button[kind="primary"] {
    min-height: 48px;
    font-weight: 800;
    border-radius: 12px;
}

.broadcast-title {
    padding: 14px 20px;
    background: linear-gradient(110deg,#10243e,#24577c);
    color: white;
    border-radius: 14px;
    margin: 12px 0;
    border: 1px solid #527a98;
}

.broadcast-title .big {
    font-family: 'Barlow Condensed',sans-serif;
    font-size: clamp(27px,3vw,39px);
    font-weight: 900;
}

.broadcast-title .small {
    font-size: 12px;
    color: #c5d9e8;
    letter-spacing: 1px;
}

.drama {
    padding: 12px;
    border-radius: 12px;
    background: linear-gradient(100deg,#571e23,#a84d18,#462450);
    color: white;
    font-weight: 900;
    font-size: clamp(17px,2.5vw,25px);
    text-align: center;
    margin: 9px 0;
}

.country-card {
    background: linear-gradient(125deg,#12263d,#225377);
    color: white;
    padding: 20px;
    border-radius: 16px;
    margin: 14px 0;
    border: 1px solid #4a7391;
}

.country-card .country {
    font-family: 'Barlow Condensed',sans-serif;
    font-size: 31px;
    font-weight: 900;
}

.country-card .athlete {
    font-size: 15px;
    color: #d5e6f1;
}

.country-card .stats {
    border-top: 1px solid #4e718b;
    margin-top: 12px;
    padding-top: 12px;
    font-size: 14px;
}

.score-strip {
    background: #152d46;
    border-radius: 14px;
    padding: 16px;
    color: white;
    font-weight: bold;
    text-align: center;
    font-size: 22px;
    margin: 12px 0;
}

.podium {
    display: flex;
    align-items: flex-end;
    gap: 9px;
    background: linear-gradient(#10253e,#204b70);
    border-radius: 18px;
    padding: 22px 12px 12px;
    color: white;
    text-align: center;
}

.podium-team {
    flex: 1;
    min-width: 0;
}

.podium-flag {
    font-size: 40px;
}

.podium-country {
    font-weight: 900;
    font-size: 20px;
    overflow-wrap: anywhere;
}

.podium-athlete {
    font-size: 12px;
    opacity: .85;
}

.podium-step {
    margin-top: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 37px;
    font-weight: 900;
    color: #182739;
    border-radius: 9px 9px 0 0;
}

.gold-step {
    height: 140px;
    background: linear-gradient(135deg,#ffe39c,#b78828);
}

.silver-step {
    height: 100px;
    background: linear-gradient(135deg,#e8f0f8,#96a6b4);
}

.bronze-step {
    height: 70px;
    background: linear-gradient(135deg,#e8b584,#a36c3a);
}

@media(max-width:650px) {
    .podium-flag {font-size:25px;}
    .podium-country {font-size:14px;}
}
</style>
""", unsafe_allow_html=True)


# ======================================================
# BROADCAST IMAGES
# ======================================================

def show_banner(name):
    path = ASSET_DIR / f"{name}_banner.webp"

    if path.exists():
        st.image(str(path), use_container_width=True)
    else:
        st.info(
            "Broadcast image missing. "
            "Check the assets folder in GitHub."
        )


# ======================================================
# COUNTRY DISPLAY
# ======================================================

def country_card(a):
    flag = html.escape(a["flag"])
    country = html.escape(a["country"])
    athlete = html.escape(a["athlete"])

    st.markdown(f"""
    <div class="country-card">
        <div style="display:flex;align-items:center;gap:15px">
            <div style="font-size:47px">{flag}</div>
            <div>
                <div class="country">{country}</div>
                <div class="athlete">{athlete}</div>
            </div>
        </div>
        <div class="stats">
            🎯 Perfect 10s: <b>{a["perfect_10s"]}</b>
            &nbsp; | &nbsp;
            🏹 Total arrows: <b>{a["arrows"]}</b>
            <br>
            Paris 2024 Men's Recurve Ranking Round
        </div>
    </div>
    """, unsafe_allow_html=True)


# ======================================================
# STUDENT TRAINING TARGET
# ======================================================

def large_target(shots):
    width = 560
    height = 295
    cx, cy = 145, 145
    radius = 114

    rings = [
        (114, "#f2f0ec"),
        (91, "#171a23"),
        (68, "#2ba6da"),
        (45, "#db3434"),
        (23, "#ffd44a"),
    ]

    svg = [
        f'<svg viewBox="0 0 {width} {height}" '
        'style="width:100%;max-width:560px;height:auto">'
        f'<rect width="{width}" height="{height}" '
        'rx="15" fill="#122840"/>'
    ]

    for r, color in rings:
        svg.append(
            f'<circle cx="{cx}" cy="{cy}" r="{r}" '
            f'fill="{color}" stroke="#293747" '
            'stroke-width="2"/>'
        )

    for i, hit in enumerate(shots):
        angle = i * 2.39996323

        if hit:
            distance = 3 + (i * 5) % 13
        else:
            distance = 29 + (i * 11) % 72

        x = cx + distance * math.cos(angle)
        y = cy + distance * math.sin(angle)

        color = "#00e4a4" if hit else "#ff714b"

        svg.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" '
            f'r="5" fill="{color}" '
            'stroke="#122030" stroke-width="1.5"/>'
        )

    svg.extend([
        '<text x="295" y="68" fill="#c3dbe9" '
        'font-size="17" font-family="Arial">'
        'TRAINING TARGET</text>',

        f'<text x="295" y="128" fill="white" '
        'font-size="51" font-weight="900" '
        f'font-family="Arial">{sum(shots)} / {len(shots)}</text>',

        '<text x="295" y="155" fill="#d0e2ee" '
        'font-size="14" font-family="Arial">'
        'PERFECT 10s</text>',

        '<circle cx="305" cy="194" r="6" fill="#00e4a4"/>'
        '<text x="320" y="199" fill="white" '
        'font-size="14">Perfect 10</text>',

        '<circle cx="305" cy="224" r="6" fill="#ff714b"/>'
        '<text x="320" y="229" fill="white" '
        'font-size="14">Not a perfect 10</text>',

        '</svg>'
    ])

    components.html(
        '<html><body style="margin:0;background:transparent">'
        + "".join(svg)
        + '</body></html>',
        height=300,
        scrolling=False,
    )


# ======================================================
# STUDENT MODE
# ======================================================

def student_mode():
    st.subheader("🌍 Olympic Village")

    options = {
        athlete_label(a): a for a in ATHLETES
    }

    selected = st.selectbox(
        "Choose your assigned country",
        list(options),
    )

    a = options[selected]

    if st.session_state.get("student_code") != a["code"]:
        st.session_state.student_code = a["code"]
        st.session_state.student_stage = "Probability Check"
        st.session_state.athlete_unlocked = False
        st.session_state.training_started = False
        st.session_state.training_shots = []
        st.session_state.training_prediction = None

    country_card(a)

    stages = [
        "Probability Check",
        "Training Camp",
        "Results & Reflection",
    ]

    stage = st.radio(
        "Your next step",
        stages,
        horizontal=True,
        key="student_stage",
    )

    if stage == stages[0]:
        st.markdown("### 🔐 Unlock Your Athlete")

        st.write(
            f'{a["athlete"]} scored '
            f'{a["perfect_10s"]} perfect 10s '
            f'out of {a["arrows"]} arrows.'
        )

        st.write(
            "Calculate the percentage of perfect 10s "
            "on your worksheet."
        )

        entered = st.number_input(
            "Enter your calculated probability (%)",
            min_value=0.0,
            max_value=100.0,
            value=None,
            step=0.1,
            format="%.1f",
            key="student_probability",
        )

        correct = a["p"] * 100

        if entered is not None:
            if abs(entered - correct) <= 0.51:
                st.session_state.athlete_unlocked = True
                st.success(
                    "Correct! Your athlete is unlocked!"
                )
            else:
                st.warning(
                    "Try again: perfect 10s divided by "
                    "72, multiplied by 100."
                )

        if st.session_state.athlete_unlocked:
            st.button(
                "🏹 Continue to Training Camp →",
                type="primary",
                use_container_width=True,
                on_click=lambda: st.session_state.update(
                    student_stage=stages[1]
                ),
            )

    elif stage == stages[1]:
        if not st.session_state.athlete_unlocked:
            st.warning(
                "Complete the Probability Check first."
            )
            return

        st.subheader("🏹 Training Camp")

        if not st.session_state.training_started:
            prediction = st.number_input(
                "Predict the number of perfect 10s "
                "in 10 arrows",
                min_value=0,
                max_value=10,
                value=5,
                key="training_predict",
            )

            if st.button(
                "Start Training",
                type="primary",
            ):
                st.session_state.training_prediction = prediction
                st.session_state.training_started = True
                st.session_state.training_shots = []
                st.rerun()

        else:
            shots = st.session_state.training_shots

            st.progress(len(shots) / 10)
            large_target(shots)

            if len(shots) < 10:
                if st.button(
                    "🏹 Release Next Arrow",
                    type="primary",
                    use_container_width=True,
                ):
                    shot = simulate(a)[0]
                    st.session_state.training_shots.append(shot)
                    st.rerun()

            else:
                st.success("Training Complete!")

                st.write(
                    f"Prediction: "
                    f"{st.session_state.training_prediction}/10"
                )

                st.write(
                    f"Actual: {sum(shots)}/10"
                )

                st.button(
                    "Continue to Results & Reflection →",
                    type="primary",
                    use_container_width=True,
                    on_click=lambda: st.session_state.update(
                        student_stage=stages[2]
                    ),
                )

                if st.button("Try Another Training Round"):
                    st.session_state.training_started = False
                    st.session_state.training_shots = []
                    st.rerun()

    else:
        shots = st.session_state.get(
            "training_shots", []
        )

        if not shots:
            st.info("Complete Training Camp first.")
            return

        st.subheader("📋 Results & Reflection")
        large_target(shots)

        st.metric(
            "Experimental Probability",
            f"{sum(shots)/len(shots)*100:.1f}%",
        )

        st.write(
            f"Your prediction was "
            f"{st.session_state.training_prediction}/10."
        )

        st.write(
            "**Reflection:** Why might your simulated "
            "results differ from your athlete's "
            "historical Olympic results?"
        )


# ======================================================
# TOURNAMENT ENGINE
# ======================================================

def new_match(codes, title):
    return {
        "codes": list(codes),
        "title": title,
        "shots": [[], []],
        "resolved": False,
        "winner": None,
        "loser": None,
        "shootout": False,
        "shootout_rounds": 0,
        "last_reveal": None,
        "bye": False,
    }


def start_bracket(codes):
    if len(codes) < 2 or len(codes) > 24:
        raise ValueError("Choose between 2 and 24 countries.")

    if len(set(codes)) != len(codes):
        raise ValueError("Countries must be unique.")

    entries = list(codes)
    secrets.SystemRandom().shuffle(entries)

    state = {
        "phase": "knockout",
        "round_number": 1,
        "entrants": entries[:],
        "matches": [],
        "semifinal_losers": [],
        "medals": {},
        "history": [],
        "ceremony_step": 0,
        "last_action": 0,
    }

    if len(entries) == 2:
        state["phase"] = "medals"
        state["matches"] = [
            new_match(entries, "🥇 GOLD FINAL")
        ]
        return state

    size = 1 << (len(entries) - 1).bit_length()
    byes = size - len(entries)

    matches = []

    for i in range(size // 2):
        if i < byes:
            match = new_match(
                [entries.pop(0), None],
                f"ROUND 1 · MATCH {i+1}",
            )
            match["resolved"] = True
            match["winner"] = match["codes"][0]
            match["bye"] = True
        else:
            match = new_match(
                [entries.pop(0), entries.pop(0)],
                f"ROUND 1 · MATCH {i+1}",
            )

        matches.append(match)

    state["matches"] = matches
    return state


def resolve_match(match, winner_index):
    match["winner"] = match["codes"][winner_index]
    match["loser"] = match["codes"][1 - winner_index]
    match["resolved"] = True
    match["shootout"] = False


def fire_regular(match):
    if match["resolved"]:
        return

    a = BY_CODE[match["codes"][0]]
    b = BY_CODE[match["codes"][1]]

    pair = [
        simulate(a)[0],
        simulate(b)[0],
    ]

    for k in range(2):
        match["shots"][k].append(pair[k])

    match["last_reveal"] = pair

    if len(match["shots"][0]) == MATCH_ARROWS:
        scores = [
            sum(s[:MATCH_ARROWS])
            for s in match["shots"]
        ]

        if scores[0] > scores[1]:
            resolve_match(match, 0)

        elif scores[1] > scores[0]:
            resolve_match(match, 1)

        else:
            match["shootout"] = True


def fire_shootout(match):
    if match["resolved"]:
        return

    a = BY_CODE[match["codes"][0]]
    b = BY_CODE[match["codes"][1]]

    pair = [
        simulate(a)[0],
        simulate(b)[0],
    ]

    for k in range(2):
        match["shots"][k].append(pair[k])

    match["last_reveal"] = pair
    match["shootout_rounds"] += 1

    if pair[0] != pair[1]:
        resolve_match(
            match,
            0 if pair[0] else 1,
        )


def advance_all_arrows(state):
    for match in state["matches"]:
        if match["resolved"]:
            continue

        if match["shootout"]:
            fire_shootout(match)
        else:
            fire_regular(match)


def round_finished(state):
    return (
        bool(state["matches"])
        and all(
            m["resolved"] for m in state["matches"]
        )
    )


def finish_round(state):
    if not round_finished(state):
        return

    for m in state["matches"]:
        state["history"].append({
            "title": m["title"],
            "codes": m["codes"][:],
            "winner": m["winner"],
            "score": [
                sum(shots[:MATCH_ARROWS])
                for shots in m["shots"]
            ],
            "shootout": m["shootout_rounds"],
            "bye": m["bye"],
        })

    if state["phase"] == "medals":
        for match in state["matches"]:
            if "BRONZE" in match["title"]:
                state["medals"]["bronze"] = match["winner"]
            else:
                state["medals"]["gold"] = match["winner"]
                state["medals"]["silver"] = match["loser"]

        state["phase"] = "complete"
        return

    matches = state["matches"]
    winners = [m["winner"] for m in matches]

    if len(matches) == 2:
        state["semifinal_losers"] = [
            m["loser"] for m in matches
            if m["loser"] is not None
        ]

    if len(winners) == 2:
        medal_matches = []

        if len(state["semifinal_losers"]) == 2:
            medal_matches.append(
                new_match(
                    state["semifinal_losers"],
                    "🥉 BRONZE MATCH",
                )
            )

        elif (
            len(state["entrants"]) == 3
            and len(state["semifinal_losers"]) == 1
        ):
            state["medals"]["bronze"] = (
                state["semifinal_losers"][0]
            )

        medal_matches.append(
            new_match(winners, "🥇 GOLD FINAL")
        )

        state["matches"] = medal_matches
        state["phase"] = "medals"

    else:
        state["round_number"] += 1

        state["matches"] = [
            new_match(
                winners[i:i+2],
                f'ROUND {state["round_number"]} '
                f'· MATCH {i//2+1}',
            )
            for i in range(0, len(winners), 2)
        ]


# ======================================================
# COMPACT ARCHERY TARGET
# ======================================================

def target_svg(shots):
    rings = [
        (52, "#f1eee9"),
        (42, "#20242e"),
        (32, "#2aa7db"),
        (22, "#dd3e3c"),
        (12, "#ffd54d"),
    ]

    output = [
        '<svg viewBox="0 0 120 120" '
        'style="display:block;width:100%;'
        'max-width:100px;height:104px;margin:auto">'
    ]

    for r, color in rings:
        output.append(
            f'<circle cx="60" cy="60" r="{r}" '
            f'fill="{color}" stroke="#182636" '
            'stroke-width="1"/>'
        )

    for i, hit in enumerate(shots[-20:]):
        angle = i * 2.39996323

        if hit:
            distance = 3 + (i * 5) % 7
        else:
            distance = 15 + (i * 7) % 35

        x = 60 + distance * math.cos(angle)
        y = 60 + distance * math.sin(angle)

        color = "#00dfa8" if hit else "#ff714b"

        output.append(
            f'<circle cx="{x:.2f}" cy="{y:.2f}" '
            f'r="3.2" fill="{color}" '
            'stroke="#102130" stroke-width="1"/>'
        )

    output.append("</svg>")
    return "".join(output)


# ======================================================
# MATCH DISPLAY
# ======================================================

def one_match_html(match, index):
    if match["bye"]:
        a = BY_CODE[match["winner"]]

        return (
            '<div class="match">'
            f'<div class="match-label">MATCH {index+1} · BYE</div>'
            f'<div class="bye">{html.escape(a["flag"])} '
            f'{html.escape(a["country"])} advances</div>'
            '</div>'
        )

    cards = []

    for k, code in enumerate(match["codes"]):
        a = BY_CODE[code]
        shots = match["shots"][k]

        score = sum(shots[:MATCH_ARROWS])
        count = min(len(shots), MATCH_ARROWS)

        last = (
            "🎯" if shots[-1] else "✕"
        ) if shots else "—"

        winner_class = (
            " winner"
            if match["resolved"] and code == match["winner"]
            else ""
        )

        cards.append(f"""
        <div class="athlete{winner_class}">
            <div class="flag">
                {html.escape(a["flag"])}
            </div>
            <div class="name">
                {html.escape(a["country"])}
            </div>
            <div class="person">
                {html.escape(a["athlete"])}
            </div>

            <div class="score">
                {score}
                <span>/ {count}</span>
            </div>

            <div class="last">LAST: {last}</div>

            {target_svg(shots)}
        </div>
        """)

    score_a = sum(match["shots"][0][:MATCH_ARROWS])
    score_b = sum(match["shots"][1][:MATCH_ARROWS])

    if score_a == score_b:
        leader = "TIED"
    else:
        winning_index = 0 if score_a > score_b else 1
        leader = (
            "LEADS: "
            + html.escape(
                BY_CODE[
                    match["codes"][winning_index]
                ]["country"]
            )
        )

    if match["resolved"]:
        status = (
            "🏁 WINNER: "
            + html.escape(
                BY_CODE[match["winner"]]["country"]
            )
        )
    elif match["shootout"]:
        status = "⚡ SUDDEN-DEATH SHOOT-OFF"
    else:
        status = (
            f'ARROW {len(match["shots"][0]) + 1}'
            f' OF {MATCH_ARROWS}'
        )

    return (
        '<div class="match">'
        f'<div class="match-label">'
        f'{html.escape(match["title"])}</div>'
        '<div class="competitors">'
        + "".join(cards)
        + '</div>'
        f'<div class="status">{status}</div>'
        f'<div class="leader">{leader}</div>'
        '</div>'
    )


# ======================================================
# DRAMATIC LIVE SCORING
# ======================================================

def drama_message(state):
    active = [
        m for m in state["matches"]
        if not m["resolved"]
    ]

    if not active:
        return "🏁 ROUND COMPLETE — READY TO ADVANCE!"

    if any(m["shootout"] for m in active):
        return (
            "⚡ SUDDEN DEATH — "
            "EVERY ARROW COULD DECIDE IT!"
        )

    remaining = min(
        max(
            0,
            MATCH_ARROWS - len(m["shots"][0])
        )
        for m in active
    )

    if remaining == 1:
        return (
            "🔥 FINAL ARROW — "
            "THE MEDAL DREAM IS ON THE LINE!"
        )

    if remaining <= 3:
        return (
            f"🔥 FINAL {remaining} ARROWS — "
            "THE PRESSURE IS ON!"
        )

    return f"🏹 {remaining} ARROWS REMAIN!"


def latest_action_message(state):
    messages = []

    for match in state["matches"]:
        if match["bye"] or not match["last_reveal"]:
            continue

        a = BY_CODE[match["codes"][0]]
        b = BY_CODE[match["codes"][1]]

        pair = match["last_reveal"]

        if pair[0] != pair[1]:
            scorer = a if pair[0] else b
            messages.append(
                f'{scorer["flag"]} '
                f'{scorer["country"]} hits a perfect 10!'
            )

        if match["resolved"]:
            winner = BY_CODE[match["winner"]]
            messages.append(
                f'🏆 {winner["country"]} advances!'
            )

    if messages:
        return " • ".join(messages[:4])

    return (
        "Both archers hold steady — "
        "no new perfect-10 advantage."
    )


# ======================================================
# FOUR-MATCH BROADCAST GRID
# ======================================================

def broadcast_grid(state):
    matches = state["matches"]
    n = len(matches)

    # Hide decorative banner when four or more
    # matches are displayed to save screen space.
    if (
        st.session_state.get("v6_broadcast_art", True)
        and n < 4
    ):
        show_banner(
            "medals"
            if state["phase"] == "medals"
            else "match"
        )

    label = (
        "MEDAL MATCHES"
        if state["phase"] == "medals"
        else f'ROUND {state["round_number"]} '
             '· LIVE COMPETITION'
    )

    unresolved = [
        m for m in matches
        if not m["resolved"]
    ]

    st.markdown(f"""
    <div class="broadcast-title">
        <div class="small">
            OLYMPIC PROBABILITY ARENA · LIVE
        </div>
        <div class="big">{label}</div>
        <div class="small">
            {len(unresolved)} MATCHES STILL LIVE
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        f'<div class="drama">'
        f'{html.escape(drama_message(state))}'
        '</div>',
        unsafe_allow_html=True,
    )

    if state.get("last_action", 0):
        st.caption(latest_action_message(state))

    cols = 2 if n >= 2 else 1
    rows = (n + cols - 1) // cols

    cards = "".join(
        one_match_html(match, i)
        for i, match in enumerate(matches)
    )

    html_doc = f"""
    <!doctype html>
    <html>
    <head>
    <meta name="viewport"
          content="width=device-width,initial-scale=1">
    <style>

    * {{
        box-sizing:border-box;
    }}

    html,body {{
        margin:0;
        padding:0;
        background:transparent;
        color:white;
        font-family:Arial,sans-serif;
    }}

    .grid {{
        display:grid;
        grid-template-columns:
            repeat({cols},minmax(0,1fr));
        gap:10px;
    }}

    .match {{
        background:linear-gradient(
            145deg,#132940,#1d4262
        );
        border:1px solid #42617e;
        border-radius:12px;
        padding:7px;
        min-width:0;
        overflow:hidden;
    }}

    .match-label {{
        color:#f6c988;
        font-weight:800;
        font-size:12px;
        min-height:20px;
    }}

    .competitors {{
        display:grid;
        grid-template-columns:
            repeat(2,minmax(0,1fr));
        gap:6px;
    }}

    .athlete {{
        background:#0c2033;
        border:1px solid #284d69;
        border-radius:9px;
        padding:3px;
        min-width:0;
        text-align:center;
    }}

    .athlete.winner {{
        border:2px solid #f5c56d;
    }}

    .flag {{
        font-size:19px;
        line-height:20px;
    }}

    .name {{
        font-size:13px;
        font-weight:800;
        overflow:hidden;
        text-overflow:ellipsis;
        white-space:nowrap;
    }}

    .person {{
        color:#bdd1de;
        font-size:10px;
        overflow:hidden;
        text-overflow:ellipsis;
        white-space:nowrap;
    }}

    /* SCORES ARE ABOVE THE TARGET */

    .score {{
        font-size:27px;
        font-weight:900;
        line-height:29px;
        background:#254b6c;
        color:white;
        border-radius:6px;
        margin:3px 0 1px;
    }}

    .score span {{
        font-size:12px;
        color:#c9e4f2;
    }}

    .winner .score {{
        color:#fbd37d;
        text-shadow:0 0 12px #d49c31;
    }}

    .last {{
        font-size:10px;
        color:#bbd7e7;
    }}

    .athlete svg {{
        width:100%;
        max-width:100px;
        height:104px;
        object-fit:contain;
    }}

    .status {{
        text-align:center;
        color:#f5ca8a;
        font-size:11px;
        font-weight:800;
        padding:5px 1px 1px;
    }}

    .leader {{
        color:#7fe9c3;
        font-weight:900;
        font-size:11px;
        text-align:center;
        margin-top:3px;
    }}

    .bye {{
        padding:48px 5px 60px;
        text-align:center;
        font-size:15px;
    }}

    @media(max-width:600px) {{
        .grid {{
            grid-template-columns:1fr;
        }}
    }}

    </style>
    </head>
    <body>
        <div class="grid">
            {cards}
        </div>
    </body>
    </html>
    """

    # Room for both scoreboard rows.
    # Prevent bottom-row clipping.
    board_height = rows * 290 + 18

    components.html(
        html_doc,
        height=board_height,
        scrolling=False,
    )


# ======================================================
# TOURNAMENT BRACKET
# ======================================================

def dynamic_bracket(state):
    st.markdown("### 🏆 Tournament Bracket")

    if st.session_state.get("v6_broadcast_art", True):
        show_banner("bracket")

    columns = st.columns(
        2 if len(state["matches"]) > 1 else 1
    )

    for i, match in enumerate(state["matches"]):
        labels = []

        for code in match["codes"]:
            if code is None:
                labels.append("BYE")
            else:
                athlete = BY_CODE[code]
                labels.append(
                    f'{athlete["flag"]} '
                    f'{athlete["country"]}'
                )

        status = (
            f'✅ {BY_CODE[match["winner"]]["country"]} advances'
            if match["resolved"]
            else "⏳ In progress"
        )

        with columns[i % len(columns)]:
            st.markdown(
                f'**{match["title"]}**  \n'
                f'{labels[0]} vs {labels[1]}  \n'
                f'{status}'
            )


# ======================================================
# MEDAL CEREMONY
# ======================================================

def medal_podium(medals):
    placements = []

    if "silver" in medals:
        placements.append(
            ("silver", 2, "🥈", "silver-step")
        )

    if "gold" in medals:
        placements.append(
            ("gold", 1, "🥇", "gold-step")
        )

    if "bronze" in medals:
        placements.append(
            ("bronze", 3, "🥉", "bronze-step")
        )

    pieces = []

    for key, place, emoji, css in placements:
        athlete = BY_CODE[medals[key]]

        pieces.append(f"""
        <div class="podium-team">
            <div style="font-size:27px">{emoji}</div>
            <div class="podium-flag">
                {html.escape(athlete["flag"])}
            </div>
            <div class="podium-country">
                {html.escape(athlete["country"])}
            </div>
            <div class="podium-athlete">
                {html.escape(athlete["athlete"])}
            </div>
            <div class="podium-step {css}">
                {place}
            </div>
        </div>
        """)

    st.markdown(
        '<div class="podium">'
        + "".join(pieces)
        + '</div>',
        unsafe_allow_html=True,
    )


def medal_ceremony(state):
    medals = state["medals"]
    step = state["ceremony_step"]

    if st.session_state.get("v6_broadcast_art", True):
        show_banner("medals")

    st.title("🏟️ Olympic Medal Ceremony")

    def display_medal(key, symbol):
        athlete = BY_CODE[medals[key]]
        st.markdown(
            f'### {symbol} {athlete["flag"]} '
            f'{athlete["country"]} — {athlete["athlete"]}'
        )

    if step == 0:
        st.info(
            "The medalists have been decided. "
            "Are you ready to reveal the podium?"
        )

        button_text = (
            "🥉 Reveal Bronze"
            if "bronze" in medals
            else "🥈 Reveal Silver"
        )

        if st.button(
            button_text,
            type="primary",
            use_container_width=True,
        ):
            state["ceremony_step"] = 1
            st.rerun()
        return

    if "bronze" in medals:
        display_medal("bronze", "🥉")

        if step == 1:
            if st.button(
                "🥈 Reveal Silver",
                type="primary",
                use_container_width=True,
            ):
                state["ceremony_step"] = 2
                st.rerun()
            return
    else:
        if step == 1:
            state["ceremony_step"] = 2
            st.rerun()

    display_medal("silver", "🥈")

    if step == 2:
        if st.button(
            "🥇 REVEAL GOLD!",
            type="primary",
            use_container_width=True,
        ):
            state["ceremony_step"] = 3
            st.rerun()
        return

    display_medal("gold", "🥇")
    medal_podium(medals)

    if not state.get("confetti_shown", False):
        st.balloons()
        state["confetti_shown"] = True

    st.success("🏆 Congratulations to our Olympic medalists!")

    st.caption(
        "These medals are from the classroom simulation, "
        "not the actual Paris 2024 competition."
    )


# ======================================================
# TEACHER CHAMPIONSHIP
# ======================================================

def teacher_mode():
    st.subheader(
        "🏟️ Teacher Championship — Live Broadcast"
    )

    try:
        teacher_pin = st.secrets.get("TEACHER_PIN", "")
    except Exception:
        teacher_pin = ""

    if not teacher_pin:
        st.error(
            "Set TEACHER_PIN in Streamlit Cloud Secrets."
        )
        return

    if not st.session_state.get(
        "teacher_authenticated", False
    ):
        supplied = st.text_input(
            "Teacher PIN",
            type="password",
        )

        if st.button("Unlock Teacher Dashboard"):
            if hmac.compare_digest(
                str(supplied), str(teacher_pin)
            ):
                st.session_state.teacher_authenticated = True
                st.rerun()
            else:
                st.error("Incorrect PIN")

        return

    state = st.session_state.get("live_bracket")

    # COUNTRY SELECTION

    if state is None:
        choices = {
            athlete_label(a): a["code"]
            for a in ATHLETES
        }

        selected = st.multiselect(
            "Choose Competing Countries (2–24)",
            options=list(choices),
            default=list(choices)[:8],
            key="bracket_competitors",
        )

        st.caption(
            "All matches run simultaneously. "
            "Countries with byes advance automatically."
        )

        if st.button(
            "🏁 Create Olympic Tournament",
            type="primary",
            disabled=len(selected) < 2,
            use_container_width=True,
        ):
            st.session_state.live_bracket = start_bracket(
                [choices[x] for x in selected]
            )

            st.session_state.v7_playing = False
            st.session_state.v7_last_fire = time.monotonic()
            st.rerun()

        return

    top_left, top_right = st.columns([4, 1])

    with top_left:
        st.write(
            f'**{len(state["entrants"])} countries** '
            f'· **{len(state["matches"])} live matches** '
            '· Teacher-controlled'
        )

    with top_right:
        if st.button("End Tournament"):
            st.session_state.live_bracket = None
            st.session_state.v7_playing = False
            st.rerun()

    # AUTOPLAY CONTROLS

    if state["phase"] != "complete":
        st.session_state.setdefault("v7_speed", 4)

        st.select_slider(
            "🎬 Automatic Arrow Speed",
            options=[2, 4, 6],
            value=st.session_state["v7_speed"],
            format_func=lambda x: f"{x} seconds",
            key="speed_selector",
            on_change=lambda: st.session_state.update(
                v7_speed=st.session_state.speed_selector
            ),
        )

        playing = st.session_state.get(
            "v7_playing", False
        )

        controls = st.columns([1, 1, 2])

        with controls[0]:
            if st.button(
                "⏸ Pause" if playing else "▶ Autoplay",
                type="primary",
                use_container_width=True,
            ):
                new_value = (
                    not playing and not round_finished(state)
                )

                st.session_state.v7_playing = new_value
                st.session_state.v7_last_fire = (
                    time.monotonic()
                )
                st.rerun()

        with controls[1]:
            if st.button(
                "🏹 One Arrow",
                use_container_width=True,
                disabled=playing or round_finished(state),
            ):
                advance_all_arrows(state)
                state["last_action"] += 1
                st.session_state.v7_last_fire = (
                    time.monotonic()
                )
                st.rerun()

        with controls[2]:
            st.caption(
                "Autoplay releases arrows across all "
                "active matches. The final arrow gets "
                "an extra dramatic pause."
            )

    # LIVE BROADCAST

    @st.fragment(
        run_every=(
            f'{st.session_state.get("v7_speed",4)}s'
            if st.session_state.get("v7_playing", False)
            and state["phase"] != "complete"
            else None
        )
    )
    def championship_live_view():
        live_state = st.session_state.get(
            "live_bracket"
        )

        if live_state is None:
            return

        playing = st.session_state.get(
            "v7_playing", False
        )

        if (
            live_state["phase"] != "complete"
            and playing
            and not round_finished(live_state)
        ):
            now = time.monotonic()
            speed = st.session_state.get("v7_speed", 4)

            remaining = [
                MATCH_ARROWS - len(m["shots"][0])
                for m in live_state["matches"]
                if not m["resolved"]
                and not m["shootout"]
                and not m["bye"]
            ]

            interval = (
                speed * 1.5
                if remaining and min(remaining) == 1
                else speed
            )

            elapsed = (
                now - st.session_state.get(
                    "v7_last_fire", now
                )
            )

            if elapsed >= interval - 0.12:
                advance_all_arrows(live_state)
                live_state["last_action"] += 1
                st.session_state.v7_last_fire = now

        if live_state["phase"] == "complete":
            medal_ceremony(live_state)
            return

        broadcast_grid(live_state)

        if round_finished(live_state):
            st.session_state.v7_playing = False

            st.success(
                "🏁 All matches in this round are decided!"
            )

            if st.button(
                "➡️ Advance All Winners",
                type="primary",
                use_container_width=True,
                key="advance_winners",
            ):
                finish_round(live_state)

                st.session_state.v7_last_fire = (
                    time.monotonic()
                )
                st.rerun()

        elif st.session_state.get(
            "v7_playing", False
        ):
            st.info(
                "🔴 LIVE — Automatic arrows are releasing. "
                "Press Pause above to take control."
            )

    championship_live_view()

    with st.expander(
        "🏅 View Tournament Bracket",
        expanded=False,
    ):
        dynamic_bracket(state)

    with st.expander(
        "📋 Completed Rounds and Results"
    ):
        for event in state["history"]:
            winner = BY_CODE[event["winner"]]

            if event["bye"]:
                st.write(
                    f'{event["title"]}: '
                    f'{winner["flag"]} '
                    f'{winner["country"]} received a bye.'
                )

            else:
                code_a, code_b = event["codes"]
                country_a = BY_CODE[code_a]["country"]
                country_b = BY_CODE[code_b]["country"]

                st.write(
                    f'{event["title"]}: '
                    f'{country_a} {event["score"][0]} – '
                    f'{event["score"][1]} {country_b}. '
                    f'Winner: {winner["flag"]} '
                    f'{winner["country"]}'
                    + (
                        " (shoot-off)"
                        if event["shootout"]
                        else ""
                    )
                )

    st.caption(
        "Each arrow is simulated using the athlete's "
        "historical probability of scoring a perfect 10. "
        "Arrow positions are illustrative."
    )


# ======================================================
# MAIN APP
# ======================================================

if "v6_broadcast_art" not in st.session_state:
    st.session_state.v6_broadcast_art = True

show_banner("opening")

st.caption(
    "Sports by the Numbers · Paris 2024 "
    "Olympic Archery Probability Championship"
)

st.toggle(
    "🎬 Cinematic Broadcast Graphics "
    "(turn off for compact view)",
    key="v6_broadcast_art",
)

mode = st.radio(
    "App Mode",
    [
        "🎓 Student Training",
        "🏆 Teacher Championship",
    ],
    horizontal=True,
)

if mode.startswith("🎓"):
    student_mode()
else:
    teacher_mode()

st.divider()

st.caption(
    "Dataset: Paris 2024 Men's Individual Recurve "
    "Ranking Round. Each athlete shot 72 arrows. "
    "This app models perfect 10 versus not a 10, "
    "rather than complete Olympic ring scoring. "
    "Tournament results are classroom simulations."
)
