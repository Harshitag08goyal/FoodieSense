"""ui.py — shared look & feel for every foodieSense page."""
import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800;900&display=swap');
*, *::before, *::after { font-family: 'Poppins', sans-serif !important; box-sizing: border-box; }
/* keep Streamlit's icon font (fixes "keyboard_arrow_down" text overlapping labels) */
[data-testid="stIconMaterial"], span[class*="material-symbols"], .material-icons, .material-symbols-rounded {
    font-family: 'Material Symbols Rounded' !important;
}
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"] { visibility: hidden; }
header[data-testid="stHeader"] { background: #0a0a0a !important; border-bottom: 1px solid #161616; }
.block-container { padding: 3.5rem 2rem 2rem !important; max-width: 1400px !important; }
.stApp { background: #080808 !important; }
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-thumb { background: #ff6b35; border-radius: 3px; }

/* ── Top navbar ── */
.st-key-navbar {
    background: #0d0d0d; border: 1px solid #1c1c1c; border-radius: 18px;
    padding: 0.55rem 1.1rem; margin-bottom: 1.6rem;
    box-shadow: 0 8px 30px rgba(0,0,0,0.5);
}
.st-key-navbar [data-testid="stHorizontalBlock"] { align-items: center; }
.nav-brand { font-size:1.15rem; font-weight:800; background:linear-gradient(135deg,#fff 30%,#ff6b35 100%);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; white-space:nowrap; }
.st-key-navbar [data-testid="stPageLink-NavLink"] {
    justify-content:center; border-radius:12px; padding:0.45rem 0.6rem; color:#aaa;
    font-size:0.85rem; font-weight:600; transition: all .2s;
}
.st-key-navbar [data-testid="stPageLink-NavLink"]:hover { background:#1a1a1a; color:#fff; }
.st-key-navbar [data-testid="stPageLink-NavLink"][aria-current="page"] {
    background: linear-gradient(135deg,#ff6b35,#ff9a3c); color:#fff;
}
.st-key-navbar .user-chip { margin-bottom:0; }
.st-key-navbar .stButton > button { padding: 0.4rem 0.8rem !important; font-size:0.8rem !important; }

/* Auth card */
.auth-card {
    max-width: 420px;
    margin: 4rem auto;
    background: #0f0f0f;
    border: 1px solid #1e1e1e;
    border-radius: 24px;
    padding: 2.5rem 2rem;
    box-shadow: 0 0 80px rgba(255,107,53,0.06);
}
.auth-logo { text-align:center; font-size:2.4rem; font-weight:900; background:linear-gradient(135deg,#fff 30%,#ff6b35 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:0.3rem; }
.auth-sub  { text-align:center; color:#444; font-size:0.85rem; margin-bottom:2rem; }
.auth-tab  { display:flex; gap:4px; background:#111; border-radius:12px; padding:4px; margin-bottom:1.5rem; }
.auth-tab-btn { flex:1; text-align:center; padding:8px; border-radius:9px; font-size:0.82rem; font-weight:600; cursor:pointer; color:#555; transition:all 0.2s; }
.auth-tab-btn.active { background:#ff6b35; color:#fff; }

/* Inputs */
input[type="text"], input[type="password"] {
    background: #111 !important;
    border: 1px solid #1e1e1e !important;
    color: #fff !important;
    border-radius: 10px !important;
}
input:focus { border-color: #ff6b35 !important; box-shadow: 0 0 0 2px rgba(255,107,53,0.15) !important; }
.stTextInput > label { color: #666 !important; font-size: 0.8rem !important; }

/* Primary button */
.stButton > button {
    background: linear-gradient(135deg,#ff6b35,#f7931e) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    transition: all 0.2s !important;
    box-shadow: 0 4px 15px rgba(255,107,53,0.3) !important;
}
.stButton > button:hover { transform: translateY(-2px) !important; box-shadow: 0 6px 20px rgba(255,107,53,0.4) !important; }

/* Sidebar */
section[data-testid="stSidebar"] { background: #0a0a0a !important; border-right: 1px solid #111 !important; }
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] p { color: #bbb !important; }
.sb-title { font-size:1.1rem; font-weight:800; color:#fff !important; }
.sb-live  { display:inline-block; background:rgba(111,207,151,0.12); border:1px solid rgba(111,207,151,0.25); color:#6fcf97; font-size:0.65rem; font-weight:700; padding:2px 8px; border-radius:20px; margin-left:6px; text-transform:uppercase; letter-spacing:1px; }
.user-chip { display:inline-flex; align-items:center; gap:8px; background:#111; border:1px solid #1e1e1e; border-radius:30px; padding:6px 14px; color:#fff; font-size:0.82rem; font-weight:600; margin-bottom:0.5rem; }

/* Hero */
.hero-box { background:#0f0f0f; border:1px solid #1a1a1a; border-radius:24px; padding:2.5rem; text-align:center; margin-bottom:1.5rem; box-shadow:0 0 80px rgba(255,107,53,0.05); }
.hero-tag { display:inline-block; background:rgba(255,107,53,0.1); border:1px solid rgba(255,107,53,0.2); color:#ff6b35; font-size:0.7rem; font-weight:700; padding:3px 14px; border-radius:30px; margin-bottom:0.8rem; text-transform:uppercase; letter-spacing:1px; }
.hero-title { font-size:3rem; font-weight:900; background:linear-gradient(135deg,#fff 30%,#ff6b35 70%,#ffcd3c 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;line-height:1.1;margin-bottom:0.4rem; }
.hero-sub { color:#555; font-size:0.9rem; margin:0; }

/* Stats */
.stat-box { background:#0f0f0f; border:1px solid #161616; border-radius:16px; padding:1rem; text-align:center; margin-bottom:1rem; }
.stat-num { font-size:1.8rem; font-weight:800; color:#ff6b35; }
.stat-lbl { font-size:0.65rem; color:#444; text-transform:uppercase; letter-spacing:1px; margin-top:2px; }

/* Section header */
.sec-head { display:flex; align-items:center; gap:10px; margin:0.5rem 0 1.2rem; }
.sec-head h2 { margin:0; font-size:1.3rem; font-weight:800; color:#fff; white-space:nowrap; }
.sec-line { flex:1; height:1px; background:linear-gradient(90deg,#1e1e1e,transparent); }
.sec-badge { font-size:0.68rem; font-weight:700; padding:3px 10px; border-radius:20px; }
.sec-badge.ml  { background:rgba(111,207,151,0.1); border:1px solid rgba(111,207,151,0.2); color:#6fcf97; }
.sec-badge.sim { background:rgba(124,131,253,0.1); border:1px solid rgba(124,131,253,0.2); color:#7c83fd; }
.sec-count { color:#444; font-size:0.78rem; }

/* Food cards */
.food-card { background:#0f0f0f; border-radius:20px; overflow:hidden; border:1px solid #161616; transition:all 0.3s cubic-bezier(0.4,0,0.2,1); margin-bottom:1.4rem; }
.food-card:hover { transform:translateY(-7px) scale(1.01); border-color:rgba(255,107,53,0.35); box-shadow:0 18px 50px rgba(255,107,53,0.12),0 4px 20px rgba(0,0,0,0.5); }
.fc-img-wrap { position:relative; overflow:hidden; }
.fc-img { width:100%; height:195px; object-fit:cover; display:block; transition:transform 0.4s; }
.food-card:hover .fc-img { transform:scale(1.06); }
.fc-overlay { position:absolute; inset:0; background:linear-gradient(to top,rgba(0,0,0,0.65) 0%,transparent 55%); }
.fc-rank { position:absolute; top:10px; left:10px; background:rgba(0,0,0,0.65); border:1px solid rgba(255,255,255,0.08); color:#ff6b35; font-size:0.68rem; font-weight:800; padding:3px 10px; border-radius:20px; backdrop-filter:blur(4px); }
.fc-price { position:absolute; bottom:10px; right:10px; background:#ff6b35; color:#fff; font-size:0.78rem; font-weight:700; padding:3px 12px; border-radius:20px; z-index:2; }
.fc-cal  { position:absolute; top:10px; right:10px; background:rgba(0,0,0,0.65); border:1px solid rgba(255,255,255,0.08); color:#fff; font-size:0.68rem; font-weight:600; padding:3px 10px; border-radius:20px; backdrop-filter:blur(4px); }
.fc-body { padding:1rem 1.1rem 0.7rem; }
.fc-name { color:#fff; margin:0 0 0.5rem; font-size:1.05rem; font-weight:700; }
.badge { display:inline-block; border-radius:20px; padding:2px 9px; font-size:0.67rem; font-weight:600; margin:0 2px 4px 0; }
.b-cuisine { background:rgba(124,131,253,0.1); color:#7c83fd; border:1px solid rgba(124,131,253,0.18); }
.b-cat     { background:rgba(111,207,151,0.08); color:#6fcf97; border:1px solid rgba(111,207,151,0.18); }
.b-nonveg  { background:rgba(235,87,87,0.08);   color:#eb5757; border:1px solid rgba(235,87,87,0.18); }
.b-veg     { background:rgba(111,207,151,0.08); color:#6fcf97; border:1px solid rgba(111,207,151,0.18); }
.fc-div    { height:1px; background:#161616; margin:0.6rem 0; }
.rating-row { display:flex; align-items:center; gap:8px; }
.rating-bar { flex:1; height:4px; background:#1a1a1a; border-radius:2px; overflow:hidden; }
.rating-fill { height:100%; border-radius:2px; background:linear-gradient(90deg,#ff6b35,#ffcd3c); }
.rating-num { color:#f7c59f; font-size:0.78rem; font-weight:700; }
.fc-reason { color:#3a3a3a; font-size:0.72rem; font-style:italic; margin-top:0.5rem; padding:0.35rem 0.6rem; background:rgba(255,107,53,0.03); border-left:2px solid rgba(255,107,53,0.15); border-radius:0 6px 6px 0; }

/* Feedback buttons */
div[data-testid="stHorizontalBlock"] .stButton button {
    background:#111 !important; color:#555 !important;
    border:1px solid #1a1a1a !important; border-radius:10px !important;
    box-shadow:none !important; font-size:0.78rem !important;
}
div[data-testid="stHorizontalBlock"] .stButton button:hover {
    border-color:#ff6b35 !important; color:#ff6b35 !important;
    background:rgba(255,107,53,0.05) !important; transform:none !important;
}
</style>
"""


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)


def section_head(title: str, right_html: str = ""):
    st.markdown(
        f'<div class="sec-head"><h2>{title}</h2><div class="sec-line"></div>{right_html}</div>',
        unsafe_allow_html=True,
    )


def require_login():
    """Call at the top of any page that needs an account."""
    if st.session_state.get("user_id") is None:
        _, mid, _ = st.columns([1, 1.6, 1])
        with mid:
            st.markdown(
                '<div class="auth-card" style="margin:3rem auto 1rem;text-align:center">'
                '<div style="font-size:2.4rem">🔒</div>'
                '<div style="color:#fff;font-weight:700;font-size:1.1rem;margin:.5rem 0">Please login first</div>'
                '<div class="auth-sub" style="margin-bottom:0">You need an account to use this page.</div></div>',
                unsafe_allow_html=True,
            )
            st.page_link("views/login.py", label="Go to Login / Sign Up", icon="🔑", use_container_width=True)
        st.stop()


def stat_row(items):
    """items = [(number, label), ...]"""
    for col, (num, lbl) in zip(st.columns(len(items)), items):
        col.markdown(
            f'<div class="stat-box"><div class="stat-num">{num}</div>'
            f'<div class="stat-lbl">{lbl}</div></div>',
            unsafe_allow_html=True,
        )
