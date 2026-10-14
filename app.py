import csv
import html
import math
import hmac
import random
import secrets
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Olympic Archery | Sports by the Numbers", page_icon="🏹", layout="wide")

DATA_FILE = Path(__file__).with_name("athletes.csv")
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
st.markdown('<div class="hero"><div class="eyebrow">DOVER TIGERS · SPORTS BY THE NUMBERS</div><div class="huge">🏹 ROAD TO GOLD</div><div class="subtitle">OLYMPIC ARCHERY CHAMPIONSHIP · Paris 2024 probability lab</div></div>', unsafe_allow_html=True)
st.caption("Olympic results determine the model probability. Every in-app arrow and medal result is a new classroom simulation, not an Olympic replay.")


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


def new_match(codes, title):
    return {"codes": list(codes), "title": title, "shots": [[], []],
            "resolved": False, "winner": None, "loser": None,
            "shootout": False, "shootout_rounds": 0, "last_reveal": None}


def start_bracket(codes):
    entries = list(codes)
    secrets.SystemRandom().shuffle(entries)
    size = 1 << (len(entries) - 1).bit_length()
    # Distribute byes among pairs, so no match has two empty entries.
    byes = size - len(entries)
    entries_with_byes = []
    extra = entries[:]
    for i in range(size // 2):
        if i < byes:
            entries_with_byes.extend([extra.pop(0), None])
        else:
            entries_with_byes.extend([extra.pop(0), extra.pop(0)])
    state = {"phase": "knockout", "round_number": 1,
             "entrants": list(codes), "matches": [], "match_index": 0,
             "winners": [], "semifinal_losers": [], "medal_queue": [],
             "medals": {}, "history": []}
    if len(codes) == 2:
        state["phase"] = "medals"
        state["medal_queue"] = [new_match(entries, "🥇 GOLD MEDAL FINAL")]
    else:
        state["matches"] = [new_match(entries_with_byes[i:i+2],
                         f"ROUND 1 · MATCH {i//2+1}")
                          for i in range(0, size, 2)]
        skip_byes(state)
    return state


def active_match(state):
    if state["phase"] == "knockout":
        return state["matches"][state["match_index"]]
    if state["phase"] == "medals":
        return state["medal_queue"][0]
    return None


def skip_byes(state):
    # Automatically progress competitors who draw a bye.
    while state["phase"] == "knockout":
        while state["match_index"] < len(state["matches"]):
            match = state["matches"][state["match_index"]]
            present = [c for c in match["codes"] if c is not None]
            if len(present) == 2:
                return
            if len(present) == 1:
                match["resolved"] = True
                match["winner"] = present[0]
                state["winners"].append(present[0])
                state["history"].append(f"{BY_CODE[present[0]]['country']} advances with a bye")
            state["match_index"] += 1
        finish_round(state)


def finish_round(state):
    winners = state["winners"][:]
    state["winners"] = []
    if len(winners) == 2:
        # Semifinals are complete. Bronze is played before the gold final.
        queue = []
        if len(state["semifinal_losers"]) == 2:
            queue.append(new_match(state["semifinal_losers"], "🥉 BRONZE MEDAL MATCH"))
        elif len(state["entrants"]) == 3 and len(state["semifinal_losers"]) == 1:
            # Three-team field: the other finalist received a bye;
            # the sole semifinal loser takes bronze automatically.
            state["medals"]["bronze"] = state["semifinal_losers"][0]
        queue.append(new_match(winners, "🥇 GOLD MEDAL FINAL"))
        state["medal_queue"] = queue
        state["phase"] = "medals"
        return
    if len(winners) < 2:
        raise ValueError("Knockout bracket lost competitors.")
    state["round_number"] += 1
    state["matches"] = [new_match(winners[i:i+2],
                        f"ROUND {state['round_number']} · MATCH {i//2+1}")
                        for i in range(0, len(winners), 2)]
    state["match_index"] = 0
    skip_byes(state)


def fire_pair(state):
    match = active_match(state)
    a, b = (BY_CODE[c] for c in match["codes"])
    rng = secrets.SystemRandom()
    pair = [rng.random() < a["p"], rng.random() < b["p"]]
    for k in range(2):
        match["shots"][k].append(pair[k])
    match["last_reveal"] = pair
    if len(match["shots"][0]) >= MATCH_ARROWS:
        score_a, score_b = map(sum, match["shots"])
        if score_a == score_b:
            match["shootout"] = True
        else:
            resolve_match(state, 0 if score_a > score_b else 1)


def fire_shootout(state):
    match = active_match(state)
    a, b = (BY_CODE[c] for c in match["codes"])
    rng = secrets.SystemRandom()
    pair = [rng.random() < a["p"], rng.random() < b["p"]]
    for k in range(2):
        match["shots"][k].append(pair[k])
    match["last_reveal"] = pair
    match["shootout_rounds"] += 1
    if pair[0] != pair[1]:
        resolve_match(state, 0 if pair[0] else 1)


def resolve_match(state, index):
    match = active_match(state)
    win = match["codes"][index]
    lose = match["codes"][1-index]
    match["winner"] = win
    match["loser"] = lose
    match["resolved"] = True
    state["history"].append({
        "round": match["title"], "winner": win, "loser": lose,
        "score": [sum(match["shots"][0][:MATCH_ARROWS]),
                  sum(match["shots"][1][:MATCH_ARROWS])],
        "shootout_rounds": match["shootout_rounds"],
    })


def next_match(state):
    match = active_match(state)
    assert match and match["resolved"]
    if state["phase"] == "medals":
        if "BRONZE" in match["title"]:
            state["medals"]["bronze"] = match["winner"]
        else:
            state["medals"]["gold"] = match["winner"]
            state["medals"]["silver"] = match["loser"]
        state["medal_queue"].pop(0)
        if not state["medal_queue"]:
            state["phase"] = "complete"
        return
    # For the semifinals, save both losers for the bronze match.
    if len(state["matches"]) == 2:
        state["semifinal_losers"].append(match["loser"])
    state["winners"].append(match["winner"])
    state["match_index"] += 1
    skip_byes(state)


def match_visual(match):
    a, b = (BY_CODE[c] for c in match["codes"])
    scores = [sum(s) for s in match["shots"]]
    st.markdown(f"### {match['title']}")
    st.caption("Press **Release both arrows** to reveal one shot from each country. Each arrow uses its own athlete's real 2024 perfect-10 rate.")
    cols = st.columns(2, gap="small")
    for k, (col, athlete) in enumerate(zip(cols, [a, b])):
        with col:
            st.markdown(f"#### {athlete['flag']} {athlete['country']}")
            st.caption(athlete["athlete"])
            n = len(match["shots"][k])
            st.metric("Perfect 10s", f"{scores[k]} / {n}")
            archery_visual(match["shots"][k], heading="MATCH TARGET", compact=True)
            st.markdown(" ".join("🎯" if hit else "✕" for hit in match["shots"][k]) or "Ready to shoot")
    if match["last_reveal"] is not None:
        words = ["🎯 PERFECT 10!" if hit else "🏹 Not a 10" for hit in match["last_reveal"]]
        st.info(f"Last arrows: {a['flag']} {words[0]}   ·   {b['flag']} {words[1]}")
    if match["shootout_rounds"]:
        st.warning(f"Sudden-death shoot-off: {match['shootout_rounds']} extra arrow(s) per country.")



# ==================================================
# V4: TOURNAMENT BROADCAST DISPLAY
# ==================================================

st.markdown("""
<style>
.match-head {padding:15px 20px; background:linear-gradient(90deg,#102d4c,#234663);
 border:1px solid #58728b;border-radius:16px;color:white;text-align:center;margin:12px 0}
.match-head .round {font-size:12px;letter-spacing:3px;color:#ffdb96;font-weight:800}
.match-head .countries {font-size:clamp(20px,3vw,38px);font-weight:900;letter-spacing:.3px}
.match-head .versus {color:#ffbd65;padding:0 12px;font-size:18px}
.score-fight {display:flex;justify-content:center;align-items:center;gap:22px;
 background:#0b243c;color:white;padding:12px;border-radius:14px;margin:8px 0 12px}
.score-fight .score {font-size:clamp(35px,5vw,64px);font-weight:900;line-height:1}
.score-fight .center {font-size:13px;text-transform:uppercase;letter-spacing:2px;color:#c8d6e1;text-align:center}
.score-fight .leading {color:#ffd078}
.dramatic-banner {background:linear-gradient(110deg,#612b16,#a24b15);border:2px solid #f7c86d;
 padding:15px;border-radius:14px;color:#fff;text-align:center;font-size:clamp(17px,2.5vw,27px);font-weight:800;margin:12px 0}
.tournament-board {border:1px solid #385673;background:#122b45;color:#fff;
 padding:16px;border-radius:16px;margin:12px 0}
.tournament-board .label {font-size:12px;font-weight:900;color:#ffcf78;letter-spacing:2px;margin-bottom:8px}
.tournament-board .matchline {font-size:14px;padding:8px;border-bottom:1px solid #34536d}
.ceremony {background:linear-gradient(135deg,#102640,#38527c,#8b5f21);border:2px solid #e4c379;
 color:white;padding:25px;border-radius:20px;text-align:center;margin:16px 0}
.ceremony .big {font-size:clamp(28px,5vw,52px);font-weight:900}
.ceremony .country {font-size:clamp(24px,3.5vw,43px);font-weight:800}
</style>
""", unsafe_allow_html=True)


def country_short(code):
    if code is None:
        return "BYE"
    a = BY_CODE[code]
    return f"{a['flag']} {html.escape(a['country'])}"


def round_overview(state):
    if state["phase"] == "complete":
        return
    if state["phase"] == "medals":
        matches = state["medal_queue"]
        label = "MEDAL MATCHES"
    else:
        matches = state["matches"]
        label = f"ROUND {state['round_number']} · BRACKET"
    lines=[]
    for m in matches:
        left,right=(country_short(c) for c in m["codes"])
        if m["resolved"]:
            status = "🏁 " + country_short(m["winner"]) + " advances"
        else:
            status = "⏳ Up next" if m is active_match(state) else "Upcoming"
        lines.append(f'<div class="matchline">{left} <b>vs</b> {right} · {status}</div>')
    st.markdown('<div class="tournament-board"><div class="label">'+label+'</div>'+''.join(lines)+'</div>',unsafe_allow_html=True)


def broadcast_match(match):
    a,b=(BY_CODE[c] for c in match["codes"])
    count=len(match["shots"][0]); scores=[sum(x) for x in match["shots"]]
    title=html.escape(match['title'])
    st.markdown(f"""<div class="match-head"><div class="round">{title}</div>
    <div class="countries">{country_short(a['code'])}<span class="versus">VS</span>{country_short(b['code'])}</div> </div>""",unsafe_allow_html=True)
    leading=max(scores)
    c0=' leading' if scores[0]>scores[1] else ''
    c1=' leading' if scores[1]>scores[0] else ''
    st.markdown(f"""<div class="score-fight"><div class="score{c0}">{scores[0]}</div>
    <div class="center">PERFECT 10s<br/>ARROW {min(count,10)} / 10<br/>
{('SHOOT-OFF' if match['shootout'] else 'LIVE')}</div>
    <div class="score{c1}">{scores[1]}</div> </div>""",unsafe_allow_html=True)
    col1,col2=st.columns(2,gap='small')
    for col,a_,shots in ((col1,a,match['shots'][0]),(col2,b,match['shots'][1])):
        with col:
            st.markdown(f"**{a_['flag']} {a_['country']}** · {a_['athlete']}")
            archery_visual(shots,heading="LIVE MATCH",compact=True)
            st.caption(' '.join('🎯' if x else '➖' for x in shots) or 'Awaiting opening arrow')
    if match['last_reveal'] is not None:
        p=match['last_reveal']
        result=lambda x: 'PERFECT 10 🎯' if x else 'NOT A 10'
        st.markdown(f"**Most recent arrows:** {a['flag']} {result(p[0])}  |  {b['flag']} {result(p[1])}")
    if not match['resolved']:
        left=10-count
        if match['shootout']:
            st.markdown('<div class="dramatic-banner">⚡ SUDDEN DEATH — ONE PERFECT 10 CAN DECIDE IT!</div>',unsafe_allow_html=True)
        elif 0<left<=3:
            st.markdown(f'<div class="dramatic-banner">🔥 FINAL {left} ARROW{"S" if left!=1 else ""} — THE MEDALS ARE ON THE LINE!</div>',unsafe_allow_html=True)
        elif count and scores[0]==scores[1]:
            st.info('Dead even! Each next arrow could change the match.')
        elif count:
            leader=a if scores[0]>scores[1] else b
            st.info(f"{leader['flag']} {leader['country']} leads by {abs(scores[0]-scores[1])} perfect 10(s).")


def ceremony_reveal(state):
    phase=st.session_state.get('ceremony_step',0)
    medals=state['medals']
    st.title('🏟️ THE OLYMPIC MEDAL CEREMONY')
    if phase==0:
        st.markdown('<div class="ceremony"><div class="big">THE FINAL RESULTS ARE IN.</div><p>Who will stand on the podium?</p></div>',unsafe_allow_html=True)
        if st.button('🥉 Reveal Bronze' if 'bronze' in medals else '🥈 Reveal Silver',type='primary',use_container_width=True):
            st.session_state.ceremony_step=1;st.rerun()
        return
    if 'bronze' in medals:
        a=BY_CODE[medals['bronze']]
        st.markdown(f'<div class="ceremony">🥉 BRONZE MEDAL<div class="country">{country_short(a["code"])}</div><div>{html.escape(a["athlete"])}</div></div>',unsafe_allow_html=True)
    if phase==1 and 'bronze' in medals:
        if st.button('🥈 Reveal Silver',type='primary',use_container_width=True):
            st.session_state.ceremony_step=2;st.rerun()
        return
    if phase==1 and 'bronze' not in medals:
        phase=2
    silver=BY_CODE[medals['silver']]
    st.markdown(f'<div class="ceremony">🥈 SILVER MEDAL<div class="country">{country_short(silver["code"])}</div><div>{html.escape(silver["athlete"])}</div></div>',unsafe_allow_html=True)
    if phase==2:
        if st.button('🥇 REVEAL OLYMPIC GOLD',type='primary',use_container_width=True):
            st.session_state.ceremony_step=3;st.rerun()
        return
    gold=BY_CODE[medals['gold']]
    st.balloons()
    st.markdown(f'<div class="ceremony">🏆 🥇 OLYMPIC GOLD 🥇 🏆<div class="big">{country_short(gold["code"])}</div><div>{html.escape(gold["athlete"])}</div></div>',unsafe_allow_html=True)
    if 'bronze' in medals:
        bronze=BY_CODE[medals['bronze']]
        medal_podium([{'athlete':gold,'score':'Gold'},{'athlete':silver,'score':'Silver'},{'athlete':bronze,'score':'Bronze'}])
    st.caption('These medals are awarded in the classroom probability simulation—not at Paris 2024.')


def teacher_mode():
    st.subheader('🏟️ Teacher Championship · Live Knockout Tournament')
    try:
        teacher_pin=st.secrets.get('TEACHER_PIN','')
    except Exception:
        teacher_pin=''
    if not teacher_pin:
        st.error('Set TEACHER_PIN in Streamlit Cloud Secrets.')
        st.code('TEACHER_PIN = "your-private-pin"',language='toml')
        return
    if not st.session_state.get('teacher_authenticated',False):
        supplied=st.text_input('Teacher PIN',type='password')
        if st.button('Unlock teacher dashboard'):
            if hmac.compare_digest(str(supplied),str(teacher_pin)):
                st.session_state.teacher_authenticated=True;st.rerun()
            else:st.error('Incorrect PIN')
        return
    state=st.session_state.get('live_bracket')
    if state is None:
        choices={athlete_label(a):a['code'] for a in ATHLETES}
        selected=st.multiselect('Choose competing countries (2–24)',list(choices),default=list(choices)[:8],key='bracket_competitors')
        st.caption('Knockout bracket; byes are assigned where necessary. Classroom results use the real Olympic perfect-10 rates as model probabilities.')
        if st.button('🏁 Create Olympic Tournament',type='primary',disabled=len(selected)<2):
            st.session_state.live_bracket=start_bracket([choices[x] for x in selected])
            st.session_state.ceremony_step=0
            st.rerun()
        return
    top1,top2=st.columns([4,1])
    with top1: st.write(f"**{len(state['entrants'])} countries entered** · 10 arrows per competitor per match · Teacher-controlled")
    with top2:
        if st.button('End Tournament'):
            st.session_state.live_bracket=None
            st.session_state.ceremony_step=0
            st.rerun()
    if state['phase']=='complete':
        ceremony_reveal(state)
    else:
        current=active_match(state)
        round_overview(state)
        st.progress(1.0 if current['resolved'] else min(1.0,len(current['shots'][0])/MATCH_ARROWS))
        broadcast_match(current)
        if current['resolved']:
            winner=BY_CODE[current['winner']]
            st.markdown(f'<div class="dramatic-banner">🏆 {html.escape(winner["flag"])} {html.escape(winner["country"])} WINS THE MATCH!</div>',unsafe_allow_html=True)
            if st.button('➡️ Advance to Next Match',type='primary',use_container_width=True):
                next_match(state)
                st.rerun()
        elif current['shootout']:
            if st.button('⚡ RELEASE SUDDEN-DEATH ARROWS',type='primary',use_container_width=True):
                fire_shootout(state);st.rerun()
        else:
            count=len(current['shots'][0])
            label=f'🏹 RELEASE BOTH ARROWS · {count+1} / 10'
            if count>=7:label=f'🔥 FINAL ARROWS · RELEASE {count+1} / 10'
            if st.button(label,type='primary',use_container_width=True):
                fire_pair(state);st.rerun()
    with st.expander('📋 Completed match results',expanded=False):
        if not state['history']:
            st.write('No completed matches yet.')
        for event in state['history']:
            if isinstance(event,str):st.caption(event)
            else:
                a=BY_CODE[event['winner']];b=BY_CODE[event['loser']]
                st.write(f"{event['round']}: **{a['flag']} {a['country']}** defeated {b['country']} · {event['score'][0]}–{event['score'][1]}"+(f" · {event['shootout_rounds']} shoot-off round(s)" if event['shootout_rounds'] else ''))
    st.caption('Probability model: each arrow independently scores a perfect 10 with p = athlete perfect 10s / 72. Other ring scores are not modeled. Tournament is local to this teacher session.')

mode=st.radio("App mode",["🎓 Student Training","🏆 Teacher Championship"],horizontal=True)
if mode.startswith('🎓'):
    student_mode()
else:
    teacher_mode()

st.divider()
st.caption("Dataset: Paris 2024 men's individual recurve ranking round, as transcribed into the Sports by the Numbers 24-country class cards. Each archer took 72 arrows. All new app shots use independent Bernoulli trials with p = perfect 10s ÷ 72. This simplified model does not estimate actual chances of winning Olympic medals.")
