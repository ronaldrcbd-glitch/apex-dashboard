import json
import plotly.graph_objects as go
import streamlit as st
import pandas as pd
from datetime import datetime as _dt
from pathlib import Path

DATA_FILE = Path(__file__).parent / "apex_data.json"

st.set_page_config(page_title="APEX PA Monitor | Ronald Rodriguez", layout="wide", page_icon="🔥")

# ──────────────────────────────────────────────
# GLOBAL STYLES
# ──────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

    /* Hide streamlit branding */
    #MainMenu, footer, header {visibility: hidden;}
    .block-container {padding-top: 1rem; padding-bottom: 1rem; max-width: 1400px;}

    /* Global font */
    html, body, [class*="css"] {font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;}

    /* Header banner */
    .header-banner {
        background: linear-gradient(135deg, #0c1222 0%, #1a1040 40%, #0f172a 100%);
        border: 1px solid rgba(99,102,241,0.2);
        border-radius: 16px; padding: 24px 32px; margin-bottom: 20px;
        position: relative; overflow: hidden;
    }
    .header-banner::before {
        content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
        background: linear-gradient(90deg, #6366f1, #8b5cf6, #a855f7, #6366f1);
        background-size: 200% auto; animation: shimmer 3s linear infinite;
    }
    @keyframes shimmer { to { background-position: 200% center; } }
    .header-title {font-size: 1.8rem; font-weight: 900; letter-spacing: -1px;
        background: linear-gradient(135deg, #e2e8f0, #c7d2fe); -webkit-background-clip: text;
        -webkit-text-fill-color: transparent; margin: 0; line-height: 1.2;}
    .header-sub {color: #818cf8; font-size: 0.85rem; font-weight: 600; letter-spacing: 2px;
        text-transform: uppercase; margin-top: 4px;}
    .header-right {color: #64748b; font-size: 0.75rem; text-align: right;}
    .header-right b {color: #94a3b8;}

    /* KPI cards */
    .kpi {background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        border: 1px solid rgba(51,65,85,0.5); backdrop-filter: blur(10px);
        border-radius: 14px; padding: 18px 20px; text-align: center;
        position: relative; overflow: hidden; transition: transform 0.2s, border-color 0.2s;}
    .kpi:hover {transform: translateY(-2px); border-color: rgba(99,102,241,0.3);}
    .kpi::before {content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;}
    .kpi-green::before {background: linear-gradient(90deg, #22c55e, #4ade80);}
    .kpi-yellow::before {background: linear-gradient(90deg, #eab308, #facc15);}
    .kpi-red::before {background: linear-gradient(90deg, #ef4444, #f87171);}
    .kpi-blue::before {background: linear-gradient(90deg, #3b82f6, #60a5fa);}
    .kpi-purple::before {background: linear-gradient(90deg, #8b5cf6, #a855f7);}
    .kpi-label {color: #64748b; font-size: 0.7rem; text-transform: uppercase;
        letter-spacing: 1.5px; font-weight: 700; margin-bottom: 6px;}
    .kpi-value {color: #f1f5f9; font-size: 1.7rem; font-weight: 900; line-height: 1.1;}
    .kpi-sub {color: #94a3b8; font-size: 0.75rem; margin-top: 4px; font-weight: 500;}

    /* Badges */
    .badge {padding: 3px 12px; border-radius: 20px; font-weight: 700;
        font-size: 0.7rem; letter-spacing: 0.5px; display: inline-block;}
    .badge-safe {background: rgba(34,197,94,0.15); color: #4ade80; border: 1px solid rgba(34,197,94,0.3);}
    .badge-watch {background: rgba(234,179,8,0.15); color: #facc15; border: 1px solid rgba(234,179,8,0.3);}
    .badge-danger {background: rgba(239,68,68,0.15); color: #f87171; border: 1px solid rgba(239,68,68,0.3);}

    /* Alert bars */
    .alert {padding: 10px 16px; border-radius: 10px; margin-bottom: 6px;
        font-size: 0.82rem; border-left: 4px solid; font-weight: 500;
        backdrop-filter: blur(4px);}
    .alert-red {background: rgba(239,68,68,0.06); border-color: #ef4444; color: #fca5a5;}
    .alert-yellow {background: rgba(234,179,8,0.06); border-color: #eab308; color: #fde68a;}
    .alert-green {background: rgba(34,197,94,0.06); border-color: #22c55e; color: #86efac;}

    /* Rules box */
    .rules-box {background: linear-gradient(135deg, #0f172a, #1e293b);
        border: 1px solid #334155; border-radius: 10px; padding: 12px 18px;
        font-size: 0.78rem; color: #94a3b8;}
    .rules-box b {color: #c7d2fe;}

    /* Account cards */
    .acct-card {background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        border: 1px solid rgba(51,65,85,0.5); backdrop-filter: blur(10px);
        border-radius: 14px; padding: 20px; margin-bottom: 16px;
        position: relative; overflow: hidden; transition: border-color 0.2s;}
    .acct-card:hover {border-color: rgba(99,102,241,0.3);}
    .acct-card::before {content: ''; position: absolute; top: 0; left: 0; bottom: 0; width: 4px;}
    .acct-card-safe::before {background: linear-gradient(180deg, #22c55e, #16a34a);}
    .acct-card-watch::before {background: linear-gradient(180deg, #eab308, #ca8a04);}
    .acct-card-danger::before {background: linear-gradient(180deg, #ef4444, #dc2626);}

    /* Checklist */
    .check-pass {color: #4ade80; font-weight: 600; font-size: 0.82rem;}
    .check-fail {color: #64748b; font-weight: 500; font-size: 0.82rem;}

    /* Mini pnl bars */
    .pnl-bar {height: 20px; border-radius: 3px; margin: 1px 0; min-width: 2px;
        transition: opacity 0.2s;}

    /* Plotly chart bg */
    .stPlotlyChart {border-radius: 14px; overflow: hidden;}

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {gap: 4px; background: rgba(15,23,42,0.5);
        border-radius: 12px; padding: 4px;}
    .stTabs [data-baseweb="tab"] {padding: 8px 20px; border-radius: 8px;
        font-weight: 600; font-size: 0.85rem;}

    /* Section headers */
    .section-header {color: #c7d2fe; font-size: 1.1rem; font-weight: 700;
        letter-spacing: -0.3px; margin: 16px 0 12px 0; display: flex;
        align-items: center; gap: 8px;}
    .section-header span {font-size: 1.2rem;}

    /* Payout tracker */
    .payout-card {background: linear-gradient(135deg, #0f172a, #1e293b);
        border: 1px solid rgba(51,65,85,0.5); border-radius: 12px;
        padding: 16px 20px; margin-bottom: 10px;}
    .payout-acct {color: #e2e8f0; font-weight: 700; font-size: 0.95rem;}
    .payout-rule {display: flex; align-items: center; gap: 8px; padding: 4px 0;
        font-size: 0.8rem;}
    .payout-pass {color: #4ade80;}
    .payout-fail {color: #475569;}
    .payout-bar-bg {flex: 1; height: 6px; background: #1e293b; border-radius: 3px; overflow: hidden;}
    .payout-bar-fill {height: 100%; border-radius: 3px; transition: width 0.5s ease;}
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# DATA & COMPUTATIONS
# ──────────────────────────────────────────────
@st.cache_data(ttl=30)
def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def compute_consistency(daily_pnl, profit_total):
    if profit_total <= 0:
        return 0.0
    positive_days = [p for p in daily_pnl if p > 0]
    if not positive_days:
        return 0.0
    return round((max(positive_days) / profit_total) * 100, 1)


def count_50_dollar_days(daily_pnl):
    return sum(1 for p in daily_pnl if p >= 50)


def check_payout_eligible(a):
    rules = {}
    rules["profit_target"] = a["balance"] >= a["min_payout_balance"]
    rules["min_days"] = a["days_traded"] >= a["min_days_required"]
    rules["fifty_dollar_days"] = count_50_dollar_days(a["daily_pnl"]) >= 5
    consistency = compute_consistency(a["daily_pnl"], a["profit_total"])
    rules["consistency"] = consistency <= 30.0 if a["profit_total"] > 0 else True
    return rules, consistency


def determine_status(a, rules):
    dd_usage = abs(a["trailing_drawdown"]) / abs(a["max_loss_limit"]) if a["max_loss_limit"] != 0 else 0
    if a["profit_total"] < -500 or dd_usage > 0.85:
        return "DANGER"
    if a["profit_total"] < 0 or dd_usage > 0.65 or not rules.get("consistency", True):
        return "WATCH"
    return "SAFE"


def compute_risk_score(accounts):
    """Compute portfolio risk score 0-100 (100 = safest)."""
    scores = []
    for a in accounts:
        score = 100
        # Drawdown penalty (biggest factor)
        dd_pct = a["_dd_usage_pct"]
        if dd_pct > 90:
            score -= 50
        elif dd_pct > 85:
            score -= 40
        elif dd_pct > 75:
            score -= 25
        elif dd_pct > 65:
            score -= 15
        # Loss penalty
        if a["profit_total"] < -500:
            score -= 25
        elif a["profit_total"] < 0:
            score -= 10
        # Consistency penalty
        if a["profit_total"] > 0 and a["_consistency"] > 30:
            score -= 15
        elif a["profit_total"] > 0 and a["_consistency"] > 25:
            score -= 5
        scores.append(max(score, 0))
    return round(sum(scores) / len(scores)) if scores else 0


def badge(status):
    return f'<span class="badge badge-{status.lower()}">{status}</span>'


def cp(v):
    c = "#4ade80" if v >= 0 else "#f87171"
    return f"color: {c}; font-weight: 600"


def render_mini_pnl(daily_pnl):
    if not daily_pnl:
        return ""
    max_abs = max(abs(v) for v in daily_pnl) or 1
    bars = ""
    for v in daily_pnl:
        w = max(int(abs(v) / max_abs * 50), 2)
        c = "#4ade80" if v >= 0 else "#f87171"
        bars += f'<div class="pnl-bar" style="width:{w}px;background:{c};" title="${v:+.0f}"></div>'
    return f'<div style="display:flex;gap:1px;align-items:center;">{bars}</div>'


# Load
data = load_data()
accounts = data["accounts"]
last_updated = data.get("last_updated", "N/A")

# Compute fields
for a in accounts:
    rules, consistency = check_payout_eligible(a)
    a["_rules"] = rules
    a["_consistency"] = consistency
    a["_fifty_days"] = count_50_dollar_days(a["daily_pnl"])
    a["_all_passed"] = all(rules.values())
    a["_status"] = determine_status(a, rules)
    dd = abs(a["max_loss_limit"])
    a["_dd_usage_pct"] = round(abs(a["trailing_drawdown"]) / dd * 100, 1) if dd else 0
    a["_to_payout"] = a["min_payout_balance"] - a["balance"]

total_pnl = sum(a["profit_total"] for a in accounts)
total_balance = sum(a["balance"] for a in accounts)
safe_count = sum(1 for a in accounts if a["_status"] == "SAFE")
watch_count = sum(1 for a in accounts if a["_status"] == "WATCH")
danger_count = sum(1 for a in accounts if a["_status"] == "DANGER")
payout_ready = sum(1 for a in accounts if a["_all_passed"])
risk_score = compute_risk_score(accounts)


# ──────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 10px 0;">
        <div style="font-size:2rem; font-weight:900; background: linear-gradient(135deg, #818cf8, #c084fc);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;">APEX PA</div>
        <div style="color:#64748b; font-size:0.75rem; letter-spacing:3px; text-transform:uppercase; font-weight:600;">
            Risk Monitor</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("**Ronald Rodriguez**")
    st.caption("Personal Portfolio | 10x Legacy 50K")
    st.markdown("---")

    try:
        updated_dt = _dt.fromisoformat(last_updated)
        delta = _dt.now() - updated_dt
        if delta.days > 0:
            age = f"{delta.days}d ago"
            color = "#ef4444" if delta.days > 2 else "#eab308"
        else:
            age = f"{delta.seconds // 3600}h ago"
            color = "#4ade80"
    except Exception:
        age, color = "unknown", "#64748b"

    st.markdown(f"""
    <div style="background:#0f172a; border:1px solid #1e293b; border-radius:10px; padding:12px; text-align:center;">
        <div style="color:#64748b; font-size:0.7rem; text-transform:uppercase; letter-spacing:1px; font-weight:600;">Last Update</div>
        <div style="color:{color}; font-weight:800; font-size:1.1rem;">{age}</div>
        <div style="color:#475569; font-size:0.7rem; margin-top:2px;">{last_updated}</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("")
    st.caption("**Refresh:** Say *'actualiza los datos de Apex'* to Claude")
    st.markdown("---")
    st.markdown("[Apex Portal](https://dashboard.apextraderfunding.com/member) | [PA Charts](https://dashboard.apextraderfunding.com/AccountSummary/index/pa/acc)")
    st.markdown("---")
    st.markdown(f"""<div class="rules-box">
    <b>Legacy Rules 50K</b><br>
    Target: $52,600 | 8 Days | 5x $50+<br>
    Consistency: 30% | DD: $2,500 | 10 Contracts
    </div>""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# HEADER BANNER
# ──────────────────────────────────────────────
hdr_left, hdr_right = st.columns([3, 1])
with hdr_left:
    st.markdown(f"""
    <div class="header-banner">
        <div class="header-title">Apex PA Portfolio Monitor</div>
        <div class="header-sub">10 Performance Accounts | Legacy 50K Rithmic</div>
    </div>
    """, unsafe_allow_html=True)
with hdr_right:
    risk_color = "#4ade80" if risk_score >= 70 else "#facc15" if risk_score >= 40 else "#f87171"
    st.markdown(f"""
    <div class="header-banner" style="text-align:center;">
        <div style="color:#64748b; font-size:0.7rem; text-transform:uppercase; letter-spacing:2px; font-weight:700;">Portfolio Risk Score</div>
        <div style="color:{risk_color}; font-size:2.8rem; font-weight:900; line-height:1.1;">{risk_score}</div>
        <div style="color:#64748b; font-size:0.7rem;">/ 100</div>
    </div>
    """, unsafe_allow_html=True)


# ──────────────────────────────────────────────
# HEADER KPIs
# ──────────────────────────────────────────────
pnl_sign = "+" if total_pnl >= 0 else ""
pnl_css = "kpi-green" if total_pnl >= 0 else "kpi-red"
pnl_pct = (total_pnl / 500000) * 100

k1, k2, k3, k4, k5, k6 = st.columns(6)
with k1:
    st.markdown(f'<div class="kpi {pnl_css}"><div class="kpi-label">Total P&L</div><div class="kpi-value">{pnl_sign}${total_pnl:,.0f}</div><div class="kpi-sub">{pnl_sign}{pnl_pct:.2f}% return</div></div>', unsafe_allow_html=True)
with k2:
    st.markdown(f'<div class="kpi kpi-blue"><div class="kpi-label">Total Balance</div><div class="kpi-value">${total_balance:,.0f}</div><div class="kpi-sub">starting $500K</div></div>', unsafe_allow_html=True)
with k3:
    st.markdown(f'<div class="kpi kpi-green"><div class="kpi-label">Safe</div><div class="kpi-value">{safe_count}</div><div class="kpi-sub">on track</div></div>', unsafe_allow_html=True)
with k4:
    st.markdown(f'<div class="kpi kpi-yellow"><div class="kpi-label">Watch</div><div class="kpi-value">{watch_count}</div><div class="kpi-sub">needs attention</div></div>', unsafe_allow_html=True)
with k5:
    st.markdown(f'<div class="kpi kpi-red"><div class="kpi-label">Danger</div><div class="kpi-value">{danger_count}</div><div class="kpi-sub">at risk</div></div>', unsafe_allow_html=True)
with k6:
    st.markdown(f'<div class="kpi kpi-purple"><div class="kpi-label">Payout Ready</div><div class="kpi-value">{payout_ready}</div><div class="kpi-sub">eligible now</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# TABS
# ──────────────────────────────────────────────
tab_overview, tab_payout, tab_consistency, tab_accounts, tab_charts = st.tabs(
    ["Overview", "Payout Tracker", "Consistency", "Account Details", "Analytics"])


# ═══════════════════════════════════════════════
# TAB 1: OVERVIEW
# ═══════════════════════════════════════════════
with tab_overview:
    # Alerts
    alerts = []
    for a in accounts:
        cid = a["account_id"].replace("PA-APEX-433540-", "PA-")
        if a["profit_total"] > 0 and a["_consistency"] > 30:
            alerts.append(("red", f"CONSISTENCY {cid} — {a['_consistency']:.1f}% (limit 30%)"))
        elif a["profit_total"] > 0 and a["_consistency"] > 25:
            alerts.append(("yellow", f"CONSISTENCY {cid} — {a['_consistency']:.1f}% approaching limit"))
        if a["_dd_usage_pct"] > 90:
            alerts.append(("red", f"DRAWDOWN {cid} — {a['_dd_usage_pct']:.0f}% used. STOP TRADING."))
        elif a["_dd_usage_pct"] > 75:
            alerts.append(("red", f"DRAWDOWN {cid} — {a['_dd_usage_pct']:.0f}% used"))
        if a["profit_total"] < -500:
            alerts.append(("red", f"LOSS {cid} — P&L ${a['profit_total']:+,.0f}"))
        if a["_all_passed"]:
            alerts.append(("green", f"PAYOUT READY {cid} — All rules passed"))
        elif 0 < a["_to_payout"] <= 500 and a["profit_total"] > 0:
            alerts.append(("green", f"CLOSE TO PAYOUT {cid} — ${a['_to_payout']:,.0f} away"))

    if alerts:
        for kind, msg in alerts:
            icon = {"red": "&#9888;", "yellow": "&#9888;", "green": "&#10003;"}.get(kind, "")
            st.markdown(f'<div class="alert alert-{kind}">{icon} {msg}</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

    # Overview grid - 2 columns of account cards
    sorted_overview = sorted(accounts, key=lambda x: {"DANGER": 0, "WATCH": 1, "SAFE": 2}[x["_status"]])

    col_left, col_right = st.columns(2)
    for idx, a in enumerate(sorted_overview):
        sid = a["account_id"].replace("PA-APEX-433540-", "PA-")
        status = a["_status"]
        pnl = a["profit_total"]
        bal = a["balance"]
        dd = a["_dd_usage_pct"]
        cons = a["_consistency"]
        to_pay = a["_to_payout"]
        days = a["days_traded"]
        fifty = a["_fifty_days"]

        status_colors = {"SAFE": "#4ade80", "WATCH": "#facc15", "DANGER": "#f87171"}
        sc = status_colors[status]
        pnl_c = "#4ade80" if pnl >= 0 else "#f87171"
        dd_c = "#f87171" if dd > 85 else "#facc15" if dd > 65 else "#4ade80"
        cons_c = "#f87171" if cons > 30 and pnl > 0 else "#facc15" if cons > 25 and pnl > 0 else "#4ade80"

        # DD bar width
        dd_w = min(dd, 100)
        # Payout info
        if to_pay <= 0:
            pay_text = f'<span style="color:#4ade80;font-weight:700;">PAYOUT READY</span>'
        elif to_pay <= 500 and pnl > 0:
            pay_text = f'<span style="color:#60a5fa;">${to_pay:,.0f} to payout</span>'
        else:
            pay_text = f'<span style="color:#475569;">${to_pay:,.0f} to payout</span>'

        # Mini sparkline bars (last 10 days)
        last_days = a["daily_pnl"][:10]
        spark = ""
        if last_days:
            max_abs = max(abs(v) for v in last_days) or 1
            for v in last_days:
                h = max(int(abs(v) / max_abs * 24), 2)
                bc = "#4ade80" if v >= 0 else "#f87171"
                spark += f'<div style="width:4px;height:{h}px;background:{bc};border-radius:1px;"></div>'
            spark = f'<div style="display:flex;gap:2px;align-items:end;height:26px;">{spark}</div>'

        card_html = f"""
        <div style="background:linear-gradient(135deg,#0f172a,#1e293b);border:1px solid rgba(51,65,85,0.5);
            border-radius:14px;padding:16px 20px;margin-bottom:12px;border-left:4px solid {sc};
            transition:border-color 0.2s;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
                <div style="display:flex;align-items:center;gap:10px;">
                    <span style="color:#e2e8f0;font-weight:800;font-size:1rem;">{sid}</span>
                    {badge(status)}
                </div>
                <div style="color:{pnl_c};font-weight:800;font-size:1.2rem;">${pnl:+,.0f}</div>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                <span style="color:#94a3b8;font-size:0.8rem;">Balance: <b style="color:#e2e8f0">${bal:,.0f}</b></span>
                <span style="color:#94a3b8;font-size:0.8rem;">Days: <b style="color:#e2e8f0">{days}/{a["min_days_required"]}</b></span>
                <span style="color:#94a3b8;font-size:0.8rem;">$50+: <b style="color:#e2e8f0">{fifty}/5</b></span>
            </div>
            <div style="display:flex;gap:16px;align-items:center;margin-bottom:8px;">
                <div style="flex:1;">
                    <div style="display:flex;justify-content:space-between;margin-bottom:3px;">
                        <span style="color:#64748b;font-size:0.7rem;font-weight:600;">DRAWDOWN</span>
                        <span style="color:{dd_c};font-size:0.75rem;font-weight:700;">{dd:.0f}%</span>
                    </div>
                    <div style="height:6px;background:#1e293b;border-radius:3px;overflow:hidden;">
                        <div style="height:100%;width:{dd_w}%;background:{dd_c};border-radius:3px;"></div>
                    </div>
                </div>
                <div style="flex:0.6;">
                    <div style="display:flex;justify-content:space-between;margin-bottom:3px;">
                        <span style="color:#64748b;font-size:0.7rem;font-weight:600;">CONSISTENCY</span>
                        <span style="color:{cons_c};font-size:0.75rem;font-weight:700;">{cons:.1f}%</span>
                    </div>
                    <div style="height:6px;background:#1e293b;border-radius:3px;overflow:hidden;">
                        <div style="height:100%;width:{min(cons / 50 * 100, 100):.0f}%;background:{cons_c};border-radius:3px;"></div>
                    </div>
                </div>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:end;">
                <div>{spark}</div>
                <div style="font-size:0.75rem;">{pay_text}</div>
            </div>
        </div>
        """

        target_col = col_left if idx % 2 == 0 else col_right
        with target_col:
            st.markdown(card_html, unsafe_allow_html=True)


# ═══════════════════════════════════════════════
# TAB 2: PAYOUT TRACKER
# ═══════════════════════════════════════════════
with tab_payout:
    st.markdown('<div class="section-header"><span>&#127919;</span> Payout Progress</div>', unsafe_allow_html=True)
    st.caption("Track each account's progress toward the 4 payout requirements")
    st.markdown("<br>", unsafe_allow_html=True)

    # Sort accounts: closest to payout first
    sorted_accts = sorted(accounts, key=lambda a: sum(a["_rules"].values()), reverse=True)

    for a in sorted_accts:
        sid = a["account_id"].replace("PA-APEX-433540-", "PA-")
        rules_passed = sum(a["_rules"].values())
        r = a["_rules"]

        # Rule progress values
        profit_target = a["min_payout_balance"] - a["starting_balance"]
        profit_pct = min((a["profit_total"] / profit_target * 100) if profit_target > 0 and a["profit_total"] > 0 else 0, 100)
        days_pct = min(a["days_traded"] / a["min_days_required"] * 100, 100)
        fifty_pct = min(a["_fifty_days"] / 5 * 100, 100)
        cons_pct = 100 if (a["_consistency"] <= 30 or a["profit_total"] <= 0) else max(0, (30 / a["_consistency"]) * 100)

        all_pass = rules_passed == 4
        border_color = "#22c55e" if all_pass else "rgba(51,65,85,0.5)"
        glow = "box-shadow: 0 0 20px rgba(34,197,94,0.15);" if all_pass else ""
        ready_html = " &#10003; PAYOUT READY" if all_pass else ""

        # Build each rule row
        def rule_row(passed, label, pct, color_pass, color_fail, val_text):
            cls = "payout-pass" if passed else "payout-fail"
            icon = "&#10003;" if passed else "&#10007;"
            bar_color = color_pass if passed else color_fail
            return (
                '<div class="payout-rule">'
                f'<span style="width:16px;" class="{cls}">{icon}</span>'
                f'<span style="color:#94a3b8; width:140px; font-weight:600;">{label}</span>'
                f'<div class="payout-bar-bg"><div class="payout-bar-fill" style="width:{pct:.0f}%;background:{bar_color};"></div></div>'
                f'<span style="color:#e2e8f0; width:100px; text-align:right; font-weight:600;">{val_text}</span>'
                '</div>'
            )

        profit_val = f"${a['profit_total']:+,.0f} / ${profit_target:,.0f}"
        days_val = f"{a['days_traded']} / {a['min_days_required']}"
        fifty_val = f"{a['_fifty_days']} / 5"
        cons_val = f"{a['_consistency']:.1f}% / 30%"

        row1 = rule_row(r["profit_target"], "Profit Target", profit_pct, "#4ade80", "#3b82f6", profit_val)
        row2 = rule_row(r["min_days"], "Min 8 Days", days_pct, "#4ade80", "#eab308", days_val)
        row3 = rule_row(r["fifty_dollar_days"], "5x $50+ Days", fifty_pct, "#4ade80", "#a855f7", fifty_val)
        row4 = rule_row(r["consistency"], "Consistency", cons_pct, "#4ade80", "#f87171", cons_val)

        badge_html = badge(a["_status"])
        card = (
            f'<div class="payout-card" style="border-color:{border_color};{glow}">'
            f'<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">'
            f'<div><span class="payout-acct">{sid}</span> {badge_html}'
            f'<span style="color:#4ade80; font-weight:700; font-size:0.8rem;">{ready_html}</span></div>'
            f'<div style="color:#94a3b8; font-size:0.8rem; font-weight:600;">{rules_passed}/4 rules</div>'
            f'</div>{row1}{row2}{row3}{row4}</div>'
        )
        st.markdown(card, unsafe_allow_html=True)


# ═══════════════════════════════════════════════
# TAB 3: CONSISTENCY CALCULATOR
# ═══════════════════════════════════════════════
with tab_consistency:
    st.markdown('<div class="section-header"><span>&#9878;</span> Consistency Calculator</div>', unsafe_allow_html=True)
    st.caption("Legacy Rule: No single trading day can represent more than 30% of your total profit.")
    st.markdown("<br>", unsafe_allow_html=True)

    cons_rows = []
    for a in accounts:
        profit = a["profit_total"]
        best_day = a.get("best_day_pnl", max([p for p in a["daily_pnl"] if p > 0], default=0))
        sid = a["account_id"].replace("PA-APEX-433540-", "PA-")

        if profit <= 0:
            cons_rows.append({"Account": sid, "Total Profit": profit, "Best Day": best_day,
                              "Best Day %": 0, "Max Today": 0, "Safe Target": 0, "Status": "N/A", "Fix Needed": 0})
            continue

        pct = (best_day / profit) * 100
        max_today = profit * 0.30
        safe = profit * 0.25
        fix = max((best_day / 0.30) - profit, 0)

        if pct > 30:
            status = "VIOLATION"
        elif pct > 25:
            status = "WARNING"
        else:
            status = "OK"

        cons_rows.append({"Account": sid, "Total Profit": profit, "Best Day": best_day,
                          "Best Day %": pct, "Max Today": max_today, "Safe Target": min(safe, 200),
                          "Status": status, "Fix Needed": fix})

    cdf = pd.DataFrame(cons_rows)

    def ccs(v):
        if v == "VIOLATION": return "color: #f87171; font-weight: 700"
        if v == "WARNING": return "color: #facc15; font-weight: 600"
        if v == "OK": return "color: #4ade80; font-weight: 600"
        return "color: #64748b"

    def cbp(v):
        return f"color: {'#f87171' if v > 30 else '#facc15' if v > 25 else '#4ade80'}; font-weight: 600"

    cs2 = (cdf.style.map(ccs, subset=["Status"]).map(cbp, subset=["Best Day %"]).map(cp, subset=["Total Profit"])
           .format({"Total Profit": "${:+,.2f}", "Best Day": "${:,.2f}", "Best Day %": "{:.1f}%",
                    "Max Today": "${:,.0f}", "Safe Target": "${:,.0f}", "Fix Needed": "${:,.0f}"}))

    st.dataframe(cs2, use_container_width=True, hide_index=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # Visual breakdown per account
    st.markdown('<div class="section-header"><span>&#128202;</span> Per-Account Breakdown</div>', unsafe_allow_html=True)
    for a in accounts:
        profit = a["profit_total"]
        if profit <= 0:
            continue
        sid = a["account_id"].replace("PA-APEX-433540-", "PA-")
        best_day = a.get("best_day_pnl", max([p for p in a["daily_pnl"] if p > 0], default=0))
        pct = (best_day / profit) * 100
        max_today = profit * 0.30
        fix = max((best_day / 0.30) - profit, 0)
        days_to_fix = int(fix / 150) + 1 if fix > 0 else 0

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=pct,
            number={"suffix": "%", "font": {"size": 28, "color": "#f1f5f9"}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#475569", "tickfont": {"color": "#64748b"}},
                "bar": {"color": "#f87171" if pct > 30 else "#facc15" if pct > 25 else "#4ade80"},
                "bgcolor": "#1e293b",
                "bordercolor": "#334155",
                "threshold": {"line": {"color": "#ef4444", "width": 3}, "value": 30},
                "steps": [
                    {"range": [0, 25], "color": "rgba(34,197,94,0.1)"},
                    {"range": [25, 30], "color": "rgba(234,179,8,0.1)"},
                    {"range": [30, 100], "color": "rgba(239,68,68,0.1)"}
                ]
            },
            title={"text": f"{sid}", "font": {"size": 16, "color": "#e2e8f0"}},
        ))
        fig.update_layout(height=200, margin=dict(t=40, b=10, l=30, r=30),
                          paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")

        c1, c2 = st.columns([1, 2])
        with c1:
            st.plotly_chart(fig, use_container_width=True, key=f"gauge_{sid}")
        with c2:
            st.markdown(f"**Profit:** ${profit:+,.2f} | **Best Day:** ${best_day:,.2f}")
            if pct > 30:
                st.markdown(f'<div class="alert alert-red">VIOLATION: Best day = {pct:.1f}% of profit. Need ${fix:,.0f} more total profit (~{days_to_fix} days at $150/day).</div>', unsafe_allow_html=True)
            elif pct > 25:
                st.markdown(f'<div class="alert alert-yellow">WARNING: {pct:.1f}% — close to limit. Max today: ${max_today:,.0f}.</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="alert alert-green">OK: {pct:.1f}% — you can earn up to ${max_today:,.0f} today.</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════
# TAB 4: ACCOUNT DETAILS
# ═══════════════════════════════════════════════
with tab_accounts:
    filter_status = st.selectbox("Filter", ["ALL", "SAFE", "WATCH", "DANGER"], label_visibility="collapsed")
    filtered = accounts if filter_status == "ALL" else [a for a in accounts if a["_status"] == filter_status]

    for a in filtered:
        status = a["_status"]
        card_css = f"acct-card acct-card-{status.lower()}"
        sid = a["account_id"].replace("PA-APEX-433540-", "PA-")

        st.markdown(f'<div class="{card_css}">', unsafe_allow_html=True)

        c1, c2, c3, c4, c5 = st.columns([1.8, 1.2, 1.2, 1.2, 2.6])
        with c1:
            st.markdown(f"**{sid}** &nbsp; {badge(status)}", unsafe_allow_html=True)
            st.caption(f"{a['size']} | Since {a.get('purchase_date', '—')}")
        with c2:
            st.metric("Balance", f"${a['balance']:,.2f}", f"${a['profit_total']:+,.2f}")
        with c3:
            st.metric("Days", f"{a['days_traded']}", f"/{a['min_days_required']} req", delta_color="off")
        with c4:
            d = "PASS" if a["_consistency"] <= 30 or a["profit_total"] <= 0 else "FAIL"
            st.metric("Consistency", f"{a['_consistency']:.1f}%", d, delta_color="normal" if d == "PASS" else "inverse")
        with c5:
            st.markdown("**Daily P&L**")
            st.markdown(render_mini_pnl(a["daily_pnl"]), unsafe_allow_html=True)

        # Rules checklist
        r = a["_rules"]
        rc1, rc2, rc3, rc4 = st.columns(4)
        checks = [
            (r["profit_target"], f"Profit Target (${a['min_payout_balance']:,.0f})"),
            (r["min_days"], f"Min {a['min_days_required']} Days ({a['days_traded']})"),
            (r["fifty_dollar_days"], f"5x $50+ Days ({a['_fifty_days']})"),
            (r["consistency"], f"Consistency ({a['_consistency']:.1f}%)"),
        ]
        for col, (passed, label) in zip([rc1, rc2, rc3, rc4], checks):
            cls = "check-pass" if passed else "check-fail"
            icon = "&#10003;" if passed else "&#10007;"
            with col:
                st.markdown(f'<span class="{cls}">{icon} {label}</span>', unsafe_allow_html=True)

        # Progress bars
        pc1, pc2, pc3 = st.columns(3)
        with pc1:
            st.caption(f"Drawdown: {a['_dd_usage_pct']:.0f}% | Stop ${a['stop_price']:,.0f}")
            st.progress(min(a["_dd_usage_pct"] / 100, 1.0))
        with pc2:
            st.caption(f"Days: {a['days_traded']}/{a['min_days_required']}")
            st.progress(min(a["days_traded"] / a["min_days_required"], 1.0))
        with pc3:
            target = a["min_payout_balance"] - a["starting_balance"]
            if a["profit_total"] > 0 and target > 0:
                st.caption(f"Profit: ${a['profit_total']:,.0f} / ${target:,.0f}")
                st.progress(min(a["profit_total"] / target, 1.0))
            else:
                st.caption(f"Profit: ${a['profit_total']:+,.0f}")
                st.progress(0.0)

        st.markdown("</div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════
# TAB 5: ANALYTICS
# ═══════════════════════════════════════════════
with tab_charts:
    # --- Row 1: P&L and Drawdown ---
    ch1, ch2 = st.columns(2)

    acct_names = [a["account_id"].replace("PA-APEX-433540-", "PA-") for a in accounts]

    with ch1:
        pnls = [a["profit_total"] for a in accounts]
        colors = ["#4ade80" if p >= 0 else "#f87171" for p in pnls]

        fig1 = go.Figure(go.Bar(x=acct_names, y=pnls, marker_color=colors,
                                text=[f"${p:+,.0f}" for p in pnls], textposition="outside",
                                textfont=dict(size=10, color="#94a3b8")))
        fig1.update_layout(title="P&L by Account", title_font=dict(size=15, color="#e2e8f0"),
                           paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           xaxis=dict(tickfont=dict(color="#94a3b8", size=10), gridcolor="#1e293b"),
                           yaxis=dict(tickfont=dict(color="#94a3b8"), gridcolor="#1e293b", tickprefix="$"),
                           height=320, margin=dict(t=50, b=30))
        st.plotly_chart(fig1, use_container_width=True)

    with ch2:
        dd_vals = [a["_dd_usage_pct"] for a in accounts]
        dd_colors = ["#f87171" if d > 85 else "#facc15" if d > 65 else "#4ade80" for d in dd_vals]

        fig2 = go.Figure(go.Bar(x=acct_names, y=dd_vals, marker_color=dd_colors,
                                text=[f"{d:.0f}%" for d in dd_vals], textposition="outside",
                                textfont=dict(size=10, color="#94a3b8")))
        fig2.add_hline(y=85, line_dash="dash", line_color="#ef4444", annotation_text="Danger 85%",
                       annotation_font_color="#f87171")
        fig2.update_layout(title="Drawdown Usage %", title_font=dict(size=15, color="#e2e8f0"),
                           paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           xaxis=dict(tickfont=dict(color="#94a3b8", size=10), gridcolor="#1e293b"),
                           yaxis=dict(tickfont=dict(color="#94a3b8"), gridcolor="#1e293b", range=[0, 110], ticksuffix="%"),
                           height=320, margin=dict(t=50, b=30))
        st.plotly_chart(fig2, use_container_width=True)

    # --- Row 2: All Equity Curves overlaid ---
    st.markdown('<div class="section-header"><span>&#128200;</span> Equity Curves — All Accounts</div>', unsafe_allow_html=True)

    fig_eq = go.Figure()
    palette = ["#4ade80", "#60a5fa", "#f87171", "#facc15", "#a855f7",
               "#fb923c", "#2dd4bf", "#f472b6", "#818cf8", "#94a3b8"]

    for i, a in enumerate(accounts):
        sid = a["account_id"].replace("PA-APEX-433540-", "PA-")
        if not a["daily_pnl"]:
            continue
        cum_pnl = []
        running = 0
        for p in reversed(a["daily_pnl"]):
            running += p
            cum_pnl.append(running)
        color = palette[i % len(palette)]
        fig_eq.add_trace(go.Scatter(
            y=cum_pnl, mode="lines", name=sid,
            line=dict(color=color, width=2),
            hovertemplate=f"{sid}<br>Day %{{x}}<br>${{y:,.0f}}<extra></extra>"))

    fig_eq.add_hline(y=0, line_dash="dot", line_color="#475569")
    fig_eq.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(title="Trading Day", tickfont=dict(color="#94a3b8"), gridcolor="rgba(30,41,59,0.5)"),
        yaxis=dict(title="Cumulative P&L", tickfont=dict(color="#94a3b8"), gridcolor="rgba(30,41,59,0.5)", tickprefix="$"),
        legend=dict(font=dict(color="#94a3b8", size=10), bgcolor="rgba(0,0,0,0)",
                    orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        height=400, margin=dict(t=30, b=50))
    st.plotly_chart(fig_eq, use_container_width=True)

    # --- Row 3: Heatmap + Radar ---
    hm_col, radar_col = st.columns(2)

    with hm_col:
        st.markdown('<div class="section-header"><span>&#127777;</span> Daily P&L Heatmap</div>', unsafe_allow_html=True)

        # Build heatmap matrix (accounts x days)
        max_days = max(len(a["daily_pnl"]) for a in accounts) if accounts else 0
        hm_data = []
        hm_labels = []
        for a in accounts:
            sid = a["account_id"].replace("PA-APEX-433540-", "PA-")
            hm_labels.append(sid)
            pnl_reversed = list(reversed(a["daily_pnl"]))
            padded = pnl_reversed + [None] * (max_days - len(pnl_reversed))
            hm_data.append(padded)

        fig_hm = go.Figure(go.Heatmap(
            z=hm_data, y=hm_labels,
            x=[f"Day {i+1}" for i in range(max_days)],
            colorscale=[[0, "#dc2626"], [0.35, "#991b1b"], [0.5, "#1e293b"], [0.65, "#166534"], [1, "#22c55e"]],
            zmid=0, zmin=-500, zmax=500,
            hovertemplate="%{y}<br>%{x}<br>$%{z:+,.0f}<extra></extra>",
            colorbar=dict(title=dict(text="P&L", font=dict(color="#94a3b8")), tickprefix="$", tickfont=dict(color="#94a3b8")),
        ))
        fig_hm.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(tickfont=dict(color="#94a3b8", size=8), gridcolor="#1e293b",
                       showgrid=False, dtick=5),
            yaxis=dict(tickfont=dict(color="#94a3b8", size=10), gridcolor="#1e293b",
                       autorange="reversed"),
            height=380, margin=dict(t=10, b=30, l=60))
        st.plotly_chart(fig_hm, use_container_width=True)

    with radar_col:
        st.markdown('<div class="section-header"><span>&#128301;</span> Account Comparison</div>', unsafe_allow_html=True)

        # Radar chart for top 5 accounts by profit
        top_accts = sorted([a for a in accounts if a["profit_total"] > 0],
                           key=lambda x: x["profit_total"], reverse=True)[:5]

        if top_accts:
            categories = ["Profit", "Days", "$50+ Days", "Consistency", "DD Safety"]
            fig_radar = go.Figure()

            for i, a in enumerate(top_accts):
                sid = a["account_id"].replace("PA-APEX-433540-", "PA-")
                profit_norm = min(a["profit_total"] / 2600 * 100, 100)
                days_norm = min(a["days_traded"] / a["min_days_required"] * 100, 100)
                fifty_norm = min(a["_fifty_days"] / 5 * 100, 100)
                cons_norm = max(0, (30 - a["_consistency"]) / 30 * 100) if a["profit_total"] > 0 else 100
                dd_safety = max(0, 100 - a["_dd_usage_pct"])

                vals = [profit_norm, days_norm, fifty_norm, cons_norm, dd_safety]
                vals.append(vals[0])  # close the polygon

                fig_radar.add_trace(go.Scatterpolar(
                    r=vals, theta=categories + [categories[0]],
                    fill="toself", name=sid,
                    line=dict(color=palette[i], width=2),
                    fillcolor="rgba({},{},{},0.1)".format(*[int(palette[i].lstrip('#')[j:j+2], 16) for j in (0, 2, 4)]),
                ))

            fig_radar.update_layout(
                polar=dict(
                    bgcolor="rgba(0,0,0,0)",
                    radialaxis=dict(visible=True, range=[0, 100], gridcolor="#1e293b",
                                    tickfont=dict(color="#475569", size=8)),
                    angularaxis=dict(gridcolor="#1e293b", tickfont=dict(color="#94a3b8", size=10)),
                ),
                paper_bgcolor="rgba(0,0,0,0)",
                legend=dict(font=dict(color="#94a3b8", size=10), bgcolor="rgba(0,0,0,0)"),
                height=380, margin=dict(t=30, b=30))
            st.plotly_chart(fig_radar, use_container_width=True)
        else:
            st.info("No profitable accounts to compare yet.")

    # --- Row 4: Distribution + Stats ---
    st.markdown('<div class="section-header"><span>&#128202;</span> P&L Distribution</div>', unsafe_allow_html=True)

    all_pnls = []
    for a in accounts:
        all_pnls.extend(a["daily_pnl"])

    fig4 = go.Figure()
    pos = [p for p in all_pnls if p >= 0]
    neg = [p for p in all_pnls if p < 0]
    fig4.add_trace(go.Histogram(x=pos, name="Wins", marker_color="rgba(74,222,128,0.6)", nbinsx=30))
    fig4.add_trace(go.Histogram(x=neg, name="Losses", marker_color="rgba(248,113,113,0.6)", nbinsx=30))
    fig4.update_layout(barmode="overlay", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                       xaxis=dict(title="Daily P&L ($)", tickfont=dict(color="#94a3b8"), gridcolor="#1e293b"),
                       yaxis=dict(title="Frequency", tickfont=dict(color="#94a3b8"), gridcolor="#1e293b"),
                       legend=dict(font=dict(color="#94a3b8")),
                       height=280, margin=dict(t=20, b=50))
    st.plotly_chart(fig4, use_container_width=True)

    # Portfolio Stats
    st.markdown('<div class="section-header"><span>&#128640;</span> Portfolio Statistics</div>', unsafe_allow_html=True)
    sc1, sc2, sc3, sc4, sc5, sc6 = st.columns(6)
    with sc1:
        win_rate = len(pos) / len(all_pnls) * 100 if all_pnls else 0
        st.markdown(f'<div class="kpi kpi-green"><div class="kpi-label">Win Rate</div><div class="kpi-value">{win_rate:.1f}%</div></div>', unsafe_allow_html=True)
    with sc2:
        avg_win = sum(pos) / len(pos) if pos else 0
        st.markdown(f'<div class="kpi kpi-green"><div class="kpi-label">Avg Win</div><div class="kpi-value">${avg_win:,.0f}</div></div>', unsafe_allow_html=True)
    with sc3:
        avg_loss = sum(neg) / len(neg) if neg else 0
        st.markdown(f'<div class="kpi kpi-red"><div class="kpi-label">Avg Loss</div><div class="kpi-value">${avg_loss:,.0f}</div></div>', unsafe_allow_html=True)
    with sc4:
        pf = abs(sum(pos) / sum(neg)) if neg and sum(neg) != 0 else 0
        pf_css = "kpi-green" if pf >= 1.5 else "kpi-yellow" if pf >= 1 else "kpi-red"
        st.markdown(f'<div class="kpi {pf_css}"><div class="kpi-label">Profit Factor</div><div class="kpi-value">{pf:.2f}</div></div>', unsafe_allow_html=True)
    with sc5:
        st.markdown(f'<div class="kpi kpi-blue"><div class="kpi-label">Total Sessions</div><div class="kpi-value">{len(all_pnls)}</div></div>', unsafe_allow_html=True)
    with sc6:
        max_win = max(all_pnls) if all_pnls else 0
        max_loss = min(all_pnls) if all_pnls else 0
        st.markdown(f'<div class="kpi kpi-purple"><div class="kpi-label">Best / Worst</div><div class="kpi-value" style="font-size:1.1rem;">${max_win:+,.0f}<br>${max_loss:+,.0f}</div></div>', unsafe_allow_html=True)


# ──────────────────────────────────────────────
# FOOTER
# ──────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="text-align:center; padding: 8px 0;">
    <span style="color:#64748b; font-size:0.75rem;">
        Ronald Rodriguez | Apex Trader Funding Legacy PA Monitor | Personal Portfolio |
        <span style="color:#818cf8;">Powered by Streamlit</span>
    </span>
</div>
""", unsafe_allow_html=True)
