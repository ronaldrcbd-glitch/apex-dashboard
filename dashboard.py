import json
import plotly.graph_objects as go
import streamlit as st
import pandas as pd
from datetime import datetime as _dt
from pathlib import Path

DATA_FILE = Path(__file__).parent / "apex_data.json"

st.set_page_config(page_title="Apex PA Monitor", layout="wide", page_icon="📊")

# ──────────────────────────────────────────────
# GLOBAL STYLES
# ──────────────────────────────────────────────
st.markdown("""
<style>
    /* Hide streamlit branding */
    #MainMenu, footer, header {visibility: hidden;}
    .block-container {padding-top: 1.5rem; padding-bottom: 1rem;}

    /* KPI cards */
    .kpi {background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); border: 1px solid #334155;
          border-radius: 12px; padding: 20px 24px; text-align: center; position: relative; overflow: hidden;}
    .kpi::before {content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;}
    .kpi-green::before {background: linear-gradient(90deg, #22c55e, #4ade80);}
    .kpi-yellow::before {background: linear-gradient(90deg, #eab308, #facc15);}
    .kpi-red::before {background: linear-gradient(90deg, #ef4444, #f87171);}
    .kpi-blue::before {background: linear-gradient(90deg, #3b82f6, #60a5fa);}
    .kpi-label {color: #64748b; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 600; margin-bottom: 6px;}
    .kpi-value {color: #f1f5f9; font-size: 1.8rem; font-weight: 800; line-height: 1.1;}
    .kpi-sub {color: #94a3b8; font-size: 0.8rem; margin-top: 4px;}

    /* Badges */
    .badge {padding: 3px 12px; border-radius: 20px; font-weight: 700; font-size: 0.7rem; letter-spacing: 0.5px; display: inline-block;}
    .badge-safe {background: rgba(34,197,94,0.15); color: #4ade80; border: 1px solid rgba(34,197,94,0.3);}
    .badge-watch {background: rgba(234,179,8,0.15); color: #facc15; border: 1px solid rgba(234,179,8,0.3);}
    .badge-danger {background: rgba(239,68,68,0.15); color: #f87171; border: 1px solid rgba(239,68,68,0.3);}

    /* Alert bars */
    .alert {padding: 10px 16px; border-radius: 8px; margin-bottom: 6px; font-size: 0.85rem; border-left: 4px solid;}
    .alert-red {background: rgba(239,68,68,0.08); border-color: #ef4444; color: #fca5a5;}
    .alert-yellow {background: rgba(234,179,8,0.08); border-color: #eab308; color: #fde68a;}
    .alert-green {background: rgba(34,197,94,0.08); border-color: #22c55e; color: #86efac;}

    /* Rules box */
    .rules-box {background: linear-gradient(135deg, #0f172a, #1e293b); border: 1px solid #334155;
                border-radius: 10px; padding: 12px 18px; font-size: 0.8rem; color: #94a3b8;}
    .rules-box b {color: #e2e8f0;}

    /* Account cards */
    .acct-card {background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); border: 1px solid #334155;
                border-radius: 12px; padding: 20px; margin-bottom: 16px; position: relative; overflow: hidden;}
    .acct-card::before {content: ''; position: absolute; top: 0; left: 0; bottom: 0; width: 4px;}
    .acct-card-safe::before {background: #22c55e;}
    .acct-card-watch::before {background: #eab308;}
    .acct-card-danger::before {background: #ef4444;}

    /* Header */
    .dash-header {display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;}
    .dash-title {font-size: 1.6rem; font-weight: 800; color: #f1f5f9; letter-spacing: -0.5px;}
    .dash-subtitle {color: #64748b; font-size: 0.8rem;}

    /* Checklist */
    .check-pass {color: #4ade80; font-weight: 600; font-size: 0.82rem;}
    .check-fail {color: #94a3b8; font-weight: 500; font-size: 0.82rem;}

    /* Mini pnl bars */
    .pnl-bar {height: 20px; border-radius: 3px; margin: 1px 0; min-width: 2px;}

    /* Plotly chart bg */
    .stPlotlyChart {border-radius: 12px; overflow: hidden;}

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {gap: 8px;}
    .stTabs [data-baseweb="tab"] {padding: 8px 20px; border-radius: 8px 8px 0 0;}
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


def badge(status):
    return f'<span class="badge badge-{status.lower()}">{status}</span>'


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


# ──────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("## Apex PA Monitor")
    st.markdown("**Ronald Rodriguez**")
    st.caption("Personal Portfolio | Legacy 50K")
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

    st.markdown(f'Data: <span style="color:{color};font-weight:700">{age}</span>', unsafe_allow_html=True)
    st.caption(last_updated)
    st.markdown("---")
    st.caption("**Refresh:** Open Claude Code and say\n*'actualiza los datos de Apex'*")
    st.markdown("---")
    st.markdown("[Apex Portal](https://dashboard.apextraderfunding.com/member) | [PA Charts](https://dashboard.apextraderfunding.com/AccountSummary/index/pa/acc)")
    st.markdown("---")
    st.markdown("""<div class="rules-box">
    <b>Legacy Rules 50K</b><br>
    Target: $52,600 | 8 Days | 5x $50+ | Consistency 30% | DD $2,500 | 10 Contracts
    </div>""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# HEADER KPIs
# ──────────────────────────────────────────────
pnl_sign = "+" if total_pnl >= 0 else ""
pnl_css = "kpi-green" if total_pnl >= 0 else "kpi-red"

k1, k2, k3, k4, k5, k6 = st.columns(6)
with k1:
    st.markdown(f'<div class="kpi {pnl_css}"><div class="kpi-label">Total P&L</div><div class="kpi-value">{pnl_sign}${total_pnl:,.0f}</div><div class="kpi-sub">across {len(accounts)} accounts</div></div>', unsafe_allow_html=True)
with k2:
    st.markdown(f'<div class="kpi kpi-blue"><div class="kpi-label">Total Balance</div><div class="kpi-value">${total_balance:,.0f}</div><div class="kpi-sub">starting $500K</div></div>', unsafe_allow_html=True)
with k3:
    st.markdown(f'<div class="kpi kpi-green"><div class="kpi-label">Safe</div><div class="kpi-value">{safe_count}</div><div class="kpi-sub">accounts on track</div></div>', unsafe_allow_html=True)
with k4:
    st.markdown(f'<div class="kpi kpi-yellow"><div class="kpi-label">Watch</div><div class="kpi-value">{watch_count}</div><div class="kpi-sub">needs attention</div></div>', unsafe_allow_html=True)
with k5:
    st.markdown(f'<div class="kpi kpi-red"><div class="kpi-label">Danger</div><div class="kpi-value">{danger_count}</div><div class="kpi-sub">at risk</div></div>', unsafe_allow_html=True)
with k6:
    st.markdown(f'<div class="kpi kpi-green"><div class="kpi-label">Payout Ready</div><div class="kpi-value">{payout_ready}</div><div class="kpi-sub">eligible now</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# TABS
# ──────────────────────────────────────────────
tab_overview, tab_consistency, tab_accounts, tab_charts = st.tabs(["Overview", "Consistency Calculator", "Account Details", "Analytics"])


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
            alerts.append(("green", f"PAYOUT READY {cid}"))
        if 0 < a["_to_payout"] <= 500 and a["profit_total"] > 0:
            alerts.append(("green", f"CLOSE TO PAYOUT {cid} — ${a['_to_payout']:,.0f} away"))

    if alerts:
        for kind, msg in alerts:
            st.markdown(f'<div class="alert alert-{kind}">{msg}</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

    # Main table
    rows = []
    for a in accounts:
        rows.append({
            "Account": a["account_id"].replace("PA-APEX-433540-", "PA-"),
            "Balance": a["balance"],
            "P&L": a["profit_total"],
            "To Payout": a["_to_payout"],
            "Days": a["days_traded"],
            "$50+ Days": f"{a['_fifty_days']}/5",
            "Consistency": a["_consistency"],
            "DD Used %": a["_dd_usage_pct"],
            "Stop": a["stop_price"],
            "Status": a["_status"],
        })
    df = pd.DataFrame(rows)

    def cs(v):
        colors = {"SAFE": "#4ade80", "WATCH": "#facc15", "DANGER": "#f87171"}
        return f"color: {colors.get(v, '#fff')}; font-weight: 700"
    def cp(v):
        c = "#4ade80" if v >= 0 else "#f87171"
        return f"color: {c}; font-weight: 600"
    def cc(v):
        c = "#f87171" if v > 30 else "#facc15" if v > 25 else "#4ade80"
        return f"color: {c}"
    def cd(v):
        c = "#f87171" if v > 85 else "#facc15" if v > 65 else "#4ade80"
        return f"color: {c}"
    def ctp(v):
        c = "#4ade80" if v <= 0 else "#60a5fa" if v <= 500 else "#64748b"
        return f"color: {c}"

    styled = (df.style.map(cs, subset=["Status"]).map(cp, subset=["P&L"])
              .map(cc, subset=["Consistency"]).map(cd, subset=["DD Used %"]).map(ctp, subset=["To Payout"])
              .format({"Balance": "${:,.2f}", "P&L": "${:+,.2f}", "To Payout": "${:,.0f}",
                       "Consistency": "{:.1f}%", "DD Used %": "{:.0f}%", "Stop": "${:,.0f}"}))

    st.dataframe(styled, use_container_width=True, height=420, hide_index=True)


# ═══════════════════════════════════════════════
# TAB 2: CONSISTENCY CALCULATOR
# ═══════════════════════════════════════════════
with tab_consistency:
    st.markdown("#### How it works")
    st.caption("Legacy Rule: No single trading day can represent more than 30% of your total profit. If your best day exceeds 30%, you need to accumulate more small wins to dilute it below the threshold.")
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
    st.markdown("#### Per-Account Breakdown")
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

        # Gauge chart
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
# TAB 3: ACCOUNT DETAILS
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
# TAB 4: ANALYTICS
# ═══════════════════════════════════════════════
with tab_charts:
    ch1, ch2 = st.columns(2)

    with ch1:
        # P&L by account bar chart
        acct_names = [a["account_id"].replace("PA-APEX-433540-", "PA-") for a in accounts]
        pnls = [a["profit_total"] for a in accounts]
        colors = ["#4ade80" if p >= 0 else "#f87171" for p in pnls]

        fig1 = go.Figure(go.Bar(x=acct_names, y=pnls, marker_color=colors,
                                text=[f"${p:+,.0f}" for p in pnls], textposition="outside",
                                textfont=dict(size=11, color="#94a3b8")))
        fig1.update_layout(title="P&L by Account", title_font=dict(size=16, color="#e2e8f0"),
                           paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           xaxis=dict(tickfont=dict(color="#94a3b8"), gridcolor="#1e293b"),
                           yaxis=dict(tickfont=dict(color="#94a3b8"), gridcolor="#1e293b", tickprefix="$"),
                           height=350, margin=dict(t=50, b=30))
        st.plotly_chart(fig1, use_container_width=True)

    with ch2:
        # Drawdown usage bar chart
        dd_vals = [a["_dd_usage_pct"] for a in accounts]
        dd_colors = ["#f87171" if d > 85 else "#facc15" if d > 65 else "#4ade80" for d in dd_vals]

        fig2 = go.Figure(go.Bar(x=acct_names, y=dd_vals, marker_color=dd_colors,
                                text=[f"{d:.0f}%" for d in dd_vals], textposition="outside",
                                textfont=dict(size=11, color="#94a3b8")))
        fig2.add_hline(y=85, line_dash="dash", line_color="#ef4444", annotation_text="Danger 85%",
                       annotation_font_color="#f87171")
        fig2.update_layout(title="Drawdown Usage %", title_font=dict(size=16, color="#e2e8f0"),
                           paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           xaxis=dict(tickfont=dict(color="#94a3b8"), gridcolor="#1e293b"),
                           yaxis=dict(tickfont=dict(color="#94a3b8"), gridcolor="#1e293b", range=[0, 110], ticksuffix="%"),
                           height=350, margin=dict(t=50, b=30))
        st.plotly_chart(fig2, use_container_width=True)

    # Portfolio equity curve (cumulative P&L of best account)
    best_acct = max(accounts, key=lambda a: a["profit_total"])
    best_sid = best_acct["account_id"].replace("PA-APEX-433540-", "PA-")
    cum_pnl = []
    running = 0
    for p in reversed(best_acct["daily_pnl"]):
        running += p
        cum_pnl.append(running)

    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(y=cum_pnl, mode="lines+markers",
                              line=dict(color="#4ade80", width=2),
                              marker=dict(size=4, color=["#4ade80" if p >= 0 else "#f87171" for p in reversed(best_acct["daily_pnl"])]),
                              fill="tozeroy", fillcolor="rgba(74,222,128,0.05)",
                              hovertemplate="Day %{x}<br>Cumulative: $%{y:,.2f}<extra></extra>"))
    fig3.update_layout(title=f"Equity Curve — {best_sid} (Top Account)", title_font=dict(size=16, color="#e2e8f0"),
                       paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                       xaxis=dict(title="Trading Day", tickfont=dict(color="#94a3b8"), gridcolor="#1e293b"),
                       yaxis=dict(title="Cumulative P&L", tickfont=dict(color="#94a3b8"), gridcolor="#1e293b", tickprefix="$"),
                       height=350, margin=dict(t=50, b=50))
    st.plotly_chart(fig3, use_container_width=True)

    # P&L distribution
    all_pnls = []
    for a in accounts:
        all_pnls.extend(a["daily_pnl"])

    fig4 = go.Figure()
    pos = [p for p in all_pnls if p >= 0]
    neg = [p for p in all_pnls if p < 0]
    fig4.add_trace(go.Histogram(x=pos, name="Wins", marker_color="rgba(74,222,128,0.6)", nbinsx=30))
    fig4.add_trace(go.Histogram(x=neg, name="Losses", marker_color="rgba(248,113,113,0.6)", nbinsx=30))
    fig4.update_layout(title="P&L Distribution (All Accounts)", title_font=dict(size=16, color="#e2e8f0"),
                       barmode="overlay", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                       xaxis=dict(title="Daily P&L ($)", tickfont=dict(color="#94a3b8"), gridcolor="#1e293b"),
                       yaxis=dict(title="Frequency", tickfont=dict(color="#94a3b8"), gridcolor="#1e293b"),
                       legend=dict(font=dict(color="#94a3b8")),
                       height=300, margin=dict(t=50, b=50))
    st.plotly_chart(fig4, use_container_width=True)

    # Summary stats
    st.markdown("#### Portfolio Stats")
    sc1, sc2, sc3, sc4, sc5 = st.columns(5)
    with sc1:
        win_rate = len(pos) / len(all_pnls) * 100 if all_pnls else 0
        st.metric("Win Rate", f"{win_rate:.1f}%")
    with sc2:
        avg_win = sum(pos) / len(pos) if pos else 0
        st.metric("Avg Win", f"${avg_win:,.2f}")
    with sc3:
        avg_loss = sum(neg) / len(neg) if neg else 0
        st.metric("Avg Loss", f"${avg_loss:,.2f}")
    with sc4:
        pf = abs(sum(pos) / sum(neg)) if neg and sum(neg) != 0 else 0
        st.metric("Profit Factor", f"{pf:.2f}")
    with sc5:
        st.metric("Total Trades", f"{len(all_pnls)}")


# ──────────────────────────────────────────────
# FOOTER
# ──────────────────────────────────────────────
st.markdown("---")
st.caption("Ronald Rodriguez | Apex Trader Funding Legacy PA Monitor | Personal Portfolio")
