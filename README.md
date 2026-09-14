# Kerala Power Planner ⚡

A playable Streamlit prototype covering 13 annual rounds from 2011 to 2023.
Adjust generation investments, dispatch, imports and water availability while
balancing construction delays, capital budgets and unserved energy.

**All simulation figures are illustrative. This is not a reconstruction of
Kerala's electricity system or a verified comparison of government performance.**
The comparison strategy makes no new investments; it does not represent UDF or LDF.

## Run locally

Use Python 3.11 or newer. Open a terminal in this project folder:

```bash
python -m venv .venv
```

Activate on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Activate on macOS/Linux:

```bash
source .venv/bin/activate
```

Then install and run:

```bash
python -m pip install -r requirements.txt
python -m streamlit run kerala_power_game.py
```

Open the local URL printed in the terminal. No API keys or data files are needed.
Game progress lasts for the browser session; download results before closing.

## Upload to GitHub

1. Extract the ZIP.
2. Create an empty GitHub repository, for example `kerala-power-planner`.
3. Upload the **contents** of this folder to the repository root, not the ZIP itself.
4. Commit the uploaded files. The app and `requirements.txt` should be at the root.

For Git users, run the following in the extracted project folder, replacing the
placeholder URL with your own empty repository URL:

```bash
git init
git add .
git commit -m "Add Kerala Power Planner prototype"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/kerala-power-planner.git
git push -u origin main
```

Hidden folders such as `.github` and `.streamlit` may be omitted by browser upload.
Git uploads include them. The application can still run without these optional folders.

## Streamlit Community Cloud

Create an app linked to this repository. Choose branch `main` and entrypoint
`kerala_power_game.py`, with Python 3.11 or newer. Dependencies are in
`requirements.txt`. GitHub Pages cannot run this Python server application.

## Verification

```bash
python kerala_power_game.py --self-test
python -m py_compile kerala_power_game.py
```

The built-in checks cover budget enforcement, construction delay, state isolation,
energy balance and the full campaign. GitHub Actions also runs a Streamlit initial
render smoke check. Full browser appearance and interactive play still need manual review.

## Model and evidence

Annual generation uses MW × 8,760 × capacity factor / 1,000 to obtain GWh.
Hydro output is adjusted by synthetic water availability. Purchases meet some of
the internal generation gap; unserved energy is what remains after purchases.
Contract prices, demand, fleet sizes, weather, construction costs and budgets are
teaching assumptions. Capital and operating costs are reported separately.

Hourly adequacy, transmission, storage, financing, land constraints and project
uncertainty are not modelled. The synthetic weather is not climate attribution.

The evidence panel links Kerala Solar Energy Policy 2013. Policy targets must not
be confused with commissioned capacity. A future historical mode needs sourced
annual data, project approval/construction/commissioning dates and the regulatory
history of the disputed power-purchase agreements.

## Project files

- `kerala_power_game.py`: game and built-in simulation checks.
- `requirements.txt`: Python dependencies.
- `.streamlit/config.toml`: dark theme.
- `.github/workflows/check.yml`: automated checks on pushes and pull requests.
- `.gitignore`: excludes local environments, caches and secrets.
