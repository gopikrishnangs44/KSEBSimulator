"""Run: python -m pip install streamlit
Then: python -m streamlit run kerala_grid_challenge.py
Fictional advocacy game. All numbers and thresholds are scenario assumptions.
"""
import streamlit as st

st.set_page_config(page_title="Keep Kerala Lit", page_icon="⚡", layout="wide")
st.markdown('''<style>
.stApp {background:radial-gradient(ellipse at top,#183849,#08111e);color:#f1f7ff;}
h1,h2,h3 {color:#f1f7ff!important;}
.block-container {max-width:1150px;padding-top:2rem;}
.hero {font-size:48px;font-weight:900;letter-spacing:-2px;}
.eyebrow {color:#65e0c4;letter-spacing:4px;font-size:12px;font-weight:800;}
.panel {background:#15263c;border:1px solid #335069;border-radius:20px;padding:24px;margin:12px 0;}
.city {font-size:48px;letter-spacing:10px;text-align:center;padding:24px;border-radius:20px;background:#15263c;}
.notice {border-left:5px solid #ffcb6b;background:#302c28;padding:18px;border-radius:12px;}
.loss {background:#401d2a;border:2px solid #ff647c;border-radius:22px;padding:28px;}
.win {background:#123b34;border:2px solid #65e0c4;border-radius:22px;padding:28px;}
[data-testid="stMetric"] {background:#15263c;padding:18px;border-radius:16px;}
.stButton button {border-radius:12px;min-height:48px;font-weight:700;}
</style>''', unsafe_allow_html=True)

if 'round_id' not in st.session_state:
    st.session_state.round_id = 0
if 'result' not in st.session_state:
    st.session_state.result = None

st.markdown('<div class="eyebrow">A FICTIONAL ENERGY POLICY CHALLENGE</div><div class="hero">⚡ KEEP KERALA LIT</div>', unsafe_allow_html=True)
st.write('Power the city. Protect the family budget. Can you close the gap?')
st.caption('Scenario rules, not historical Kerala data. The no-investment premise is fictional; '
           'the game does not establish what an actual government did.')

with st.sidebar:
    st.header('🎮 How to play')
    st.write('1. Add internal generation capacity.\n\n2. Buy enough external power to meet demand.\n\n3. Submit your plan.')
    st.write('Lose if the purchase price exceeds ₹12/unit, the model family bill exceeds '
             '₹5,000/month, or demand remains unmet. Otherwise you win.')
    st.caption('The two price limits are game rules chosen for this scenario, not official affordability standards.')
    if st.button('↻ Start again'):
        st.session_state.round_id += 1
        st.session_state.result = None
        st.rerun()

locked = st.session_state.result is not None
round_id = st.session_state.round_id
left, right = st.columns([1.25, 1])
with left:
    st.subheader('🕹️ Grid control room')
    st.caption('Planning sandbox: additions represent completed investments after a planning period, not instant construction.')
    added = st.slider('Build internal capacity (MW)', 0, 2500, 0, 100,
                      key=f'add_{round_id}', disabled=locked)
    bought = st.slider('Buy external power (average MW)', 0, 2500, 500, 100,
                       key=f'buy_{round_id}', disabled=locked)
    rain = st.select_slider('Water availability', options=['Dry', 'Normal', 'Wet'],
                            value='Normal', key=f'rain_{round_id}', disabled=locked)
    if added > 0:
        st.markdown('<div class="notice"><b>📣 Your challenge to the government</b><br>'
                    '“Why did my government do nothing to build this capacity?”<br><br>'
                    '<small>Fictional scenario: the previous administration added zero capacity. '
                    'This line is a player viewpoint, not a verified claim about Kerala.</small></div>',
                    unsafe_allow_html=True)
    st.caption('Increasing purchases pushes the assumed purchase price upward. Internal investments '
               'also have a cost; their simplified capital recovery is included in the bill.')

# Deliberately simple game rules, not an empirical tariff or dispatch model.
demand = 2200.0
hydro = 800 * {'Dry': 0.65, 'Normal': 1.0, 'Wet': 1.15}[rain]
internal = hydro + added * 0.60
supply = internal + bought
shortfall = max(0.0, demand - supply)
purchase_price = 4.5 + bought * 0.004
internal_unit_cost = 3.0 + added * 0.001
blended_cost = (internal * internal_unit_cost + bought * purchase_price) / max(supply, 1)
retail = blended_cost + 2.0
usage = 500
bill = usage * retail + 150
coverage = min(1.0, supply / demand)

with right:
    st.markdown('<div class="city">🏘️ 🏥 🏫 🏭</div>', unsafe_allow_html=True)
    st.progress(coverage)
    st.caption(f'City demand covered: {coverage:.0%} · Demand: {demand:,.0f} average MW')
    a, b = st.columns(2)
    a.metric('Internal output', f'{internal:,.0f} MW')
    b.metric('Supply shortfall', f'{shortfall:,.0f} MW')
    a.metric('Purchase price', f'₹{purchase_price:.2f}/unit' if bought else 'No purchases')
    b.metric('Model retail rate', f'₹{retail:.2f}/unit')
    st.markdown(f'<div class="panel"><b>🏠 THE FAMILY BUDGET</b><h2>₹{bill:,.0f} / month</h2>'
                f'Example consumption: {usage} units/month<br>Game affordability limit: ₹5,000<br>'
                '<small>Illustrative household bill, not an actual KSEB tariff calculation.</small></div>',
                unsafe_allow_html=True)

if st.button('⚡ SUBMIT YOUR POWER PLAN', type='primary', disabled=locked):
    reasons = []
    if bought > 0 and purchase_price > 12:
        reasons.append('Purchased electricity costs more than ₹12/unit: the game price ceiling is breached.')
    if bill > 5000:
        reasons.append('People are suffering high electricity charges in this scenario. '
                       'A bill above ₹5,000/month is unaffordable for the example middle-class family under this game’s rule.')
    if shortfall > 0:
        reasons.append(f'The city still lacks {shortfall:,.0f} average MW. Essential demand remains unmet.')
    st.session_state.result = reasons if reasons else ['WIN']
    st.rerun()

result = st.session_state.result
if result is not None:
    if result == ['WIN']:
        st.markdown('<div class="win"><h2>🏆 YOU KEPT THE LIGHTS ON</h2>'
                    'Demand is met and both price limits are respected. Your simulated plan passes.</div>',
                    unsafe_allow_html=True)
    else:
        st.markdown('<div class="loss"><h2>💥 GAME OVER</h2>' +
                    ''.join(f'<p>{reason}</p>' for reason in result) + '</div>', unsafe_allow_html=True)
    st.info('Use “Start again” in the sidebar to try another plan.')

with st.expander('Show the rules behind the game'):
    st.write('Demand: 2,200 average MW. Existing hydro output: 800 MW in normal conditions. '
             'New capacity delivers 60% average output. Purchase price = ₹4.50 + ₹0.004 × purchased MW. '
             'Internal cost = ₹3 + ₹0.001 × added MW, including simplified capital recovery. '
             'Retail rate = output-weighted supply cost + ₹2/unit. Example bill = 500 × retail rate + ₹150. '
             'The wholesale purchase price and household retail tariff are different quantities.')
    st.write('All assumptions are invented for gameplay. No historical weather, generation, procurement '
             'or tariff dataset is loaded. There is no hourly reliability model. The year-by-year campaign '
             'has been replaced with a single-plan challenge. A historical accountability version would '
             'require sourced project and generation records before attributing failures to a real administration.')
