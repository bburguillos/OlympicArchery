import csv
import hmac
import random
import secrets
from pathlib import Path

import streamlit as st

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
.block-container{padding-top:1.5rem;max-width:1150px}
.huge{font-size:2.3rem;font-weight:900;letter-spacing:.02em}
.smallnote{opacity:.78;font-size:.88rem}
.hero{border-radius:18px;padding:20px 25px;background:linear-gradient(110deg,#25344b,#1c2c40 65%,#59402c);margin-bottom:14px;border:1px solid #3d4d62}
.result-chip{border-radius:12px;padding:10px;text-align:center;border:1px solid #6f7c8c;background:#25354c;font-size:1.5rem}
</style>
""", unsafe_allow_html=True)
st.markdown('<div class="hero"><div class="huge">🏹 OLYMPIC ARCHERY · ROAD TO GOLD</div><div>Sports by the Numbers · Paris 2024 athlete data · Classroom probability simulator</div></div>', unsafe_allow_html=True)
st.caption("Real Olympic data powers the probabilities; all training and championship shots are NEW computer simulations, not historical Olympic results.")


def calc_ok(answer, expected):
    return answer is not None and abs(float(answer)-expected) <= 0.51


def simulate(a, count, rng):
    # Uses the unrounded historical success probability, NEVER a student's entered percentage.
    return [rng.random() < a["p"] for _ in range(count)]


def target(success, key=""):
    # Decorative target depicts perfect-10 vs not-10 only. Does not invent exact ring scores.
    if success is None:
        st.markdown("<div style='text-align:center;font-size:5rem'>🎯</div>", unsafe_allow_html=True)
    elif success:
        st.success("🎯 PERFECT 10! The simulated arrow hit the center.")
    else:
        st.info("🏹 Not a perfect 10 this time. Exact ring points are not modeled.")


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
    st.write(f'**Athlete:** {a["athlete"]}  ·  **Country:** {a["flag"]} {a["country"]}  ·  **Competition:** Paris 2024 men’s individual recurve ranking round')
    t1,t2,t3 = st.tabs(["🔐 Probability Check", "🏹 Training Camp", "📋 Results & Reflection"])
    with t1:
        unlocked = check_panel(a, "my")
        st.markdown("**Further worksheet questions:** Calculate P(not a 10), then predict how many perfect 10s you expect in 20 arrows.")
        st.caption("We never change the athlete's underlying real-data probability when a student enters an answer.")
    with t2:
        if not unlocked:
            st.info("Complete the Probability Check tab first.")
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
                st.metric("Training score", f"{sum(shots)} perfect 10s / {len(shots)} arrows")
                st.progress(len(shots)/10)
                if shots:
                    target(shots[-1]); st.write(' '.join('🎯' if v else '➖' for v in shots))
                else:
                    target(None)
                if len(shots)<10:
                    if st.button("Release next arrow 🏹",type="primary"):
                        shot=simulate(a,1,secrets.SystemRandom())[0]
                        st.session_state.training_shots = shots + [shot]
                        st.rerun()
                else:
                    st.success(f'Training complete: you predicted {st.session_state.training_prediction} perfect 10s and got {sum(shots)}.')
                    st.caption("Different results from your prediction are normal in a random simulation.")
                    if st.button("Run another 10-arrow session"):
                        st.session_state.training_started=False
                        st.session_state.training_shots=[]
                        st.session_state.training_prediction=None
                        st.rerun()
    with t3:
        shots=st.session_state.get("training_shots",[])
        if not shots:
            st.info("Complete training to see your results here.")
        else:
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

