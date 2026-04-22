import streamlit as st
from playwright.sync_api import sync_playwright
from concurrent.futures import ThreadPoolExecutor
import os, shutil, re, time, zipfile

st.set_page_config(
    page_title="Browser Matrix | Happy Horizon",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Brand CSS (from brand-guide.md) ──────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

:root {
    --navy:    #0f1a2e;
    --yellow:  #FFE600;
    --yellow-h:#f0d800;
    --lime:    #c8f04c;
    --white:   #ffffff;
    --text:    #1a1a1a;
    --muted:   #666666;
    --subtle:  #999999;
    --border:  #e8e8e0;
    --surface: #f9f9f7;
}

*, *::before, *::after {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    box-sizing: border-box;
}

#MainMenu, footer, .stDeployButton, [data-testid="stToolbar"] { visibility: hidden; }
.main .block-container { padding-top: 1.5rem; max-width: 1440px; }

/* ── Sidebar ── */
[data-testid="stSidebar"] { background: var(--navy) !important; }

/* All sidebar text → readable on dark */
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div { color: rgba(255,255,255,0.82) !important; }

/* URL input: white bg + dark text = always readable */
[data-testid="stSidebar"] .stTextInput input {
    background: #ffffff !important;
    border: none !important;
    border-radius: 7px !important;
    color: var(--navy) !important;
    caret-color: var(--navy) !important;
    font-size: 0.9rem !important;
    font-weight: 500 !important;
    padding: 0.55rem 0.75rem !important;
}
[data-testid="stSidebar"] .stTextInput input::placeholder {
    color: #aaa !important;
}
[data-testid="stSidebar"] .stTextInput input:focus {
    outline: 2px solid var(--yellow) !important;
    outline-offset: 0px !important;
}

/* Section labels: yellow uppercase */
[data-testid="stSidebar"] .sidebar-label {
    color: var(--yellow) !important;
    font-size: 0.67rem !important;
    font-weight: 700 !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    display: block;
    margin: 1.25rem 0 0.4rem;
}
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.08) !important; }

/* Checkbox tick on dark */
[data-testid="stSidebar"] .stCheckbox > label > div:first-child {
    border-color: rgba(255,255,255,0.35) !important;
}

/* Slider track */
[data-testid="stSidebar"] .stSlider [data-baseweb="slider"] [role="progressbar"] {
    background: var(--lime) !important;
}

/* ── Primary button — yellow bg, black text ── */
div.stButton > button[kind="primary"],
[data-testid="stSidebar"] div.stButton > button[kind="primary"] {
    background: var(--yellow) !important;
    color: #000000 !important;
    border: none !important;
    border-radius: 9999px !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    padding: 0.65rem 1.5rem !important;
    letter-spacing: -0.01em !important;
}
div.stButton > button[kind="primary"] >div{
    color:#000000 !important;            
}            
div.stButton > button[kind="primary"]:hover,
[data-testid="stSidebar"] div.stButton > button[kind="primary"]:hover {
    background: var(--yellow-h) !important;
    color: #000000 !important;
}

/* ── Secondary / back button ── */
div.stButton > button[kind="secondary"] {
    background: transparent !important;
    border: 1.5px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 9999px !important;
    font-weight: 600 !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] { border-bottom: 2px solid var(--border); gap: 0; }
.stTabs [data-baseweb="tab"] {
    border-radius: 8px 8px 0 0 !important;
    padding: 0.55rem 1.25rem !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
    color: var(--muted) !important;
    border: none !important;
    outline: none !important;
}
.stTabs [aria-selected="true"] {
    background: var(--navy) !important;
    color: var(--yellow) !important;
}

/* ── Page header ── */
.hh-page-header {
    padding: 0.25rem 0 1.75rem;
    border-bottom: 2px solid var(--border);
    margin-bottom: 2rem;
}
.hh-page-header h1 {
    font-size: 2rem; font-weight: 800; color: var(--navy);
    margin: 0; line-height: 1.2; letter-spacing: -0.04em;
}
.hh-page-header p { color: var(--muted); font-size: 0.95rem; margin: 0.4rem 0 0; }
.hh-badge {
    background: var(--yellow); color: var(--navy);
    font-size: 0.62rem; font-weight: 800;
    padding: 2px 9px; border-radius: 999px;
    text-transform: uppercase; letter-spacing: 0.08em;
    vertical-align: middle; margin-left: 10px; display: inline-block;
}

/* ── Device cards ── */
.device-card {
    background: var(--white);
    border: 1px solid var(--border);
    border-radius: 12px;
    overflow: hidden;
    margin-bottom: 1.25rem;
    transition: box-shadow 0.2s, transform 0.15s;
}
.device-card:hover {
    box-shadow: 0 6px 24px rgba(15,26,46,0.1);
    transform: translateY(-2px);
}
.card-header {
    padding: 0.7rem 1rem;
    border-bottom: 1px solid var(--surface);
    display: flex; align-items: center; justify-content: space-between;
}
.card-device { font-weight: 700; font-size: 0.85rem; color: var(--navy); }
.card-vp     { font-size: 0.72rem; color: var(--subtle); margin-top: 2px; }
.eng-badge   { font-size: 0.68rem; font-weight: 700; padding: 3px 10px; border-radius: 999px; white-space: nowrap; }
.eng-chromium { background: #EFF6FF; color: #2563EB; }
.eng-firefox  { background: #FFF7ED; color: #EA580C; }
.eng-webkit   { background: #F5F3FF; color: #7C3AED; }

/* ── Lightbox ── */
.lb-wrap {
    background: var(--navy); border-radius: 14px; padding: 1.5rem;
    margin-bottom: 1.5rem; border: 2px solid rgba(200,240,76,0.2);
}
.lb-title { color: white; font-weight: 700; font-size: 1.05rem; margin: 0 0 0.25rem; }
.lb-meta  { color: rgba(255,255,255,0.45); font-size: 0.78rem; }

/* ── Stats row ── */
.stat-block {
    text-align: center; padding: 1rem;
    background: var(--surface); border-radius: 10px;
}
.stat-num   { font-size: 2rem; font-weight: 800; color: var(--navy); line-height: 1; }
.stat-label {
    font-size: 0.72rem; color: var(--subtle); margin-top: 4px;
    text-transform: uppercase; letter-spacing: 0.06em;
}
</style>
""", unsafe_allow_html=True)

# ── Device Registry ───────────────────────────────────────────────────────────
DEVICES = [
    # Desktop
    {
        "name": "Chrome · Windows", "cat": "desktop", "engine": "chromium",
        "vp": (1920, 1080),
        "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    },
    {
        "name": "Chrome · macOS", "cat": "desktop", "engine": "chromium",
        "vp": (1440, 900),
        "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    },
    {
        "name": "Edge · Windows", "cat": "desktop", "engine": "chromium",
        "vp": (1920, 1080),
        "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.2210.91",
    },
    {
        "name": "Firefox · Windows", "cat": "desktop", "engine": "firefox",
        "vp": (1920, 1080),
        "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    },
    {
        "name": "Safari · macOS", "cat": "desktop", "engine": "webkit",
        "vp": (1440, 900),
        "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    },
    # Mobile
    {
        "name": "iPhone 15 Pro", "cat": "mobile", "engine": "webkit",
        "vp": (393, 852),
        "ua": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
        "mobile": True, "dpr": 3,
    },
    {
        "name": "iPhone SE (3rd gen)", "cat": "mobile", "engine": "webkit",
        "vp": (375, 667),
        "ua": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
        "mobile": True, "dpr": 2,
    },
    {
        "name": "Samsung Galaxy S23", "cat": "mobile", "engine": "chromium",
        "vp": (360, 780),
        "ua": "Mozilla/5.0 (Linux; Android 13; SM-S911B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.144 Mobile Safari/537.36",
        "mobile": True, "dpr": 3,
    },
    {
        "name": "Google Pixel 7", "cat": "mobile", "engine": "chromium",
        "vp": (412, 915),
        "ua": "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.144 Mobile Safari/537.36",
        "mobile": True, "dpr": 3,
    },
    {
        "name": 'iPad Pro 12.9"', "cat": "mobile", "engine": "webkit",
        "vp": (1024, 1366),
        "ua": "Mozilla/5.0 (iPad; CPU OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
        "mobile": True, "dpr": 2,
    },
]

BANNER_JS = """
() => {
    /* ── Per-platform selectors (major CMPs) ── */
    const bySelector = [
        /* Didomi */
        '#didomi-host', '#didomi-popup', '.didomi-popup-notice',
        '.didomi-notice', '[id*="didomi"]', '[class*="didomi"]',

        /* Cookiebot */
        '#CybotCookiebotDialog', '#CybotCookiebotDialogBodyUnderlay',
        '[id*="CookieConsent"]',

        /* CookieYes / CookieLaw */
        '.cky-consent-bar', '.cky-modal', '.cky-overlay',
        '#cky-consent', '[id*="cky-"]', '[class*="cky-"]',

        /* OneTrust */
        '#onetrust-consent-sdk', '#onetrust-banner-sdk',
        '.onetrust-pc-dark-filter', '#onetrust-pc-sdk',

        /* Usercentrics */
        '#usercentrics-root', '[class*="usercentrics"]', '[id*="usercentrics"]',
        'uc-ui-container',

        /* TrustArc / TRUSTe */
        '.trustarc-banner-container', '#truste-consent-content',
        '[id*="truste"]', '[class*="truste"]', '[id*="trustarc"]',

        /* Quantcast Choice */
        '#qc-cmp2-ui', '.qc-cmp2-ui', '.qc-cmp2-persistent-link',

        /* Sourcepoint */
        '._sp_overlay', '._sp_message-overlay', '._sp_message',
        '[id*="sp_message"]',

        /* Axeptio */
        '#axeptio_overlay', '.axeptio-widget', '#axeptio-widget',

        /* Iubenda */
        '#iubenda-cs-banner', '.iubenda-cs-accept-btn-handler',
        '.iubenda-cs-content',

        /* Borlabs Cookie */
        '#BorlabsCookieBox', '.borlabs-cookie',

        /* Complianz (WordPress) */
        '.cmplz-cookiebanner', '#cmplz-cookiebanner',

        /* WP Cookie Notice */
        '#cookie-notice', '.cookie-notice-container',

        /* Moove GDPR (WordPress) */
        '#moove_gdpr_cookie_info_bar',

        /* CIVIC Cookie Control */
        '#ccc', '#ccc-overlay', '#ccc-module',

        /* Klaro */
        '.klaro', '.klaro .cookie-modal', '.klaro .cookie-notice',

        /* Termly */
        '#termly-code-snippet-support',

        /* CookiePro */
        '#cookie-pro-banner',

        /* Cookie Consent by Insites (cc.js) */
        '.cc-window', '.cc-banner', '.cc-overlay', '.cc-revoke',

        /* Generic patterns */
        '#cookie-consent', '#cookie-bar', '#cookie-policy', '#cookie-banner',
        '[id*="cookie"]', '[class*="cookie"]',
        '[id*="consent"]', '[class*="consent"]',
        '[id*="gdpr"]', '[class*="gdpr"]',
        '[class*="CookieBanner"]', '[class*="cookiebanner"]',
        '[class*="cookie-wall"]', '[id*="cookie-wall"]',
        '[aria-modal="true"][role="dialog"]',
        '[role="alertdialog"]',
    ];

    bySelector.forEach(sel => {
        try { document.querySelectorAll(sel).forEach(el => el.remove()); } catch(e) {}
    });

    /* ── Fallback: scan fixed/sticky overlays by text content ── */
    const keywords = [
        'cookie', 'consent', 'privacy', 'gdpr',
        'akkoord', 'accepteer', 'accept', 'toestemming',
        'we use cookies', 'wij gebruiken',
    ];
    document.querySelectorAll('*').forEach(el => {
        try {
            const s = window.getComputedStyle(el);
            if ((s.position === 'fixed' || s.position === 'sticky') &&
                parseInt(s.zIndex || '0') > 100 &&
                el.offsetHeight > 60 && el.offsetWidth > 200) {
                const txt = (el.textContent || '').toLowerCase();
                if (keywords.some(k => txt.includes(k))) el.remove();
            }
        } catch(e) {}
    });

    /* ── Remove body scroll lock (null-safe) ── */
    if (document.body) {
        document.body.style.overflow = 'auto';
        document.body.style.position = '';
    }
    if (document.documentElement) {
        document.documentElement.style.overflow = 'auto';
        document.documentElement.style.position = '';
    }
}
"""

# ── Helpers ───────────────────────────────────────────────────────────────────
def ensure_https(url: str) -> str:
    url = url.strip()
    if not url:
        return ""
    return url if re.match(r"^https?://", url) else f"https://{url}"


def capture(url: str, device: dict, out_dir: str, idx: int, hide_banners: bool, full_page: bool) -> dict:
    result = {
        "device": device["name"],
        "cat": device["cat"],
        "engine": device["engine"],
        "vp": f"{device['vp'][0]}×{device['vp'][1]}",
        "path": "",
        "status": "error",
    }

    with sync_playwright() as p:
        browser = getattr(p, device["engine"]).launch(headless=True)
        ctx_opts = {
            "viewport": {"width": device["vp"][0], "height": device["vp"][1]},
            "user_agent": device["ua"],
        }
        if device.get("mobile"):
            ctx_opts["is_mobile"] = True
            ctx_opts["device_scale_factor"] = device.get("dpr", 2)

        ctx = browser.new_context(**ctx_opts)
        page = ctx.new_page()

        safe = re.sub(r"[^a-z0-9]", "_", device["name"].lower().replace('"', ""))
        path = os.path.join(out_dir, f"{safe}_{idx}.png")

        try:
            # networkidle ensures JS-rendered banners are present before we remove them
            page.goto(url, wait_until="networkidle", timeout=40_000)

            if hide_banners:
                try:
                    page.evaluate(BANNER_JS)
                except Exception:
                    pass
                page.wait_for_timeout(400)

            page.screenshot(path=path, full_page=full_page)
            result.update(path=path, status="ok")

        except Exception as e:
            result["status"] = f"Error: {str(e)[:120]}"
        finally:
            browser.close()

    return result


def render_grid(items: list, tab: str = ""):
    if not items:
        st.info("No results in this category.")
        return

    cols = st.columns(3)
    for i, r in enumerate(items):
        with cols[i % 3]:
            eng_cls = f"eng-{r['engine']}"
            st.markdown(
                f"""
                <div class="device-card">
                    <div class="card-header">
                        <div>
                            <div class="card-device">{r['device']}</div>
                            <div class="card-vp">{r['vp']}</div>
                        </div>
                        <span class="eng-badge {eng_cls}">{r['engine'].title()}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if r["status"] == "ok" and os.path.exists(r["path"]):
                st.image(r["path"], use_container_width=True)
                if st.button("🔍 Full size", key=f"lb_{tab}_{i}_{r['device']}"):
                    st.session_state.bm_lightbox = r
                    st.rerun()
            else:
                st.error(r["status"])


# ── Session state ─────────────────────────────────────────────────────────────
if "bm_results" not in st.session_state:
    st.session_state.bm_results = []
if "bm_lightbox" not in st.session_state:
    st.session_state.bm_lightbox = None

# ── Page header ───────────────────────────────────────────────────────────────
logo_path = os.path.join(os.path.dirname(__file__), "brand_assets", "hh-logo.png")
if os.path.exists(logo_path):
    st.image(logo_path, width=140)

st.markdown(
    """
    <div class="hh-page-header">
        <h1>Browser Matrix <span class="hh-badge">New</span></h1>
        <p>Screenshot any URL across 10 browser &amp; device presets — desktop and mobile, side by side.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    if os.path.exists(logo_path):
        st.image(logo_path, width=130)
    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown('<span class="sidebar-label">URL</span>', unsafe_allow_html=True)
    url_input = st.text_input("URL", placeholder="https://example.com", label_visibility="collapsed")

    st.markdown('<span class="sidebar-label">Capture options</span>', unsafe_allow_html=True)
    full_page    = st.checkbox("Full-page screenshot", value=False)
    hide_banners = st.checkbox("Hide cookie banners", value=True)

    st.markdown('<span class="sidebar-label">Performance</span>', unsafe_allow_html=True)
    workers = st.slider("Parallel browsers", 1, 5, 3, help="More workers = faster, but uses more memory")

    st.markdown('<span class="sidebar-label">Devices</span>', unsafe_allow_html=True)
    selected_names = []
    for d in DEVICES:
        icon = "🖥" if d["cat"] == "desktop" else "📱"
        if st.checkbox(f"{icon}  {d['name']}", value=True, key=f"dev_{d['name']}"):
            selected_names.append(d["name"])

    st.markdown("<hr>", unsafe_allow_html=True)
    run_btn = st.button("▶  Run capture", type="primary", use_container_width=True)

# ── Run ───────────────────────────────────────────────────────────────────────
if run_btn:
    if not url_input.strip():
        st.warning("Enter a URL first.")
    else:
        url = ensure_https(url_input)
        selected = [d for d in DEVICES if d["name"] in selected_names]

        if not selected:
            st.warning("Select at least one device.")
        else:
            out_dir = "bm_screenshots"
            if os.path.exists(out_dir):
                shutil.rmtree(out_dir)
            os.makedirs(out_dir)

            st.session_state.bm_lightbox = None

            with st.spinner(f"Capturing {len(selected)} screenshots across browsers…"):
                with ThreadPoolExecutor(max_workers=workers) as pool:
                    futures = [
                        pool.submit(capture, url, d, out_dir, i, hide_banners, full_page)
                        for i, d in enumerate(selected)
                    ]
                    st.session_state.bm_results = [f.result() for f in futures]

# ── Lightbox ──────────────────────────────────────────────────────────────────
if st.session_state.bm_lightbox:
    lb = st.session_state.bm_lightbox
    st.markdown(
        f"""
        <div class="lb-wrap">
            <p class="lb-title">🔍 {lb['device']}</p>
            <p class="lb-meta">{lb['engine'].title()} · {lb['vp']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.image(lb["path"], use_container_width=True)
    if st.button("✕  Close", key="lb_close"):
        st.session_state.bm_lightbox = None
        st.rerun()
    st.markdown("---")

# ── Results ───────────────────────────────────────────────────────────────────
results = st.session_state.bm_results

if results:
    ok    = [r for r in results if r["status"] == "ok"]
    errs  = [r for r in results if r["status"] != "ok"]
    desks = [r for r in results if r["cat"] == "desktop"]
    mobs  = [r for r in results if r["cat"] == "mobile"]

    c1, c2, c3, c4 = st.columns(4)
    for col, num, label in [
        (c1, len(ok),    "Captured"),
        (c2, len(errs),  "Errors"),
        (c3, len(desks), "Desktop"),
        (c4, len(mobs),  "Mobile"),
    ]:
        col.markdown(
            f'<div class="stat-block"><div class="stat-num">{num}</div>'
            f'<div class="stat-label">{label}</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    tab_all, tab_desk, tab_mob = st.tabs([
        f"All ({len(results)})",
        f"Desktop ({len(desks)})",
        f"Mobile ({len(mobs)})",
    ])

    with tab_all:   render_grid(results, "all")
    with tab_desk:  render_grid(desks,   "desk")
    with tab_mob:   render_grid(mobs,    "mob")

    st.markdown("---")
    zip_path = "bm_results.zip"
    with zipfile.ZipFile(zip_path, "w") as z:
        for r in ok:
            if os.path.exists(r["path"]):
                z.write(r["path"], arcname=os.path.basename(r["path"]))

    with open(zip_path, "rb") as f:
        st.download_button(
            "📦 Download all screenshots (.zip)",
            f,
            file_name="browser_matrix.zip",
            type="primary",
        )
