from pathlib import Path
import json, streamlit as st, pandas as pd
from infrastructure.config_loader import get_paths
from infrastructure.file_logger import load_json, save_json

BASE = Path(__file__).resolve().parent.parent.parent
PAIR_PATH = BASE / "config" / "pair_status.json"
API_PATH  = BASE / "config" / "api_settings.json"
TRANSFORM = BASE / "config" / "transform_ui.json"
DECISION_DIR = BASE / get_paths().get("decision_log", "user_data/decision_log")
DECISION_DIR.mkdir(parents=True, exist_ok=True)

st.set_page_config(page_title="Vision Realizer RIN v2", layout="wide")
st.title("Vision Realizer RIN v2")
tab1, tab2, tab3, tab4 = st.tabs(["銘柄管理", "ログ閲覧", "API設定", "整形ルール"])

# ───────── tab1 ─────────
with tab1:
    pdata = load_json(PAIR_PATH, {})
    slugs = sorted(
        f"{c}/{e}/{p}"
        for c, exd in pdata.items() if c != "schema_version"
        for e, pd in exd.items()
        for p in pd
    )
    def flag(c,e,p):
        m = pdata[c][e][p]
        return m.get("manual_enabled", True) if isinstance(m, dict) else bool(m)

    st.session_state.setdefault("enabled_pairs",
        {s: flag(*s.split("/")) for s in slugs})

    st.subheader("銘柄一覧")
    for s in slugs:
        st.session_state.enabled_pairs[s] = st.checkbox(s, st.session_state.enabled_pairs[s])

    if st.button("保存"):
        for s,f in st.session_state.enabled_pairs.items():
            c,e,p = s.split("/")
            pdata[c][e][p] = {"manual_enabled": f}
        save_json(PAIR_PATH, pdata)
        st.success("保存しました")

# ───────── tab2 ─────────
with tab2:
    st.subheader("decision_log")
    logs = sorted(f.name for f in DECISION_DIR.glob("*.json"))
    if logs:
        sel = st.selectbox("ファイル", logs)
        df = pd.read_json(DECISION_DIR/sel, lines=True)
        st.dataframe(df.tail(20))
    else:
        st.info("ログなし")

# ───────── tab3 ─────────
with tab3:
    st.subheader("API設定")
    cfg = load_json(API_PATH, {})
    k  = st.text_input("API Key", cfg.get("api_key",""), type="password")
    s  = st.text_input("Secret",  cfg.get("api_secret",""), type="password")
    ep = st.text_input("Endpoint",cfg.get("api_endpoint",""))
    if st.button("API保存"):
        save_json(API_PATH, {"api_key":k,"api_secret":s,"api_endpoint":ep})
        st.success("保存しました")

# ───────── tab4 ─────────
with tab4:
    st.subheader("transform_ui.json")
    t = load_json(TRANSFORM, {})
    st.json(t)
