import streamlit as st
from auth import init_auth_db
from ui import inject_css

st.set_page_config(
    page_title="foodieSense 🍽️",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="auto",
)
inject_css()
init_auth_db()

if "user_id"  not in st.session_state: st.session_state.user_id  = None
if "username" not in st.session_state: st.session_state.username = None

# ── All pages are always registered, so anyone can reach any page from the navbar ──
home  = st.Page("views/home.py",            title="Home",            icon="🏠", default=True)
recs  = st.Page("views/recommendations.py", title="Recommendations", icon="🍽️")
fb    = st.Page("views/my_feedback.py",     title="My Feedback",     icon="⭐")
model = st.Page("views/my_model.py",        title="My Model",        icon="🤖")
cart  = st.Page("views/cart.py",            title="Cart",            icon="🛒")
login = st.Page("views/login.py",           title="Login",           icon="🔑")

nav = st.navigation([home, recs, fb, model, cart, login], position="hidden")

# ── Top navbar (shown on every page) ──────────────────────────────────────────
with st.container(key="navbar"):
    c_brand, c1, c2, c3, c4, c5, c_user = st.columns([2, 0.9, 1.8, 1.4, 1.3, 1.2, 2.4])
    c_brand.markdown('<div class="nav-brand">🍽️ foodieSense</div>', unsafe_allow_html=True)
    c1.page_link(home,  label="Home",            icon="🏠")
    c2.page_link(recs,  label="Recommendations", icon="🍽️")
    c3.page_link(fb,    label="My Feedback",     icon="⭐")
    c4.page_link(model, label="My Model",        icon="🤖")
    n_items = sum(i["qty"] for i in st.session_state.get("cart", {}).values())
    c5.page_link(cart,  label=f"Cart ({n_items})" if n_items else "Cart", icon="🛒")
    with c_user:
        if st.session_state.user_id is None:
            st.page_link(login, label="Login / Sign Up", icon="🔑", use_container_width=True)
        else:
            u1, u2 = st.columns([1.5, 1])
            u1.markdown(f'<div class="user-chip">👤 {st.session_state.username}</div>', unsafe_allow_html=True)
            if u2.button("Logout", use_container_width=True):
                st.session_state.user_id  = None
                st.session_state.username = None
                st.switch_page(home)

nav.run()
