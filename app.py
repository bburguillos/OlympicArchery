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


def archery_visual(shots, heading='LIVE TARGET', compact=False):
    """A binary-outcome visualization. Marker locations illustrative, not actual arrow scores."""
    W=680; H=400 if not compact else 330
    cx=220 if not compact else 190; cy=200 if not compact else 166
    rr=168 if not compact else 139
    # Olympic-style rings for context, never labels for simulated per-ring scores.
    colors=['#f8f8f2','#171b23','#29a6da','#d93431','#ffd549']
    svg=[f'<svg viewBox="0 0 {W} {H}" width="100%" height="100%" role="img" aria-label="Archery target with simulated perfect ten and non-ten markers">',
         '<style>@keyframes arrowLand{from{opacity:0;transform:scale(2)}to{opacity:1;transform:scale(1)}}.latest{animation:arrowLand .55s ease-out;transform-box:fill-box;transform-origin:center}</style>',
         f'<rect width="{W}" height="{H}" rx="20" fill="#11253e"/>',
         f'<circle cx="{cx}" cy="{cy}" r="{rr+11}" fill="#0a1625" stroke="#6595b2" stroke-width="2"/>']
    for i,col in enumerate(colors):
        r=rr*(1-i*.19)
        svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r:.1f}" fill="{col}" stroke="#203046" stroke-width="2"/>')
    # Central perfect-10 visual threshold (only center is a success).
    ten_radius=rr*.20
    svg.extend([f'<circle cx="{cx}" cy="{cy}" r="{ten_radius:.1f}" fill="#ffd549" stroke="#141719" stroke-width="2"/>',
                f'<circle cx="{cx}" cy="{cy}" r="{ten_radius*.3:.1f}" fill="none" stroke="#1b2127" stroke-width="1.5"/>',
                f'<line x1="{cx-rr-14}" y1="{cy}" x2="{cx+rr+14}" y2="{cy}" stroke="#11243b" stroke-opacity=".15"/>'])
    # Deterministic presentation coordinates, not independently generated scores.
    for i,success in enumerate(shots):
        theta=i*2.39996322973+0.4
        if success:
            rad=ten_radius*(.22+.49*((i*7)%11)/11)
        else:
            rad=ten_radius+11+(rr-ten_radius-28)*((i*13+7)%29)/29
        x=cx+rad*math.cos(theta); y=cy+rad*math.sin(theta)
        latest=' class="latest"' if i==len(shots)-1 else ''
        svg.extend([f'<line{latest} x1="{x-13:.1f}" y1="{y-13:.1f}" x2="{x+2:.1f}" y2="{y+2:.1f}" stroke="#172c41" stroke-width="3"/>',
                    f'<circle{latest} cx="{x:.1f}" cy="{y:.1f}" r="5.2" fill="{("#00e4ad" if success else "#ff714b")}" stroke="#101d30" stroke-width="1.6"/>'])
    hits=sum(shots); count=len(shots)
    svg.extend([f'<text x="435" y="90" fill="#acc6da" font-family="Arial" font-size="17" font-weight="bold">{html.escape(heading)}</text>',
                f'<text x="435" y="156" fill="#ffffff" font-family="Arial" font-size="58" font-weight="900">{hits} / {count}</text>',
                '<text x="435" y="187" fill="#d6e7f2" font-family="Arial" font-size="15">PERFECT 10s</text>',
                f'<text x="435" y="252" fill="#c2d5e4" font-family="Arial" font-size="14">● Green = perfect 10</text>',
                f'<text x="435" y="281" fill="#c2d5e4" font-family="Arial" font-size="14">● Orange = not 10</text>',
                f'<text x="435" y="316" fill="#8dabc4" font-family="Arial" font-size="12">Visual landing spots are illustrative</text>',
                '</svg>'])
    markup=''.join(svg)
    components.html(f'<div style="max-width:100%;overflow:hidden">{markup}</div>',height=H+3,scrolling=False)


def medal_podium(results):
    if len(results)<3:return
    chunks=[]
    for pos in [1,0,2]:
        r=results[pos];a=r['athlete'];place=pos+1
        medal={1:'🥇',2:'🥈',3:'🥉'}[place]
        chunks.append(f"""<div class='podium-entry'><div class='medal'>{medal}</div><div class='flag'>{html.escape(a['flag'])}</div><div class='team'>{html.escape(a['country'])}</div><div class='archer'>{html.escape(a['athlete'])}</div><div class='score'>{r['score']} / 20</div><div class='podium-block podium-{place}'>{place}</div></div>""")
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
                    if st.button("📋 Continue to Results & Reflection →",type="primary"):
                        st.session_state.student_stage = stages[2]
                        st.rerun()
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


def teacher_mode():
    st.subheader("🏟️ Teacher Championship Control")
    try:
        teacher_pin=st.secrets.get("TEACHER_PIN", "")
    except (FileNotFoundError, Exception):
        teacher_pin=""
    if not teacher_pin:
        st.error("Teacher mode is locked until TEACHER_PIN is set in Streamlit Cloud secrets (or local .streamlit/secrets.toml).")
        st.code('TEACHER_PIN = "your-private-pin"',language='toml')
        return
    if not st.session_state.get("teacher_authenticated",False):
        supplied=st.text_input("Teacher PIN",type="password")
        if st.button("Unlock teacher dashboard"):
            if hmac.compare_digest(str(supplied),str(teacher_pin)):
                st.session_state.teacher_authenticated=True;st.rerun()
            else:st.error("Incorrect PIN")
        return
    if st.button("Lock teacher dashboard"):
        st.session_state.teacher_authenticated=False
        st.rerun()
    st.warning("Version 1 teacher mode runs on THIS screen only. It does not collect student sessions or synchronize results between devices.")
    st.markdown("### Choose the countries competing today")
    country_names={athlete_label(a):a for a in ATHLETES}
    choices=st.multiselect("Participating teams (2–24)",options=list(country_names),default=list(country_names)[:10])
    if len(choices)<2:
        st.info("Select at least two countries.")
        return
    st.caption("Each country will receive 20 simulated arrows. Perfect 10s are the only modeled score. Extra arrows break medal ties.")
    if st.button("🏁 Run a NEW championship",type="primary"):
        seed=secrets.randbits(63)
        results=tournament(seed,[country_names[n] for n in choices])
        st.session_state.championship_results=results
        st.session_state.championship_country_codes=tuple(country_names[n]["code"] for n in choices)
    results=st.session_state.get("championship_results")
    if results:
        selected=tuple(country_names[n]["code"] for n in choices)
        if selected!=st.session_state.get("championship_country_codes"):
            st.info("Selection changed; run a new championship to use the new country list.")
        st.markdown("### 🥇 Medal ceremony")
        if len(results)>=3:
            medal_podium(results)
        medals=['🥇 GOLD','🥈 SILVER','🥉 BRONZE']
        cols=st.columns(min(3,len(results)))
        for i,col in enumerate(cols):
            with col:
                r=results[i];a=r['athlete']
                st.markdown(f"#### {medals[i]}")
                st.markdown(f"### {a['flag']} {a['country']}")
                st.write(a['athlete'])
                st.metric('Perfect 10s',f"{r['score']} / 20")
        st.markdown("### Final leaderboard")
        for rank,r in enumerate(results,1):
            a=r["athlete"]
            tie_note=f" · playoff arrows: {''.join('✓' if x else '×' for x in r['playoffs'])}" if r['playoffs'] else ''
            st.write(f"**{rank}. {a['flag']} {a['country']}** — {a['athlete']} — **{r['score']}/20** perfect 10s{tie_note}")
        st.caption("Classroom medals are based on this simulated event, not actual Paris 2024 medals. Student grades should not depend on winning.")
        st.download_button("Download leaderboard CSV",data=export_results(results),file_name="olympic_archery_classroom_results.csv",mime="text/csv")
    else:
        st.info("Choose participating countries and run the championship when your class is ready.")


def export_results(results):
    import io
    output=io.StringIO()
    writer=csv.writer(output)
    writer.writerow(['place','country','code','athlete','perfect_10s_of_20','playoff_arrows'])
    for n,r in enumerate(results,1):
        a=r['athlete']
        writer.writerow([n,a['country'],a['code'],a['athlete'],r['score'],''.join('1' if x else '0' for x in r['playoffs'])])
    return output.getvalue().encode('utf-8-sig')

mode=st.radio("App mode",["🎓 Student Training","🏆 Teacher Championship"],horizontal=True)
if mode.startswith('🎓'):
    student_mode()
else:
    teacher_mode()

st.divider()
st.caption("Dataset: Paris 2024 men's individual recurve ranking round, as transcribed into the Sports by the Numbers 24-country class cards. Each archer took 72 arrows. All new app shots use independent Bernoulli trials with p = perfect 10s ÷ 72. This simplified model does not estimate actual chances of winning Olympic medals.")
