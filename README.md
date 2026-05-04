# qa-lab-appium

Mobile UI test automation framework using **Appium 2** with **BDD (Behave + Gherkin)** and the **Page Object Model**. Designed to be small, readable, and ready to scale to multiple apps and platforms (Android first, iOS extensible).

---

## Why this project

Most Appium starter projects either dump everything into `tests/` or lean entirely on raw selectors. This one separates concerns clearly:

- **Gherkin features** describe behavior in business language.
- **Step definitions** glue Gherkin to page actions — no Appium calls live here.
- **Page Objects** own locators and screen-level actions — no assertions here.
- **Core layer** owns Appium driver lifecycle and configuration — hidden from steps and pages.

The result: when the UI changes, you update one file (the page); when the test scenario changes, you update one file (the feature). Locators never appear in steps, and Appium options never appear in features.

---

## Project layout

```
qa-lab-appium/
├── core/                      # Cross-cutting infrastructure
│   ├── config.py              # AppConfig (env-driven), PlatformName enum
│   ├── driver_factory.py      # create_driver(): Android / iOS branches
│   └── reachability.py        # Fast TCP check before opening Appium sessions
├── features/                  # Behave (BDD)
│   ├── environment.py         # before_scenario / after_scenario hooks
│   ├── login.feature          # Example Gherkin scenario
│   └── steps/                 # Step definitions (Behave default location)
│       └── login_steps.py
├── pages/                     # Page Object Model
│   ├── base_page.py           # Driver wrapper; common helpers go here
│   ├── factory.py             # get_login_page() — returns Android or iOS page
│   ├── android/
│   │   └── login_page.py      # UiAutomator2 selectors + actions
│   └── ios/
│       └── login_page.py      # XCUITest selectors + actions (parallel API)
├── tests/                     # Pytest smoke tests (share core/driver_factory)
│   ├── conftest.py
│   └── test_smoke.py
├── reports/                   # Behave JUnit XML output (gitignored)
├── scripts/
│   └── run_appium.sh          # Starts Appium 2 with ANDROID_HOME exported
├── behave.ini                 # Behave runner defaults (paths, JUnit, logging)
└── requirements.txt
```

### Architecture in one sentence
**Feature → Step → Page → Driver factory → Appium**, with `core/config.py` as the single source of truth for every layer below the steps.

---

## Prerequisites

- **macOS / Linux** (the helper script targets macOS paths; tweak `scripts/run_appium.sh` for Linux)
- **Python 3.9+** (3.13 tested)
- **Node.js 18+** and **Appium 2** (`npm install -g appium && appium driver install uiautomator2`)
- **Android SDK + emulator** (or a real device), with `adb` on `PATH`
- For iOS: **Xcode + Simulator** and `appium driver install xcuitest`

---

## Setup

```bash
git clone https://github.com/arctouch-brunalavelli/qa-lab-appium.git
cd qa-lab-appium

python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

---

## How to run

You always need **three things** running before the tests:

1. An **Android emulator** (or a real device) — verify with `adb devices`.
2. The **App under test** installed on that device.
3. The **Appium server** — start with the helper script (it exports `ANDROID_HOME`):

```bash
./scripts/run_appium.sh
# Listening on http://0.0.0.0:4723 — leave it open
```

### Run the BDD scenarios (Behave)

```bash
behave                          # all features
behave -t @login                # only @login-tagged scenarios
behave features/login.feature   # one specific feature file
behave --no-capture -v          # verbose, show prints
behave --dry-run                # validate step matching without launching Appium
```

JUnit XML is automatically written to `reports/` (configured in `behave.ini`).

### Run the smoke tests (Pytest)

```bash
pytest tests/ -v
```

Pytest reuses the same `core/driver_factory` as Behave, so there is **one** Appium configuration path for the whole repo.

---

## Configuration (env vars)

Everything is overridable from the shell — no code edits required for normal use. Defaults are aimed at the arctouch demo app on Android.

| Variable | Default | Used for |
|----------|---------|----------|
| `MOBILE_PLATFORM` | `android` | `android` or `ios` — picks the driver/page implementation. |
| `APPIUM_SERVER_URL` | `http://127.0.0.1:4723` | Appium 2 endpoint. |
| `ANDROID_APP_PACKAGE` | `com.arctouch.arctouch_demo_app` | Application id of the APK under test. |
| `ANDROID_APP_ACTIVITY` | `com.arctouch.arctouch_demo_app.MainActivity` | Launcher activity. |
| `MOBILE_IOS_BUNDLE_ID` | `com.example.app` | iOS bundle id (set when targeting iOS). |
| `APPIUM_NO_RESET` | `true` | If `true`, app state is preserved between sessions. |
| `ANDROID_LOCATOR_USERNAME` | *(see `pages/android/login_page.py`)* | Override the login email field locator. |
| `ANDROID_LOCATOR_PASSWORD` | *(see `pages/android/login_page.py`)* | Override the login password field locator. |
| `ANDROID_LOCATOR_LOGIN_BTN` | *(see `pages/android/login_page.py`)* | Override the Sign In button locator. |
| `IOS_LOCATOR_*` | — | Same idea, iOS side. |

Locator override syntax (read by `_by_from_env`):
- `id=resource.id.value` *(or no prefix)* → resource-id
- `acc=accessibilityId` → accessibility id
- `ui=new UiSelector()...` → Android UiAutomator selector
- `xpath=...` *(or starts with `//`)* → XPath

Example:

```bash
export MOBILE_PLATFORM=android
export ANDROID_APP_PACKAGE=com.yourcompany.yourapp
export ANDROID_APP_ACTIVITY=com.yourcompany.yourapp.MainActivity
export ANDROID_LOCATOR_LOGIN_BTN="acc=Sign In"
behave -t @login
```

---

## Writing a new test

1. **Add a `.feature`** under `features/` describing the behavior in Gherkin.
2. **Add step definitions** under `features/steps/` — keep them thin, just call page objects.
3. **Add a Page Object** under `pages/<platform>/` exposing user-level actions (`enter_username`, `tap_login`, …). No assertions inside.
4. (If multi-platform) **Register it in `pages/factory.py`** so steps stay platform-agnostic.

Conventions:
- One Page Object per screen, per platform.
- Locators live **only** in the page; never in steps or features.
- Assertions live **only** in steps.

---

## Driver lifecycle

`features/environment.py` owns the driver, **one Appium session per scenario**:

- `before_scenario`: builds `AppConfig`, checks Appium reachability (skips the scenario with a clear message if the server is down), creates the driver.
- `after_scenario`: always calls `driver.quit()` — even on failures — so devices don’t end up with orphaned sessions.

Pytest mirrors this in `tests/conftest.py` for the smoke fixtures.

---

## Test reporting

Out of the box: **JUnit XML** → `reports/` (configured in `behave.ini`). Pluggable options:

- **JUnit / CI dashboards** — already enabled; works with Jenkins / GitHub Actions / Azure Pipelines.
- **Allure**: `pip install allure-behave`, then run `behave -f allure_behave.formatter:AllureFormatter -o allure-results` and `allure serve allure-results`.
- **HTML pretty**: `pip install behave-html-pretty-formatter` and use `-f behave_html_pretty_formatter:PrettyHTMLFormatter -o reports/report.html`.
- **TestRail / Xray / Zephyr**: write a custom hook in `environment.py` (or a CI step) that posts results via the tool’s API after each run.

---

## Continuous Integration (pointer)

A minimal GitHub Actions workflow could:

1. Set up Python and Node.js, install Appium + UiAutomator2.
2. Boot an Android emulator (e.g. `reactivecircus/android-emulator-runner`).
3. Install the APK with `adb install`.
4. Start Appium in the background (`./scripts/run_appium.sh &`).
5. Run `behave -f junit -o reports/`.
6. Upload `reports/*.xml` (and Allure results, if used) as artifacts.

This repo doesn’t ship a workflow yet — drop one under `.github/workflows/` when you’re ready to wire CI.

---

## Troubleshooting cheatsheet

| Symptom | Likely cause | Quick fix |
|---|---|---|
| Behave reports `1 skipped` and exits 0 | Appium not reachable; `before_scenario` skipped on purpose | Start `./scripts/run_appium.sh`; verify `curl http://127.0.0.1:4723/status` |
| `EADDRINUSE :4723` when starting Appium | Another Appium already running | `lsof -nP -iTCP:4723 -sTCP:LISTEN`, then `kill <pid>` |
| `zsh: command not found: adb` | Android SDK paths not on `PATH` | Add `$ANDROID_HOME/platform-tools` to `PATH` in `~/.zshrc` |
| `NoSuchElementError: ... login_username` | Locators don’t match the live UI | Use **Appium Inspector**, copy the real selector, update the page object or set `ANDROID_LOCATOR_*` |
| Login scenario times out | Wrong app, wrong activity, or app not installed | Confirm `adb shell pm list packages | grep <pkg>` and `dumpsys window | grep mFocusedApp` |
| `npm install -g appium` → `EACCES` | Trying to write to Homebrew-owned global node_modules | Use **nvm** (user-owned Node) and reinstall Appium |
| `gh: command not found` | `~/.local/bin` not on `PATH` | Add `export PATH="$HOME/.local/bin:$PATH"` to `~/.zshrc` |

---

## License

Add a license (e.g. MIT) before sharing publicly outside ArcTouch.
