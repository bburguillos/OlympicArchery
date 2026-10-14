
import csv
import html
import math
import hmac
import random
import secrets
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Olympic Archery | Sports by the Numbers",
    page_icon="🏹",
    layout="wide",
)

DATA_FILE = Path(__file__).with_name("athletes.csv")
MATCH_ARROWS = 10


# ==================================================
# ATHLETE DATABASE
# ==================================================

@st.cache_data
def load_athletes():
    with DATA_FILE.open(
        encoding="utf-8", newline=""
    ) as handle:
        records = list(csv.DictReader(handle))

    for a in records:
        a["perfect_10s"] = int(a["perfect_10s"])
        a["arrows"] = int(a["arrows"])
        a["p"] = a["perfect_10s"] / a["arrows"]

    return records


ATHLETES = load_athletes()
BY_CODE = {a["code"]: a for a in ATHLETES}


# ==================================================
# VISUAL DESIGN
# ==================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700;800;900&family=DM+Sans:wght@400;500;700&display=swap');

.block-container {
    padding-top: 1.1rem;
    max-width: 1200px;
}

.hero {
    border-radius: 24px;
    padding: 25px 30px;
    background: linear-gradient(
        115deg, #0d1b30, #183953 70%, #8c4b21
    );
    color: white !important;
    margin-bottom: 18px;
    border: 1px solid rgba(255,255,255,.16);
}

.hero .eyebrow {
    font: 700 12px 'DM Sans',sans-serif;
    letter-spacing: 3px;
    color: #fbd09b;
}

.hero .huge {
    font: 900 clamp(35px,5vw,64px)
        'Barlow Condensed',sans-serif;
    line-height: 1.05;
    margin: 5px 0 9px;
}

.hero .subtitle {
    font: 500 14px 'DM Sans',sans-serif;
    color: #d9e4f0;
}

.country-card {
    background: linear-gradient(135deg,#152c45,#244866);
    border: 1px solid #4b7393;
    border-radius: 17px;
    padding: 18px 22px;
    color: white;
    margin: 12px 0;
}

.country-head {
    display: flex;
    align-items: center;
    gap: 16px;
}

.country-card .flag {
    font-size: 48px;
}

.country-card .country {
    font: 900 32px 'Barlow Condensed',sans-serif;
}

.country-card .athlete {
    font: 500 15px 'DM Sans',sans-serif;
    color: #d5e7f6;
}

.country-card .stats {
    display: flex;
    gap: 14px;
    flex-wrap: wrap;
    margin-top: 14px;
    border-top: 1px solid #547089;
    padding-top: 13px;
    font-size: 13px;
    color: #eaf3fb;
}

.score-strip {
    background: #152d46;
    color: white;
    border-radius: 16px;
    padding: 17px 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: 12px 0;
}

.score-strip strong {
    font: 900 31px 'Barlow Condensed',sans-serif;
    color: #ffd189;
}

.podium-stage {
    display: flex;
    justify-content: center;
    align-items: flex-end;
    gap: 10px;
    padding: 24px 8px 12px;
    background: linear-gradient(#0e233a,#204663);
    border-radius: 22px;
    margin: 14px 0 20px;
    min-height: 340px;
}

.podium-entry {
    flex: 1;
    min-width: 0;
    text-align: center;
    color: white;
}

.podium-entry .flag {
    font-size: clamp(28px,4vw,54px);
}

.podium-entry .medal {
    font-size: 25px;
}

.podium-entry .team {
    font: 800 clamp(16px,2.4vw,28px)
        'Barlow Condensed',sans-serif;
    overflow-wrap: anywhere;
}

.podium-entry .archer {
    font-size: 12px;
    opacity: .85;
    margin-bottom: 8px;
}

.podium-entry .score {
    font: 800 23px 'Barlow Condensed',sans-serif;
}

.podium-block {
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 10px 10px 0 0;
    color: #12263b;
    font: 900 44px 'Barlow Condensed',sans-serif;
}

.podium-1 {
    height: 132px;
    background: linear-gradient(135deg,#ffe399,#b88723);
}

.podium-2 {
    height: 92px;
    background: linear-gradient(135deg,#ecf3fb,#889cac);
}

.podium-3 {
    height: 65px;
    background: linear-gradient(135deg,#f0bf8a,#9c632f);
}

@media(max-width:620px) {
    .hero {padding:20px;}
    .country-card .country {font-size:25px;}
    .podium-stage {gap:4px;}
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <div class="eyebrow">
        DOVER TIGERS · SPORTS BY THE NUMBERS
    </div>
    <div class="huge">🏹 ROAD TO GOLD</div>
    <div class="subtitle">
        OLYMPIC ARCHERY CHAMPIONSHIP · PARIS 2024
    </div>
</div>
""", unsafe_allow_html=True)

st.caption(
    "Real Paris 2024 statistics determine each athlete's "
    "probability. All app competitions are simulations."
)


# ==================================================
# COUNTRY CARDS
# ==================================================

def country_card(a):
    flag = html.escape(a["flag"])
    country = html.escape(a["country"])
    athlete = html.escape(a["athlete"])

    st.markdown(f"""
<div class="country-card">
    <div class="country-head">
        <div class="flag">{flag}</div>
        <div>
            <div class="country">{country}</div>
            <div class="athlete">
                {athlete} · Paris 2024
            </div>
        </div>
    </div>
    <div class="stats">
        <span>
            🎯 PERFECT 10s:
            <b>{a["perfect_10s"]}</b>
        </span>
        <span>
            🏹 ARROWS SHOT:
            <b>{a["arrows"]}</b>
        </span>
        <span>
            MEN'S RECURVE RANKING ROUND
        </span>
    </div>
</div>
""", unsafe_allow_html=True)


# ==================================================
# RESPONSIVE TARGET GRAPHICS
# ==================================================

def archery_visual(shots, heading="LIVE TARGET"):
    W, H = 560, 300
    cx, cy, rr = 143, 149, 116

    colors = [
        "#f8f8f2",
        "#171b23",
        "#29a6da",
        "#d93431",
        "#ffd549",
    ]

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {W} {H}" '
        'style="display:block;width:100%;height:auto;'
        'max-width:560px;margin:auto">',
        '<style>'
        '@keyframes land {'
        'from{opacity:0;transform:scale(1.6)}'
        'to{opacity:1;transform:scale(1)}}'
        '.latest{animation:land .55s ease-out;'
        'transform-box:fill-box;transform-origin:center}'
        '</style>',
        f'<rect width="{W}" height="{H}" '
        'rx="17" fill="#11253e"/>',
        f'<circle cx="{cx}" cy="{cy}" r="{rr+6}" '
        'fill="#0a1625" stroke="#6595b2" '
        'stroke-width="2"/>',
    ]

    for i, color in enumerate(colors):
        radius = rr * (1 - i * .19)

        svg.append(
            f'<circle cx="{cx}" cy="{cy}" '
            f'r="{radius:.1f}" fill="{color}" '
            'stroke="#203046" stroke-width="2"/>'
        )

    ten_radius = rr * .20

    svg.append(
        f'<circle cx="{cx}" cy="{cy}" '
        f'r="{ten_radius:.1f}" fill="#ffd549" '
        'stroke="#141719" stroke-width="2"/>'
    )

    for i, success in enumerate(shots):
        theta = i * 2.39996322973 + .4

        if success:
            rad = ten_radius * (
                .22 + .49 * ((i * 7) % 11) / 11
            )
        else:
            rad = (
                ten_radius + 7
                + (rr - ten_radius - 20)
                * ((i * 13 + 7) % 29) / 29
            )

        x = cx + rad * math.cos(theta)
        y = cy + rad * math.sin(theta)

        latest = (
            ' class="latest"'
            if i == len(shots) - 1 else ""
        )

        marker = (
            "#00e4ad" if success else "#ff714b"
        )

        svg.append(
            f'<circle{latest} cx="{x:.1f}" '
            f'cy="{y:.1f}" r="5" '
            f'fill="{marker}" stroke="#101d30" '
            'stroke-width="1.5"/>'
        )

    hits = sum(shots)
    count = len(shots)
    heading = html.escape(heading)

    svg.extend([
        f'<text x="297" y="71" fill="#acc6da" '
        'font-family="Arial" font-size="14" '
        f'font-weight="bold">{heading}</text>',

        f'<text x="297" y="125" fill="#ffffff" '
        'font-family="Arial" font-size="48" '
        f'font-weight="900">{hits} / {count}</text>',

        '<text x="297" y="151" fill="#d6e7f2" '
        'font-family="Arial" font-size="13">'
        'PERFECT 10s</text>',

        '<circle cx="303" cy="190" r="5" '
        'fill="#00e4ad"/>'
        '<text x="316" y="195" fill="#c2d5e4" '
        'font-family="Arial" font-size="13">'
        'Perfect 10</text>',

        '<circle cx="303" cy="220" r="5" '
        'fill="#ff714b"/>'
        '<text x="316" y="225" fill="#c2d5e4" '
        'font-family="Arial" font-size="13">'
        'Not a 10</text>',

        '<text x="297" y="262" fill="#9cb8ce" '
        'font-family="Arial" font-size="11">'
        'Arrow locations are illustrative</text>',
        '</svg>',
    ])

    components.html(
        '<html><body style="margin:0;'
        'background:transparent;overflow:hidden">'
        + "".join(svg)
        + '</body></html>',
        height=306,
        scrolling=False,
    )


# ==================================================
# PROBABILITY
# ==================================================

def simulate(a, count, rng):
    return [
        rng.random() < a["p"]
        for _ in range(count)
    ]


def athlete_label(a):
    return (
        f'{a["flag"]} {a["country"]} '
        f'— {a["athlete"]}'
    )


def calc_ok(answer, expected):
    return (
        answer is not None
        and abs(float(answer) - expected) <= .51
    )


def check_panel(a):
    st.write(
        f'**Historical results:** '
        f'{a["perfect_10s"]} perfect 10s '
        f'out of {a["arrows"]} arrows.'
    )

    st.caption(
        "Calculate the probability on your worksheet "
        "before entering your percentage."
    )

    entered = st.number_input(
        "Your calculated P(perfect 10), as a percent",
        min_value=0.0,
        max_value=100.0,
        value=None,
        step=.1,
        format="%.1f",
        key="my_pct",
        placeholder="Example: 47.2",
    )

    if entered is None:
        st.info("Enter your answer to unlock training.")
        return False

    if calc_ok(entered, a["p"] * 100):
        st.success(
            "Correct! Your athlete is unlocked."
        )
        return True

    st.warning(
        "Try again. Divide perfect 10s by 72 "
        "and multiply by 100."
    )
    return False


# ==================================================
# STUDENT TRAINING MODE
# ==================================================

def student_mode():
    st.subheader("🌍 Olympic Village")

    options = {
        athlete_label(a): a
        for a in ATHLETES
    }

    selection = st.selectbox(
        "Choose your assigned country",
        list(options),
    )

    a = options[selection]

    if st.session_state.get("student_code") != a["code"]:
        st.session_state.student_code = a["code"]
        st.session_state.training_shots = []
        st.session_state.training_started = False
        st.session_state.training_prediction = None
        st.session_state.student_stage = (
            "🔐 Probability Check"
        )
        st.session_state.athlete_unlocked = False

    country_card(a)

    stages = [
        "🔐 Probability Check",
        "🏹 Training Camp",
        "📋 Results & Reflection",
    ]

    stage = st.radio(
        "Your next step",
        stages,
        key="student_stage",
        horizontal=True,
    )

    if stage == stages[0]:
        unlocked = check_panel(a)

        st.markdown(
            "**Worksheet:** Also calculate the "
            "probability of NOT scoring a perfect 10."
        )

        if unlocked:
            st.session_state.athlete_unlocked = True

            st.button(
                "🏹 Continue to Training Camp →",
                type="primary",
                use_container_width=True,
                on_click=lambda: st.session_state.update(
                    student_stage=stages[1]
                ),
            )

    elif stage == stages[1]:
        if not st.session_state.get(
            "athlete_unlocked", False
        ):
            st.info(
                "Complete the Probability Check first."
            )
            return

        if not st.session_state.get(
            "training_started", False
        ):
            prediction = st.number_input(
                "Predict perfect 10s in 10 training arrows",
                min_value=0,
                max_value=10,
                value=5,
                step=1,
                key="predict10",
            )

            if st.button(
                "Start 10-arrow training",
                type="primary",
            ):
                st.session_state.training_started = True
                st.session_state.training_prediction = (
                    int(prediction)
                )
                st.session_state.training_shots = []
                st.rerun()

        else:
            shots = st.session_state.training_shots

            st.progress(len(shots) / 10)

            archery_visual(
                shots,
                heading="TRAINING TARGET",
            )

            st.metric(
                "Perfect 10s",
                f"{sum(shots)} / {len(shots)}",
            )

            if len(shots) < 10:
                if st.button(
                    "🏹 Release next arrow",
                    type="primary",
                ):
                    shot = simulate(
                        a, 1, secrets.SystemRandom()
                    )[0]

                    st.session_state.training_shots = (
                        shots + [shot]
                    )
                    st.rerun()

            else:
                st.success(
                    "Training complete! You predicted "
                    f'{st.session_state.training_prediction} '
                    f"and scored {sum(shots)}."
                )

                st.button(
                    "📋 Continue to Results & Reflection →",
                    type="primary",
                    use_container_width=True,
                    on_click=lambda: st.session_state.update(
                        student_stage=stages[2]
                    ),
                )

                if st.button(
                    "Run another training session"
                ):
                    st.session_state.training_started = False
                    st.session_state.training_shots = []
                    st.session_state.training_prediction = None
                    st.rerun()

    else:
        shots = st.session_state.get(
            "training_shots", []
        )

        if not shots:
            st.info("Complete Training Camp first.")
            return

        archery_visual(
            shots,
            heading="FINAL TRAINING TARGET",
        )

        st.write(
            f"**Perfect 10s:** {sum(shots)}/{len(shots)}"
        )

        st.write(
            "**Experimental probability:** "
            f"{sum(shots) / len(shots) * 100:.1f}%"
        )

        st.write(
            "**Your prediction:** "
            f'{st.session_state.training_prediction}/10'
        )

        st.markdown(
            "**Reflection:** Why might your simulated "
            "results differ from the athlete's "
            "historical Olympic percentage?"
        )


# ==================================================
# TOURNAMENT ENGINE
# ==================================================

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
    }


def start_bracket(codes):
    entries = list(codes)
    secrets.SystemRandom().shuffle(entries)

    size = 1 << (len(entries) - 1).bit_length()
    byes = size - len(entries)

    pairs = []
    remaining = entries[:]

    for i in range(size // 2):
        if i < byes:
            pairs.extend([remaining.pop(0), None])
        else:
            pairs.extend([
                remaining.pop(0),
                remaining.pop(0),
            ])

    state = {
        "phase": "knockout",
        "round_number": 1,
        "entrants": list(codes),
        "matches": [],
        "match_index": 0,
        "winners": [],
        "semifinal_losers": [],
        "medal_queue": [],
        "medals": {},
        "history": [],
    }

    if len(codes) == 2:
        state["phase"] = "medals"
        state["medal_queue"] = [
            new_match(
                entries,
                "🥇 GOLD MEDAL FINAL",
            )
        ]
    else:
        state["matches"] = [
            new_match(
                pairs[i:i + 2],
                f"ROUND 1 · MATCH {i // 2 + 1}",
            )
            for i in range(0, size, 2)
        ]

        skip_byes(state)

    return state


def active_match(state):
    if state["phase"] == "knockout":
        return state["matches"][
            state["match_index"]
        ]

    if state["phase"] == "medals":
        return state["medal_queue"][0]

    return None


def skip_byes(state):
    while state["phase"] == "knockout":
        while state["match_index"] < len(
            state["matches"]
        ):
            match = state["matches"][
                state["match_index"]
            ]

            present = [
                code for code in match["codes"]
                if code is not None
            ]

            if len(present) == 2:
                return

            if len(present) == 1:
                match["resolved"] = True
                match["winner"] = present[0]

                state["winners"].append(
                    present[0]
                )

                state["history"].append(
                    f"{BY_CODE[present[0]]['country']} "
                    "advances with a bye"
                )

            state["match_index"] += 1

        finish_round(state)


def finish_round(state):
    winners = state["winners"][:]
    state["winners"] = []

    if len(winners) == 2:
        queue = []

        if len(state["semifinal_losers"]) == 2:
            queue.append(
                new_match(
                    state["semifinal_losers"],
                    "🥉 BRONZE MEDAL MATCH",
                )
            )

        elif (
            len(state["entrants"]) == 3
            and len(state["semifinal_losers"]) == 1
        ):
            state["medals"]["bronze"] = (
                state["semifinal_losers"][0]
            )

        queue.append(
            new_match(
                winners,
                "🥇 GOLD MEDAL FINAL",
            )
        )

        state["medal_queue"] = queue
        state["phase"] = "medals"
        return

    if len(winners) < 2:
        raise ValueError(
            "Knockout bracket lost competitors."
        )

    state["round_number"] += 1

    state["matches"] = [
        new_match(
            winners[i:i + 2],
            f"ROUND {state['round_number']} "
            f"· MATCH {i // 2 + 1}",
        )
        for i in range(0, len(winners), 2)
    ]

    state["match_index"] = 0
    skip_byes(state)


# ==================================================
# ARROW-BY-ARROW MATCHES
# ==================================================

def fire_pair(state):
    match = active_match(state)

    a, b = (
        BY_CODE[c]
        for c in match["codes"]
    )

    rng = secrets.SystemRandom()

    pair = [
        rng.random() < a["p"],
        rng.random() < b["p"],
    ]

    for k in range(2):
        match["shots"][k].append(pair[k])

    match["last_reveal"] = pair

    if len(match["shots"][0]) >= MATCH_ARROWS:
        score_a, score_b = map(
            sum, match["shots"]
        )

        if score_a == score_b:
            match["shootout"] = True
        else:
            resolve_match(
                state,
                0 if score_a > score_b else 1,
            )


def fire_shootout(state):
    match = active_match(state)

    a, b = (
        BY_CODE[c]
        for c in match["codes"]
    )

    rng = secrets.SystemRandom()

    pair = [
        rng.random() < a["p"],
        rng.random() < b["p"],
    ]

    for k in range(2):
        match["shots"][k].append(pair[k])

    match["last_reveal"] = pair
    match["shootout_rounds"] += 1

    if pair[0] != pair[1]:
        resolve_match(
            state,
            0 if pair[0] else 1,
        )


def resolve_match(state, index):
    match = active_match(state)

    winner = match["codes"][index]
    loser = match["codes"][1 - index]

    match["winner"] = winner
    match["loser"] = loser
    match["resolved"] = True

    state["history"].append({
        "round": match["title"],
        "winner": winner,
        "loser": loser,
        "score": [
            sum(match["shots"][0][:MATCH_ARROWS]),
            sum(match["shots"][1][:MATCH_ARROWS]),
        ],
        "shootout_rounds": match["shootout_rounds"],
    })


def next_match(state):
    match = active_match(state)

    if not match or not match["resolved"]:
        return

    if state["phase"] == "medals":
        if "BRONZE" in match["title"]:
            state["medals"]["bronze"] = (
                match["winner"]
            )
        else:
            state["medals"]["gold"] = match["winner"]
            state["medals"]["silver"] = match["loser"]

        state["medal_queue"].pop(0)

        if not state["medal_queue"]:
            state["phase"] = "complete"

        return

    if len(state["matches"]) == 2:
        state["semifinal_losers"].append(
            match["loser"]
        )

    state["winners"].append(
        match["winner"]
    )

    state["match_index"] += 1
    skip_byes(state)


# ==================================================
# MATCH DISPLAY: TWO TARGETS SIDE BY SIDE
# ==================================================

def match_visual(match):
    a, b = (
        BY_CODE[c]
        for c in match["codes"]
    )

    scores = [
        sum(shots)
        for shots in match["shots"]
    ]

    st.markdown(
        f"### {match['title']}"
    )

    st.caption(
        "Each click releases one simulated arrow "
        "from each competitor."
    )

    col_a, col_b = st.columns(
        2, gap="small"
    )

    for k, (col, athlete) in enumerate(
        zip([col_a, col_b], [a, b])
    ):
        with col:
            st.markdown(
                f"#### {athlete['flag']} "
                f"{athlete['country']}"
            )

            st.caption(athlete["athlete"])

            count = len(
                match["shots"][k]
            )

            st.metric(
                "Perfect 10s",
                f"{scores[k]} / {count}",
            )

            archery_visual(
                match["shots"][k],
                heading="MATCH TARGET",
            )

            history = " ".join(
                "🎯" if hit else "✕"
                for hit in match["shots"][k]
            )

            st.markdown(
                history or "Ready to shoot"
            )

    if match["last_reveal"] is not None:
        words = [
            "🎯 PERFECT 10!" if hit
            else "🏹 Not a 10"
            for hit in match["last_reveal"]
        ]

        st.info(
            f"Last arrows: "
            f"{a['flag']} {words[0]}"
            f"   ·   "
            f"{b['flag']} {words[1]}"
        )

    if match["shootout_rounds"]:
        st.warning(
            "Sudden-death shoot-off: "
            f"{match['shootout_rounds']} "
            "extra arrow(s) per country."
        )


# ==================================================
# MEDAL CEREMONY
# ==================================================

def medal_podium(gold, silver, bronze):
    ordered = [
        (silver, 2, "🥈", "Silver"),
        (gold, 1, "🥇", "Gold"),
        (bronze, 3, "🥉", "Bronze"),
    ]

    chunks = []

    for athlete, place, medal, label in ordered:
        chunks.append(f"""
<div class="podium-entry">
    <div class="medal">{medal}</div>
    <div class="flag">
        {html.escape(athlete["flag"])}
    </div>
    <div class="team">
        {html.escape(athlete["country"])}
    </div>
    <div class="archer">
        {html.escape(athlete["athlete"])}
    </div>
    <div class="score">{label}</div>
    <div class="podium-block podium-{place}">
        {place}
    </div>
</div>
""")

    st.markdown(
        '<div class="podium-stage">'
        + "".join(chunks)
        + "</div>",
        unsafe_allow_html=True,
    )


# ==================================================
# TEACHER CHAMPIONSHIP
# ==================================================

def teacher_mode():
    st.subheader(
        "🏟️ Teacher Championship"
    )

    try:
        teacher_pin = st.secrets.get(
            "TEACHER_PIN", ""
        )
    except Exception:
        teacher_pin = ""

    if not teacher_pin:
        st.error(
            "Set TEACHER_PIN in Streamlit Cloud Secrets."
        )
        st.code(
            'TEACHER_PIN = "your-private-pin"',
            language="toml",
        )
        return

    if not st.session_state.get(
        "teacher_authenticated", False
    ):
        supplied = st.text_input(
            "Teacher PIN",
            type="password",
        )

        if st.button(
            "Unlock teacher dashboard"
        ):
            if hmac.compare_digest(
                str(supplied),
                str(teacher_pin),
            ):
                st.session_state.teacher_authenticated = True
                st.rerun()
            else:
                st.error("Incorrect PIN")

        return

    st.caption(
        "The teacher controls this tournament "
        "from one screen. Students can train "
        "individually on their devices."
    )

    state = st.session_state.get(
        "live_bracket"
    )

    # ---------- COUNTRY SELECTION ----------

    if state is None:
        choices = {
            athlete_label(a): a["code"]
            for a in ATHLETES
        }

        selected = st.multiselect(
            "Choose competing countries (2–24)",
            options=list(choices),
            default=list(choices)[:8],
            key="bracket_competitors",
        )

        st.caption(
            "Countries are shuffled into a "
            "knockout bracket. Byes are assigned "
            "when necessary."
        )

        if st.button(
            "🏁 Create Olympic Tournament",
            type="primary",
            disabled=len(selected) < 2,
        ):
            st.session_state.live_bracket = (
                start_bracket(
                    [choices[x] for x in selected]
                )
            )
            st.rerun()

        return

    # ---------- TOURNAMENT CONTROLS ----------

    col1, col2 = st.columns([4, 1])

    with col1:
        st.write(
            f"**Countries entered:** "
            f"{len(state['entrants'])}"
            f" · **Match format:** "
            f"{MATCH_ARROWS} arrows per athlete"
        )

    with col2:
        if st.button("End Tournament"):
            st.session_state.live_bracket = None
            st.rerun()

    # ---------- COMPLETED CHAMPIONSHIP ----------

    if state["phase"] == "complete":
        gold = BY_CODE[
            state["medals"]["gold"]
        ]
        silver = BY_CODE[
            state["medals"]["silver"]
        ]

        st.balloons()

        st.title(
            "🏅 OLYMPIC MEDAL CEREMONY"
        )

        st.markdown(
            f"## 🥇 {gold['flag']} "
            f"{gold['country']}"
        )

        st.markdown(
            f"### 🥈 {silver['flag']} "
            f"{silver['country']}"
        )

        if "bronze" in state["medals"]:
            bronze = BY_CODE[
                state["medals"]["bronze"]
            ]

            medal_podium(
                gold, silver, bronze
            )

        st.caption(
            "Classroom medals are simulated "
            "and are not actual Paris 2024 results."
        )

    # ---------- ACTIVE MATCH ----------

    else:
        current = active_match(state)

        shots_taken = len(
            current["shots"][0]
        )

        progress = (
            1.0 if current["resolved"]
            else min(
                1.0,
                shots_taken / MATCH_ARROWS
            )
        )

        st.progress(progress)

        match_visual(current)

        if current["resolved"]:
            winner = BY_CODE[
                current["winner"]
            ]

            st.success(
                f"🏆 {winner['flag']} "
                f"{winner['country']} WINS!"
            )

            if st.button(
                "➡️ Next Match",
                type="primary",
                use_container_width=True,
            ):
                next_match(state)
                st.rerun()

        elif current["shootout"]:
            st.warning(
                "TIED AFTER 10 ARROWS! "
                "Each country shoots again "
                "until one hits a perfect 10 "
                "and the other does not."
            )

            if st.button(
                "🎯 SHOOT-OFF · Release Both Arrows",
                type="primary",
                use_container_width=True,
            ):
                fire_shootout(state)
                st.rerun()

        else:
            number = shots_taken + 1

            if st.button(
                f"🏹 RELEASE BOTH ARROWS "
                f"· ROUND {number}/{MATCH_ARROWS}",
                type="primary",
                use_container_width=True,
            ):
                fire_pair(state)
                st.rerun()

    # ---------- TOURNAMENT PROGRESS ----------

    st.divider()
    st.markdown("#### 📋 Tournament Progress")

    if state["phase"] == "knockout":
        for match in state["matches"]:
            names = [
                BY_CODE[c]["country"]
                if c else "BYE"
                for c in match["codes"]
            ]

            status = (
                "✅ " + BY_CODE[
                    match["winner"]
                ]["country"]
                if match["resolved"]
                else "⏳ Waiting"
            )

            st.write(
                f"{match['title']}: "
                f"{names[0]} vs {names[1]} "
                f"— {status}"
            )

    for event in state["history"][-16:]:
        if isinstance(event, str):
            st.caption(event)
        else:
            winner = BY_CODE[
                event["winner"]
            ]
            loser = BY_CODE[
                event["loser"]
            ]

            st.write(
                f"✅ {event['round']}: "
                f"{winner['flag']} "
                f"{winner['country']} defeats "
                f"{loser['country']} "
                f"— {event['score'][0]} to "
                f"{event['score'][1]}"
            )

    st.caption(
        "The model uses each athlete's probability "
        "of scoring a perfect 10. It does not "
        "simulate exact arrow ring scores."
    )


# ==================================================
# MAIN NAVIGATION
# ==================================================

mode = st.radio(
    "App mode",
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
    "Dataset: Paris 2024 men's individual "
    "recurve ranking round. Each athlete "
    "shot 72 arrows. Simulated attempts use "
    "independent Bernoulli trials with "
    "p = perfect 10s ÷ 72. "
    "This is a simplified probability model, "
    "not an official Olympic scoring simulation."
)
