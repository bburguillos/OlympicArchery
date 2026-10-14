import csv
import html
import math
import hmac
import random
import secrets
from base64 import b64encode
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Olympic Archery | Sports by the Numbers", page_icon="🏹", layout="wide")

DATA_FILE = Path(__file__).with_name("athletes.csv")
ASSET_DIR = Path(__file__).parent / "assets"
ARROWS_IN_CHAMPIONSHIP = 20

@st.cache_data
def load_athletes():
    with DATA_FILE.open(encoding="utf-8", newline="") as handle:
        records = list(csv.DictReader(handle))
    for a in records:
        a["perfect_10s"] = int(a["perfect_10s"])
        a["arrows"] = int(a["arrows"])
        a["p"] = a["perfect_10s"] / a["arrows"]
    return records

ATHLETES = load_athletes()
BY_CODE = {a["code"]: a for a in ATHLETES}

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700;800;900&family=DM+Sans:wght@400;500;700&display=swap');
:root{--orange:#fbbf62;--deep:#10233c}
.block-container{padding-top:1.15rem;max-width:1200px}
.hero{border-radius:24px;padding:26px 30px;background:linear-gradient(115deg,#0d1b30 0%,#183953 70%,#8c4b21 100%);color:#fff!important;margin-bottom:18px;border:1px solid rgba(255,255,255,.16);box-shadow:0 12px 35px rgba(0,0,0,.14)}
.hero .eyebrow{font:700 12px 'DM Sans',sans-serif;letter-spacing:3px;color:#fbd09b}
.hero .huge{font:900 clamp(35px,5vw,64px) 'Barlow Condensed',sans-serif;letter-spacing:1px;line-height:1.03;margin:5px 0 9px}
.hero .subtitle{font:500 14px 'DM Sans',sans-serif;color:#d9e4f0}
.country-card{background:linear-gradient(135deg,#152c45,#244866);border:1px solid #4b7393;border-radius:17px;padding:18px 22px;color:white;margin:12px 0}
.country-card .country-head{display:flex;align-items:center;gap:16px}
.country-card .flag{font-size:48px;line-height:1.1}
.country-card .country{font:900 32px 'Barlow Condensed',sans-serif;line-height:1.15}
.country-card .athlete{font:500 15px 'DM Sans',sans-serif;color:#d5e7f6}
.country-card .stats{display:flex;gap:14px;flex-wrap:wrap;margin-top:14px;border-top:1px solid #547089;padding-top:13px;font-size:13px;color:#eaf3fb}
.step-note{padding:10px 14px;border-radius:11px;background:rgba(114,142,164,.13);border-left:4px solid #ed9a40;margin:10px 0;font-size:14px}
.score-strip{background:#152d46;color:white;border-radius:16px;padding:17px 20px;display:flex;align-items:center;justify-content:space-between;gap:12px;margin:12px 0}
.score-strip strong{font:900 31px 'Barlow Condensed',sans-serif;color:#ffd189}
.mini-history{font-size:21px;letter-spacing:6px;padding:8px 2px}
.podium-stage{display:flex;justify-content:center;align-items:flex-end;gap:10px;padding:24px 8px 12px;background:linear-gradient(#0e233a,#204663);border-radius:22px;margin:14px 0 20px;min-height:340px}
.podium-entry{flex:1;min-width:0;text-align:center;color:#fff}
.podium-entry .flag{font-size:clamp(28px,4vw,54px)}
.podium-entry .medal{font-size:25px}
.podium-entry .team{font:800 clamp(16px,2.4vw,28px) 'Barlow Condensed',sans-serif;overflow-wrap:anywhere}
.podium-entry .archer{font:500 12px 'DM Sans',sans-serif;opacity:.85;margin-bottom:8px}
.podium-entry .score{font:800 23px 'Barlow Condensed',sans-serif;margin:5px 0}
.podium-block{display:flex;align-items:center;justify-content:center;border-radius:10px 10px 0 0;color:#12263b;font:900 44px 'Barlow Condensed',sans-serif}
.podium-1{height:132px;background:linear-gradient(135deg,#ffe399,#b88723)}
.podium-2{height:92px;background:linear-gradient(135deg,#ecf3fb,#889cac)}
.podium-3{height:65px;background:linear-gradient(135deg,#f0bf8a,#9c632f)}
@media(max-width:620px){.hero{padding:22px 19px}.podium-stage{gap:4px;padding:16px 4px 8px}.podium-entry .archer{font-size:10px}.podium-entry .score{font-size:17px}.country-card .country{font-size:25px}}
</style>
""", unsafe_allow_html=True)
# Asset banners are cropped so no fixed sample scores or athlete names appear.
# Streamlit controls remain real, accessible widgets below the images.
def show_banner(name, max_height=None):
    path = ASSET_DIR / (name + "_banner.webp")
    if path.exists():
        st.image(str(path), use_container_width=True)
    else:
        st.info("Broadcast image missing: add the assets folder to your repository.")

show_banner("opening")
st.caption("Sports by the Numbers • Historical Paris 2024 perfect-10 rates determine the simulation. All tournament results are fictional classroom outcomes.")


def country_card(a):
    flag=html.escape(a['flag']); country=html.escape(a['country']); athlete=html.escape(a['athlete'])
    st.markdown(f"""<div class='country-card'><div class='country-head'><div class='flag'>{flag}</div><div><div class='country'>{country}</div><div class='athlete'>{athlete} · Paris 2024</div></div></div><div class='stats'><span>🎯 PERFECT 10s: <b>{a['perfect_10s']}</b></span><span>🏹 ARROWS SHOT: <b>{a['arrows']}</b></span><span>📍 MEN'S RECURVE RANKING ROUND</span></div></div>""",unsafe_allow_html=True)


def archery_visual(shots, heading="LIVE TARGET", compact=False):
    """Responsive binary-outcome target; arrow locations are illustrative only."""
    W, H = 560, 300
    cx, cy, rr = 143, 149, 116
    colors = ["#f8f8f2", "#171b23", "#29a6da", "#d93431", "#ffd549"]
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        'style="display:block;width:100%;height:auto;max-width:560px;margin:0 auto" '
        'role="img" aria-label="Archery target and simulated results">',
        '<style>@keyframes arrowLand{from{opacity:0;transform:scale(1.6)}to{opacity:1;transform:scale(1)}}'
        '.latest{animation:arrowLand .55s ease-out;transform-box:fill-box;transform-origin:center}</style>',
        f'<rect width="{W}" height="{H}" rx="17" fill="#11253e"/>',
        f'<circle cx="{cx}" cy="{cy}" r="{rr+6}" fill="#0a1625" stroke="#6595b2" stroke-width="2"/>',
    ]
    for i, col in enumerate(colors):
        radius = rr * (1 - i * .19)
        svg.append(f'<circle cx="{cx}" cy="{cy}" r="{radius:.1f}" fill="{col}" stroke="#203046" stroke-width="2"/>')
    ten_radius = rr * .20
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{ten_radius:.1f}" fill="#ffd549" stroke="#141719" stroke-width="2"/>')
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{ten_radius*.3:.1f}" fill="none" stroke="#1b2127" stroke-width="1.5"/>')
    for i, success in enumerate(shots):
        theta = i * 2.39996322973 + .4
        if success:
            rad = ten_radius * (.22 + .49 * ((i * 7) % 11) / 11)
        else:
            rad = ten_radius + 7 + (rr - ten_radius - 20) * ((i * 13 + 7) % 29) / 29
        x, y = cx + rad * math.cos(theta), cy + rad * math.sin(theta)
        latest = ' class="latest"' if i == len(shots)-1 else ''
        svg.extend([
            f'<line{latest} x1="{x-9:.1f}" y1="{y-9:.1f}" x2="{x+2:.1f}" y2="{y+2:.1f}" stroke="#172c41" stroke-width="2.5"/>',
            f'<circle{latest} cx="{x:.1f}" cy="{y:.1f}" r="4.5" fill="{("#00e4ad" if success else "#ff714b")}" stroke="#101d30" stroke-width="1.5"/>',
        ])
    hits, count = sum(shots), len(shots)
    heading = html.escape(heading)
    svg.extend([
        f'<text x="297" y="71" fill="#acc6da" font-family="Arial" font-size="14" font-weight="bold">{heading}</text>',
        f'<text x="297" y="125" fill="#ffffff" font-family="Arial" font-size="48" font-weight="900">{hits} / {count}</text>',
        '<text x="297" y="151" fill="#d6e7f2" font-family="Arial" font-size="13">PERFECT 10s</text>',
        '<circle cx="303" cy="190" r="5" fill="#00e4ad"/><text x="316" y="195" fill="#c2d5e4" font-family="Arial" font-size="13">Perfect 10</text>',
        '<circle cx="303" cy="220" r="5" fill="#ff714b"/><text x="316" y="225" fill="#c2d5e4" font-family="Arial" font-size="13">Not a 10</text>',
        '<text x="297" y="262" fill="#9cb8ce" font-family="Arial" font-size="11">Arrow locations are illustrative</text>',
        '</svg>',
    ])
    components.html('<html><body style="margin:0;background:transparent;overflow:hidden">'+''.join(svg)+'</body></html>',
                    height=306, scrolling=False)


def medal_podium(results):
    if len(results)<3:return
    chunks=[]
    for pos in [1,0,2]:
        r=results[pos];a=r['athlete'];place=pos+1
        medal={1:'🥇',2:'🥈',3:'🥉'}[place]
        chunks.append(f"""<div class='podium-entry'><div class='medal'>{medal}</div><div class='flag'>{html.escape(a['flag'])}</div><div class='team'>{html.escape(a['country'])}</div><div class='archer'>{html.escape(a['athlete'])}</div><div class='score'>{r['score'] if isinstance(r['score'], str) else str(r['score'])+' / 20'}</div><div class='podium-block podium-{place}'>{place}</div></div>""")
    st.markdown('<div class="podium-stage">'+''.join(chunks)+'</div>',unsafe_allow_html=True)


def calc_ok(answer, expected):
    return answer is not None and abs(float(answer)-expected) <= 0.51


def simulate(a, count, rng):
    # Uses the unrounded historical success probability, NEVER a student's entered percentage.
    return [rng.random() < a["p"] for _ in range(count)]


def target(success, key=""):
    if success is None:
        archery_visual([],heading="READY TO SHOOT")
    elif success:
        st.success("🎯 PERFECT 10! A simulated arrow hit the center.")
    else:
        st.info("🏹 Not a perfect 10. Exact ring points are not modeled.")


def athlete_label(a):
    return f'{a["flag"]} {a["country"]} — {a["athlete"]}'


def check_panel(a, prefix):
    st.markdown(f'**Historical results:** {a["perfect_10s"]} perfect 10s out of {a["arrows"]} ranking-round arrows.')
    st.caption("Calculate the probability on your worksheet first. Then enter your percentage below.")
    entered = st.number_input("Your calculated P(perfect 10), as a percent", min_value=0.0, max_value=100.0, value=None, step=0.1, format="%.1f", key=prefix+"_pct", placeholder="Example: 47.2")
    if entered is None:
        st.info("Enter your answer to check it and unlock training.")
        return False
    if calc_ok(entered, 100*a["p"]):
        st.success("Correct! Your probability is within 0.5 percentage points of the historical result. Training unlocked.")
        return True
    st.warning("Try again. Divide the number of perfect 10s by 72, then multiply by 100. Rounding to one decimal is fine.")
    return False


def student_mode():
    st.subheader("🌍 Olympic Village · Choose your country")
    options = {athlete_label(a): a for a in ATHLETES}
    selection = st.selectbox("Your assigned country and athlete", list(options))
    a = options[selection]
    old = st.session_state.get("student_code")
    if old != a["code"]:
        st.session_state.student_code = a["code"]
        st.session_state.training_shots = []
        st.session_state.training_prediction = None
        st.session_state.training_started = False
        st.session_state.student_stage = "🔐 Probability Check"
        st.session_state.athlete_unlocked = False
    country_card(a)
    stages = ["🔐 Probability Check", "🏹 Training Camp", "📋 Results & Reflection"]
    if "student_stage" not in st.session_state:
        st.session_state.student_stage = stages[0]
    stage = st.radio("Your next step", stages, key="student_stage", horizontal=True)
    if stage == stages[0]:
        unlocked = check_panel(a, "my")
        st.markdown("**Further worksheet questions:** Calculate P(not a 10), then predict how many perfect 10s you expect in 20 arrows.")
        st.caption("We never change the athlete's underlying real-data probability when a student enters an answer.")
        if unlocked:
            st.session_state.athlete_unlocked = True
            st.success("✅ Athlete unlocked! You're ready to practice.")
            st.button("🏹 Continue to Training Camp →", type="primary", use_container_width=True, on_click=lambda: st.session_state.update(student_stage=stages[1]))
    elif stage == stages[1]:
        unlocked = st.session_state.get("athlete_unlocked", False)
        if not unlocked:
            st.info("Complete the Probability Check first.")
        else:
            if not st.session_state.get("training_started",False):
                prediction = st.number_input("Predict perfect 10s in 10 training arrows",min_value=0,max_value=10,value=5,step=1,key="predict10")
                if st.button("Start 10-arrow training",type="primary"):
                    st.session_state.training_started = True
                    st.session_state.training_prediction = int(prediction)
                    st.session_state.training_shots = []
                    st.rerun()
            else:
                shots = st.session_state.training_shots
                st.markdown(f'<div class="score-strip"><span>TRAINING CAMP · {html.escape(a["country"])}<br><small>10-arrow practice session</small></span><strong>{sum(shots)} / {len(shots)}</strong></div>', unsafe_allow_html=True)
                st.progress(len(shots)/10)
                if shots:
                    archery_visual(shots,heading='TRAINING TARGET'); st.markdown('<div class="mini-history">'+' '.join('🎯' if v else '➖' for v in shots)+'</div>',unsafe_allow_html=True)
                else:
                    archery_visual([],heading="READY TO SHOOT")
                if len(shots)<10:
                    if st.button("Release next arrow 🏹",type="primary"):
                        shot=simulate(a,1,secrets.SystemRandom())[0]
                        st.session_state.training_shots = shots + [shot]
                        st.rerun()
                else:
                    st.success(f'Training complete: you predicted {st.session_state.training_prediction} perfect 10s and got {sum(shots)}.')
                    st.caption("Different results from your prediction are normal in a random simulation.")
                    st.button("📋 Continue to Results & Reflection →", type="primary",
                              use_container_width=True,
                              on_click=lambda: st.session_state.update(student_stage=stages[2]))
                    if st.button("Run another 10-arrow session"):
                        st.session_state.training_started=False
                        st.session_state.training_shots=[]
                        st.session_state.training_prediction=None
                        st.rerun()
    else:  # Results & Reflection
        shots=st.session_state.get("training_shots",[])
        if not shots:
            st.info("Complete training to see your results here.")
        else:
            archery_visual(shots,heading="YOUR FINAL TARGET")
            st.write(f'**Your result:** {sum(shots)}/{len(shots)} perfect 10s.')
            st.write(f'**Observed simulation success rate:** {sum(shots)/len(shots)*100:.1f}%')
            if st.session_state.get("training_prediction") is not None:
                st.write(f'**Your prediction:** {st.session_state.training_prediction} out of 10.')
            st.markdown("**Discuss:** Why might ten simulated shots differ from the athlete’s percentage based on 72 Olympic arrows?")
            st.caption("Record results on your worksheet. Version 1 does not store student records across visits or devices.")


def tournament(seed, competitors):
    rng = random.Random(seed)
    results=[]
    for a in competitors:
        shots=simulate(a,ARROWS_IN_CHAMPIONSHIP,rng)
        results.append({"athlete":a,"shots":shots,"score":sum(shots),"playoffs":[]})
    # A fair sudden-death tie-break: each tied group fires 1 additional shot per round
    # until medal ranks can be distinguished. A random coin toss after 200 rounds
    # is only a safety net against a pathological run of ties.
    for idx in range(3):
        if idx>=len(results):break
        results.sort(key=lambda r:(r["score"],r["playoffs"]),reverse=True)
        # Ties may involve the medal cutoff. Run shared additional shots, ranked lexicographically.
        while True:
            results.sort(key=lambda r:(r["score"],r["playoffs"]),reverse=True)
            target_key=(results[idx]["score"],tuple(results[idx]["playoffs"]))
            tied=[r for r in results if (r["score"],tuple(r["playoffs"]))==target_key]
            if len(tied)==1: break
            if len(tied[0]["playoffs"])>=200:
                rng.shuffle(tied)
                for k,r in enumerate(tied):r["playoffs"].append(int(k==0))
                break
            for r in tied:
                r["playoffs"].extend(simulate(r["athlete"],1,rng))
    results.sort(key=lambda r:(r["score"],r["playoffs"]),reverse=True)
    return results



# --------------------------------------------------
# VERSION 3: LIVE, TEACHER-CONTROLLED KNOCKOUT
# --------------------------------------------------
MATCH_ARROWS = 10



# ==================================================
# V5 · SIMULTANEOUS OLYMPIC BROADCAST TOURNAMENT
# ==================================================

st.markdown("""
<style>
.broadcast-banner{background:linear-gradient(110deg,#132d47,#23557c);color:#fff;
 border:1px solid #557a9a;border-radius:15px;padding:12px 17px;margin:9px 0 13px}
.broadcast-banner .big{font:900 clamp(25px,3vw,37px) 'Barlow Condensed',Arial,sans-serif}
.broadcast-banner .sub{color:#c1d9e7;font-size:12px;letter-spacing:1px}
.stButton>button[kind=primary]{min-height:53px;font-weight:800;border-radius:12px}
</style>""", unsafe_allow_html=True)


def new_match(codes, title):
    return {"codes": list(codes), "title": title, "shots": [[], []],
            "resolved": False, "winner": None, "loser": None,
            "shootout": False, "shootout_rounds": 0, "last_reveal": None,
            "bye": None}


def start_bracket(codes):
    if len(codes) < 2 or len(codes) > 24 or len(set(codes)) != len(codes):
        raise ValueError("Select 2 to 24 different countries.")
    entries = list(codes)
    secrets.SystemRandom().shuffle(entries)
    state = {"phase": "knockout", "round_number": 1, "entrants": entries[:],
             "matches": [], "semifinal_losers": [], "medals": {},
             "history": [], "ceremony_step": 0}
    if len(entries) == 2:
        state["phase"] = "medals"
        state["matches"] = [new_match(entries, "🥇 GOLD FINAL")]
        return state
    size = 1 << (len(entries) - 1).bit_length()
    byes = size - len(entries)
    matches = []
    for i in range(size // 2):
        if i < byes:
            m = new_match([entries.pop(0), None], f"ROUND 1 · MATCH {i+1}")
            m["resolved"] = True
            m["winner"] = m["codes"][0]
            m["bye"] = True
        else:
            m = new_match([entries.pop(0), entries.pop(0)], f"ROUND 1 · MATCH {i+1}")
        matches.append(m)
    state["matches"] = matches
    return state


def shot_pair(match):
    if match["resolved"]:
        return
    a, b = (BY_CODE[c] for c in match["codes"])
    rng = secrets.SystemRandom()
    pair = [rng.random() < a["p"], rng.random() < b["p"]]
    for k in range(2):
        match["shots"][k].append(pair[k])
    match["last_reveal"] = pair
    if len(match["shots"][0]) < MATCH_ARROWS:
        return
    score = [sum(s[:MATCH_ARROWS]) for s in match["shots"]]
    if score[0] != score[1]:
        settle_match(match, 0 if score[0] > score[1] else 1)
    else:
        match["shootout"] = True


def shootout_pair(match):
    if match["resolved"] or not match["shootout"]:
        return
    a, b = (BY_CODE[c] for c in match["codes"])
    rng = secrets.SystemRandom()
    pair = [rng.random() < a["p"], rng.random() < b["p"]]
    for k in range(2):
        match["shots"][k].append(pair[k])
    match["last_reveal"] = pair
    match["shootout_rounds"] += 1
    if pair[0] != pair[1]:
        settle_match(match, 0 if pair[0] else 1)


def settle_match(match, winning_index):
    match["resolved"] = True
    match["winner"] = match["codes"][winning_index]
    match["loser"] = match["codes"][1-winning_index]
    match["shootout"] = False


def advance_all_arrows(state):
    # All unfinished real matches advance by exactly one pair of arrows.
    for m in state["matches"]:
        if m["resolved"]:
            continue
        if m["shootout"]:
            shootout_pair(m)
        else:
            shot_pair(m)


def round_finished(state):
    return bool(state["matches"]) and all(m["resolved"] for m in state["matches"])


def finish_round(state):
    if not round_finished(state):
        return
    for m in state["matches"]:
        state["history"].append({"title": m["title"], "codes": m["codes"][:],
            "winner": m["winner"], "score": [sum(x[:MATCH_ARROWS]) for x in m["shots"]],
            "shootout": m["shootout_rounds"], "bye": bool(m["bye"])})
    if state["phase"] == "medals":
        for m in state["matches"]:
            if "BRONZE" in m["title"]:
                state["medals"]["bronze"] = m["winner"]
            else:
                state["medals"]["gold"] = m["winner"]
                state["medals"]["silver"] = m["loser"]
        state["phase"] = "complete"
        return
    matches = state["matches"]
    winners = [m["winner"] for m in matches]
    if len(matches) == 2:
        state["semifinal_losers"] = [m["loser"] for m in matches if m["loser"]]
    if len(winners) == 2:
        medal_matches = []
        if len(state["semifinal_losers"]) == 2:
            medal_matches.append(new_match(state["semifinal_losers"], "🥉 BRONZE MATCH"))
        elif len(state["entrants"]) == 3 and len(state["semifinal_losers"]) == 1:
            state["medals"]["bronze"] = state["semifinal_losers"][0]
        medal_matches.append(new_match(winners, "🥇 GOLD FINAL"))
        state["matches"] = medal_matches
        state["phase"] = "medals"
    else:
        state["round_number"] += 1
        state["matches"] = [new_match(winners[i:i+2],
            f'ROUND {state["round_number"]} · MATCH {i//2+1}')
            for i in range(0, len(winners), 2)]


def target_svg(shots, radius=54):
    # Small, inline SVG: full target always fits in its own compact box.
    colors = [(52, "#f0eee9"), (42, "#1e2530"), (32, "#28a5d7"),
              (22, "#e13d3b"), (12, "#fbd44f")]
    bits = ['<svg viewBox="0 0 120 120" style="width:100%;max-width:155px;'
            'height:auto;display:block;margin:auto" role="img" aria-label="Simulated arrows">']
    for r, color in colors:
        bits.append(f'<circle cx="60" cy="60" r="{r}" fill="{color}" stroke="#172c42" stroke-width="1"/>')
    for i, hit in enumerate(shots[-20:]):
        angle = i * 2.39996323
        if hit:
            dist = 3 + (i * 5) % 7
        else:
            dist = 15 + (i * 7) % 35
        x, y = 60 + dist * math.cos(angle), 60 + dist * math.sin(angle)
        color = "#04dba4" if hit else "#ff714b"
        bits.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="3.2" fill="{color}" stroke="#0e2530" stroke-width="1"/>')
    bits.append('</svg>')
    return ''.join(bits)


def one_match_html(m, idx):
    if m["bye"]:
        a = BY_CODE[m["winner"]]
        return (f'<div class="match"><div class="match-label">MATCH {idx+1} · BYE</div>'
                f'<div class="bye">{html.escape(a["flag"])} {html.escape(a["country"])} '
                'automatically advances</div></div>')
    cards = []
    for k, code in enumerate(m["codes"]):
        a = BY_CODE[code]
        s = m["shots"][k]
        last = ("🎯" if s[-1] else "✕") if s else "—"
        winning = ' winner' if m["resolved"] and code == m["winner"] else ''
        cards.append(f"""<div class="athlete{winning}">
            <div class="flag">{html.escape(a['flag'])}</div>
            <div class="name">{html.escape(a['country'])}</div>
            <div class="person">{html.escape(a['athlete'])}</div>
            {target_svg(s)}
            <div class="score">{sum(s[:MATCH_ARROWS])} <span>/ {min(len(s),MATCH_ARROWS)}</span></div>
            <div class="last">LAST: {last}</div>
        </div>""")
    status = ('🏁 WINNER: ' + html.escape(BY_CODE[m['winner']]['country'])
              if m["resolved"] else '⚡ SHOOT-OFF' if m["shootout"] else
              f'ARROW {len(m["shots"][0]) + 1} OF {MATCH_ARROWS}')
    return (f'<div class="match"><div class="match-label">{html.escape(m["title"])}</div>'
            '<div class="competitors">' + ''.join(cards) + '</div>'
            f'<div class="status">{status}</div></div>')


def broadcast_grid(state):
    if st.session_state.get("v6_broadcast_art", True):
        show_banner("match" if state["phase"] != "medals" else "medals")
    matches = state["matches"]
    n = len(matches)
    label = ("MEDAL MATCHES" if state["phase"] == "medals" else
             f'ROUND {state["round_number"]} · LIVE COMPETITION')
    unresolved = [m for m in matches if not m["resolved"]]
    normal_remaining = [max(0, MATCH_ARROWS-len(m["shots"][0])) for m in unresolved if not m["shootout"]]
    bottom = ('EVERY MATCH COMPLETE — ADVANCE TO NEXT STAGE' if not unresolved else
              'SUDDEN-DEATH SHOOT-OFF' if any(m["shootout"] for m in unresolved) else
              f'{max(normal_remaining,default=0)} ARROWS REMAINING')
    st.markdown(f"""<div class="broadcast-banner"><div class="sub">OLYMPIC PROBABILITY ARENA · LIVE</div>
        <div class="big">{label}</div><div class="sub">{bottom} · {len(unresolved)} MATCH(ES) STILL LIVE</div></div>""",
        unsafe_allow_html=True)
    # A single embedded grid prevents Streamlit elements/iframes from stretching the screen.
    cols = 2 if n >= 2 else 1
    html_doc = f"""<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1">
    <style>
    *{{box-sizing:border-box}}html,body{{margin:0;background:transparent;font-family:Arial,sans-serif;color:#fff}}
    .grid{{display:grid;grid-template-columns:repeat({cols},minmax(0,1fr));gap:10px}}
    .match{{background:linear-gradient(145deg,#132940,#1d4262);border:1px solid #42617e;border-radius:15px;
     padding:9px;min-width:0;overflow:hidden}}
    .match-label{{font-weight:800;color:#f6c988;letter-spacing:.5px;font-size:12px;min-height:20px}}
    .competitors{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:6px}}
    .athlete{{background:#0c2033;border:1px solid #284d69;border-radius:9px;text-align:center;min-width:0;padding:4px}}
    .athlete.winner{{border:2px solid #f5c56d}}
    .flag{{font-size:22px;line-height:24px}}
    .name{{font-weight:800;font-size:13px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
    .person{{font-size:10px;color:#bdd1de;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
    .score{{font-size:25px;font-weight:900;line-height:26px;color:#fff}}
    .score span{{color:#9cbed0;font-size:13px}}.last{{font-size:10px;color:#bbd7e7}}
    .status{{text-align:center;color:#f5ca8a;font-size:11px;font-weight:800;padding:5px 1px 1px}}
    .bye{{font-size:18px;text-align:center;padding:70px 5px 80px}}
    @media(max-width:600px){{.grid{{grid-template-columns:1fr}}}}
    </style></head><body><div class="grid">"""+ ''.join(one_match_html(m,i) for i,m in enumerate(matches)) + '</div></body></html>'
    # Height scales with compact 2-column card rows; no scroll within board.
    rows = (n+cols-1)//cols
    components.html(html_doc, height=rows*300+20, scrolling=False)


def dynamic_bracket(state):
    """Actual match list, never static image team labels."""
    st.markdown("### 🏆 Current tournament bracket")
    if st.session_state.get("v6_broadcast_art", True):
        show_banner("bracket")
    cols = st.columns(2 if len(state["matches"])>1 else 1)
    for index, match in enumerate(state["matches"]):
        labels = []
        for code in match["codes"]:
            a=BY_CODE.get(code)
            labels.append(f'{a["flag"]} {a["country"]}' if a else 'BYE')
        status = (f'✅ {BY_CODE[match["winner"]]["country"]} advances'
                  if match["resolved"] else '⏳ In progress')
        with cols[index % len(cols)]:
            st.markdown(f'**{match["title"]}**  \n{labels[0]} vs {labels[1]}  \n{status}')
    with st.expander("Completed-round bracket history", expanded=False):
        for entry in state["history"]:
            winner=BY_CODE[entry["winner"]]
            st.write(f'{entry["title"]}: {winner["flag"]} {winner["country"]} advances')


def ceremony_reveal_v5(state):
    step = state["ceremony_step"]
    medals = state["medals"]
    if st.session_state.get("v6_broadcast_art", True):
        show_banner("medals")
    st.title('🏟️ OLYMPIC MEDAL CEREMONY')
    def medal_line(key, symbol):
        a = BY_CODE[medals[key]]
        st.markdown(f'### {symbol} {a["flag"]} {a["country"]} — {a["athlete"]}')
    if step == 0:
        st.info('The medalists have been decided. Are you ready to reveal the podium?')
        if st.button('🥉 Reveal Bronze' if 'bronze' in medals else '🥈 Reveal Silver',type='primary',use_container_width=True):
            state['ceremony_step'] = 1
            st.rerun()
        return
    if 'bronze' in medals:
        medal_line('bronze','🥉')
        if step == 1:
            if st.button('🥈 Reveal Silver',type='primary',use_container_width=True):
                state['ceremony_step'] = 2
                st.rerun()
            return
    else:
        if step == 1:
            state['ceremony_step'] = 2
            st.rerun()
    medal_line('silver','🥈')
    if step == 2:
        if st.button('🥇 REVEAL GOLD',type='primary',use_container_width=True):
            state['ceremony_step'] = 3
            st.rerun()
        return
    medal_line('gold','🥇')
    st.balloons()
    if 'bronze' in medals:
        medal_podium([{'athlete':BY_CODE[medals['gold']],'score':'Gold'},
                      {'athlete':BY_CODE[medals['silver']],'score':'Silver'},
                      {'athlete':BY_CODE[medals['bronze']],'score':'Bronze'}])
    st.caption('These are simulated classroom medals, not actual Paris 2024 results.')


def teacher_mode():
    st.subheader('🏟️ Teacher Championship · Simultaneous Broadcast')
    try:
        teacher_pin = st.secrets.get('TEACHER_PIN','')
    except Exception:
        teacher_pin = ''
    if not teacher_pin:
        st.error('Set TEACHER_PIN in Streamlit Cloud Secrets.')
        return
    if not st.session_state.get('teacher_authenticated',False):
        supplied = st.text_input('Teacher PIN',type='password')
        if st.button('Unlock teacher dashboard'):
            if hmac.compare_digest(str(supplied),str(teacher_pin)):
                st.session_state.teacher_authenticated=True
                st.rerun()
            else:
                st.error('Incorrect PIN')
        return
    state = st.session_state.get('live_bracket')
    if state is None:
        choices = {athlete_label(a):a['code'] for a in ATHLETES}
        selected = st.multiselect('Choose competing countries (2–24)',list(choices),
                                  default=list(choices)[:8],key='bracket_competitors')
        st.caption('All matches in each knockout round run simultaneously. Byes advance automatically.')
        if st.session_state.get("v6_broadcast_art", True):
            show_banner("bracket")
        if st.button('🏁 Create Olympic Tournament',type='primary',disabled=len(selected)<2):
            st.session_state.live_bracket=start_bracket([choices[x] for x in selected])
            st.rerun()
        return
    top1,top2 = st.columns([4,1])
    with top1:
        st.write(f'**{len(state["entrants"])} countries** · '
                 f'**{len(state["matches"])} matches this round** · Teacher-controlled')
    with top2:
        if st.button('End Tournament'):
            st.session_state.live_bracket=None
            st.rerun()
    if state['phase']=='complete':
        ceremony_reveal_v5(state)
    else:
        broadcast_grid(state)
        if round_finished(state):
            if st.button('➡️ ADVANCE ALL WINNERS',type='primary',use_container_width=True):
                finish_round(state)
                st.rerun()
        else:
            unresolved = [m for m in state['matches'] if not m['resolved']]
            shootouts = any(m['shootout'] for m in unresolved)
            label = '⚡ RELEASE SHOOT-OFF ARROWS' if shootouts else '🏹 RELEASE ALL ARROWS · NEXT ROUND'
            if st.button(label,type='primary',use_container_width=True):
                advance_all_arrows(state)
                st.rerun()
            # A multi-shot control is useful when the classroom needs to move quickly.
            if not shootouts:
                if st.button('⏩ FAST-FORWARD 3 ARROWS',use_container_width=True):
                    for _ in range(3):
                        if round_finished(state):
                            break
                        advance_all_arrows(state)
                    st.rerun()
            if any(m['resolved'] for m in state['matches']):
                st.caption('Finished matches remain frozen while other matches finish their arrows or shoot-offs.')
    with st.expander('🏅 View live bracket and countries', expanded=False):
        dynamic_bracket(state)
    with st.expander('📋 Completed rounds and results'):
        for event in state['history']:
            a=BY_CODE[event['winner']]
            if event['bye']:
                st.write(f'{event["title"]}: {a["flag"]} {a["country"]} received a bye')
            else:
                c0,c1=event['codes']
                st.write(f'{event["title"]}: {BY_CODE[c0]["country"]} '
                         f'{event["score"][0]} – {event["score"][1]} {BY_CODE[c1]["country"]} '
                         f'· winner {a["flag"]} {a["country"]}'
                         + (' (shoot-off)' if event['shootout'] else ''))
    st.caption('Probability model: each arrow independently scores a perfect 10 with '
               'p = Olympic athlete perfect 10s / 72. The positions of arrow marks are illustrative.')


st.toggle('🎬 Cinematic Broadcast Graphics (turn off for compact view)',
          value=True, key='v6_broadcast_art')
mode = st.radio('App mode' ,['🎓 Student Training','🏆 Teacher Championship'],horizontal=True)
if mode.startswith('🎓'):
    student_mode()
else:
    teacher_mode()
st.divider()
st.caption('Dataset: Paris 2024 men’s individual recurve ranking round. '
           'This classroom tournament models perfect 10 versus not 10, not full Olympic point scoring. '
           'Teacher tournament state is local to this browser session.')
