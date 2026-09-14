"""Kerala Power Planner — illustrative, single-file Streamlit prototype.

Install: python -m pip install streamlit
Run:     python -m streamlit run kerala_power_game.py
Test:    python kerala_power_game.py --self-test

All simulation numbers are fictional teaching assumptions, not Kerala statistics.
No external files, API keys, or network access are required by the application.
"""

import copy
import csv
import io
import sys

START, END = 2011, 2023
# name: (crore/MW, construction years, annual capacity factor, operating Rs/kWh)
TECH = {"Solar": (5, 1, 0.19, 0.5), "Wind": (7, 2, 0.25, 0.7),
        "Hydro": (12, 4, 0.38, 1.0)}
# Synthetic weather sequence, NOT observed rainfall or climate attribution.
RAIN = [1.0, 0.85, 1.1, 0.95, 0.9, 0.8, 1.0, 1.1, 1.05, 0.95, 1.0, 0.85, 0.60]


def new_game():
    return {"year": START, "budget": 6000.0,
            "capacity": {"Solar": 100, "Wind": 100, "Hydro": 2000},
            "pipeline": [], "history": [], "capex": 0.0}


def simulate(game, builds, imports, dispatch, rain):
    """Return a new state; capital budgets and yearly energy accounts are separate."""
    cost = sum(builds[k] * TECH[k][0] for k in TECH)
    if any(v < 0 for v in builds.values()) or cost > game["budget"]:
        raise ValueError("Your construction plan exceeds the available capital budget.")
    if not 0 <= imports <= 2000 or not 0 <= dispatch <= 100 or not 0.4 <= rain <= 1.2:
        raise ValueError("Scenario controls are outside their allowed ranges.")
    g = copy.deepcopy(game)
    year = g["year"]
    if year > END:
        raise ValueError("The campaign is complete. Start a new game.")
    g["budget"] -= cost
    g["capex"] += cost
    for name, mw in builds.items():
        if mw:
            g["pipeline"].append({"Technology": name, "MW": mw,
                                  "Online year": year + TECH[name][1]})
    pending = []
    for project in g["pipeline"]:
        if project["Online year"] <= year:
            g["capacity"][project["Technology"]] += project["MW"]
        else:
            pending.append(project)
    g["pipeline"] = pending
    demand = 18000 * 1.045 ** (year - START)  # GWh/year, fictional
    generated = {}
    for name, capacity in g["capacity"].items():
        weather = rain if name == "Hydro" else 1.0
        generated[name] = capacity * 8.76 * TECH[name][2] * weather * dispatch / 100
    internal = sum(generated.values())
    need = max(0, demand - internal)
    # Existing external supply is fixed in the toy model. Extra imports are
    # annual firm-capacity purchases, not a reconstruction of the disputed PPA.
    contracted = (900 + imports) * 8.76 * 0.85
    used_contract = min(need, contracted)
    remaining = max(0, need - used_contract)
    spot = min(remaining, 4500)
    unserved = max(0, remaining - spot)
    spot_price = 9.0 if rain < 0.8 else 6.0
    # 1 GWh at Rs 1/kWh = Rs 0.1 crore. Contract costs use take-or-pay.
    operating = sum(generated[k] * TECH[k][3] * 0.1 for k in TECH)
    operating += contracted * 4.5 * 0.1 + spot * spot_price * 0.1
    row = {"Year": year, "Demand GWh": round(demand, 1),
           "Internal GWh": round(internal, 1), "Contract imports GWh": round(used_contract, 1),
           "Spot imports GWh": round(spot, 1), "Unserved GWh": round(unserved, 1),
           "Unused contract GWh": round(contracted - used_contract, 1),
           "Surplus internal GWh": round(max(0, internal - demand), 1),
           "Operating cost crore": round(operating, 1), "Capital cost crore": cost,
           "Demand served %": round(100 * (1 - unserved / demand), 2),
           "Hydro weather multiplier": rain}
    g["history"].append(row)
    g["year"] += 1
    g["budget"] += 3000 if g["year"] <= END else 0
    return g


def self_test():
    zero = dict.fromkeys(TECH, 0)
    g = new_game()
    first = simulate(g, {**zero, "Solar": 100}, 0, 100, 1.0)
    assert g["year"] == START and first["capacity"]["Solar"] == 100
    second = simulate(first, zero, 0, 100, 1.0)
    assert second["capacity"]["Solar"] == 200
    try:
        simulate(g, {**zero, "Hydro": 1000}, 0, 100, 1.0)
        raise AssertionError("Budget validation failed")
    except ValueError:
        pass
    for year in range(START, END + 1):
        g = simulate(g, zero, 0, 100, RAIN[year - START])
        r = g["history"][-1]
        assert abs(r["Internal GWh"] + r["Contract imports GWh"] +
                   r["Spot imports GWh"] + r["Unserved GWh"] - r["Demand GWh"]) < 0.3
        assert 0 <= r["Demand served %"] <= 100
    assert len(g["history"]) == 13 and g["year"] == 2024
    print("Passed: budget, immutability, construction delay, energy balance, full campaign.")


def main():
    try:
        import streamlit as st
    except ImportError:
        print("Install Streamlit: python -m pip install streamlit")
        print("Then run: python -m streamlit run kerala_power_game.py")
        return
    st.set_page_config(page_title="Kerala Power Planner", page_icon="⚡", layout="wide")
    st.markdown("""<style>
    .stApp {background: #0d1726; color: #edf5ff;}
    h1,h2,h3 {color: #63e4c5 !important;}
    [data-testid="stMetric"] {background:#18293d;padding:18px;border-radius:14px;}
    .stButton button {border:1px solid #63e4c5;border-radius:12px;}
    </style>""", unsafe_allow_html=True)
    if "power_game" not in st.session_state:
        st.session_state.power_game = new_game()
        st.session_state.baseline = new_game()
    g = st.session_state.power_game
    st.title("⚡ Kerala Power Planner")
    st.caption("2011 → 2023 • Build capacity. Plan ahead. Keep the lights on.")
    st.warning("DEMO MODEL: all game numbers, weather events and budgets are illustrative. "
               "The comparison is against a fictional no-new-investment strategy, NOT any government's record.")
    with st.sidebar:
        st.header("🎮 Mission control")
        st.write("Play 13 annual rounds. New projects take time; unused capital rolls forward.")
        st.write("Annual capital grant: ₹3,000 crore after each round. Operating costs are "
                 "tracked separately and are not deducted from this construction budget.")
        if st.button("↻ Restart campaign"):
            st.session_state.power_game = new_game()
            st.session_state.baseline = new_game()
            st.rerun()
        st.caption("Keep this browser session open to retain your game. Download results before closing.")
    done = g["year"] > END
    st.progress(len(g["history"]) / 13)
    a, b, c = st.columns(3)
    a.metric("Campaign year", "Complete" if done else str(g["year"]))
    b.metric("Available capital", f"₹{g['budget']:,.0f} crore")
    c.metric("Commissioned capacity", f"{sum(g['capacity'].values()):,} MW")
    st.caption("Capacity above is before this round's scheduled project completions.")
    if not done:
        year = g["year"]
        st.subheader(f"🕹️ Your decisions · {year}")
        st.write("Increase or decrease this year's planned builds and generation dispatch. "
                 "Dispatch changes output, not installed capacity; projects cannot be built instantly.")
        with st.form(f"round_{year}"):
            cols = st.columns(3)
            builds = {}
            for col, (name, (cost, delay, cf, _)) in zip(cols, TECH.items()):
                with col:
                    builds[name] = st.slider(f"{name}: new MW", 0, 500, 0, 50)
                    st.caption(f"₹{cost} crore/MW · {delay}-year build · {cf:.0%} capacity factor")
            imports = st.slider("Extra contracted imports for this year (MW)", 0, 2000, 300, 100)
            dispatch = st.slider("Use available internal generation (%)", 0, 100, 100, 5)
            rain = st.slider("Hydro water-availability multiplier (synthetic)", 0.4, 1.2,
                             RAIN[year - START], 0.05)
            st.caption("Contract assumption: ₹4.50/unit, 85% annual availability, take-or-pay. "
                       "Spot market limited to 4,500 GWh/year; price ₹6 or ₹9/unit in dry scenarios.")
            submit = st.form_submit_button("⚡ Commit decisions & run year")
        if submit:
            try:
                next_g = simulate(g, builds, imports, dispatch, rain)
                baseline = simulate(st.session_state.baseline, dict.fromkeys(TECH, 0), 0, 100, rain)
                st.session_state.power_game = next_g
                st.session_state.baseline = baseline
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))
    else:
        st.success("🏁 Campaign complete! Review your outcomes and export the run below.")
    if g["history"]:
        row = g["history"][-1]
        st.subheader(f"💡 Grid report · {row['Year']}")
        cols = st.columns(4)
        cols[0].metric("Demand served", f"{row['Demand served %']:.1f}%")
        cols[1].metric("Internal generation", f"{row['Internal GWh']:,.0f} GWh")
        cols[2].metric("Unserved energy", f"{row['Unserved GWh']:,.0f} GWh")
        cols[3].metric("Operating cost", f"₹{row['Operating cost crore']:,.0f} cr")
        st.info("An internal generation gap is not automatically a power shortage: imports "
                "can meet it. Unserved energy is the remaining gap after available purchases.")
        base = st.session_state.baseline["history"]
        avoided = sum(r["Unserved GWh"] for r in base) - sum(r["Unserved GWh"] for r in g["history"])
        st.write(f"**Compared with no new investment:** {avoided:,.0f} GWh less cumulative "
                 "unserved energy (negative means more). Both runs face the same weather and demand.")
        st.caption("The baseline adds no generation or extra contracts. This is a counterfactual "
                   "game benchmark, not historical UDF/LDF data. Compare costs as well as shortages.")
        st.dataframe(g["history"], hide_index=True)
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=list(g["history"][0]))
        writer.writeheader()
        writer.writerows(g["history"])
        st.download_button("Download simulation results (.csv)", output.getvalue(),
                           "illustrative_power_game_results.csv", "text/csv")
    with st.expander("🏗️ Commissioned fleet & construction queue"):
        st.write(g["capacity"])
        if g["pipeline"]:
            st.dataframe(g["pipeline"], hide_index=True)
        else:
            st.write("No projects under construction.")
        st.caption("Projects completing after 2023 remain in the queue and provide no campaign benefit.")
    with st.expander("📚 Evidence, assumptions & next version"):
        st.markdown("""
        **Historical anchor:** Kerala Solar Energy Policy 2013 proposed 500 MW by 2017
        and 2,500 MW by 2030. Targets are not proof of delivered capacity.
        [Read the policy](https://www.anert.gov.in/sites/default/files/inline-files/go_20131125_pd-49-p_solarenergypolicy2013.pdf).

        **Model assumptions:** Initial demand 18,000 GWh; annual growth 4.5%; hydro
        2,000 MW, solar 100 MW, wind 100 MW; existing external contracts 900 MW.
        These are teaching inputs, not a historical reconstruction. Annual generation
        is MW × 8,760 hours × capacity factor ÷ 1,000, adjusted by dispatch and hydro water availability.

        **Limits:** No hourly peak-demand modelling, storage, transmission losses,
        land constraints, financing, plant retirement, or construction uncertainty.
        Weather is synthetic and does not establish climate-change causation.
        Imports do not increase internal generation. Costs are stylised, not historical tariffs.

        **Government accountability mode is not yet implemented.** It requires verified
        annual demand, generation, purchases and project milestones. Record approval,
        construction and commissioning separately across administrations. The disputed
        PPA needs a sourced regulatory timeline, not an unrestricted cancellation switch.
        This prototype cannot establish that a government did nothing or quantify its inefficiency.
        """)


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test()
    else:
        main()
