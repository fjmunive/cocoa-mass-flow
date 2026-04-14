"""
Cocoa Mass Flow Simulator — Streamlit app
Deploy free at share.streamlit.io

Local run:
  pip install streamlit plotly
  streamlit run app.py
"""
import streamlit as st
import plotly.graph_objects as go

# ── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="Cocoa Mass Flow Simulator",
    page_icon="🍫",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Colour palette (mirrors original R code) ──────────────────
PAL = {
    "input":     "#6D3B0F",
    "process":   "#8B5E3C",
    "byproduct": "#C49A3C",
    "loss":      "#B85450",
    "product":   "#2E7D32",
}

def rgba(hex_col, a=0.42):
    h = hex_col.lstrip("#")
    r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
    return f"rgba({r},{g},{b},{a})"

# ── Sankey builder ────────────────────────────────────────────
def build_sankey(m, variety_name):
    T = m["total"]

    def lbl(name, kg):
        pct = (kg / T * 100) if T > 0 else 0
        return f"{name}<br><b>{kg:.1f} kg</b>  ({pct:.1f}%)"

    labels = [
        lbl("Whole Fruit",              T),               # 0
        lbl("Cacao Husk",               m["husk"]),       # 1
        lbl("Placenta",                 m["placenta"]),   # 2
        lbl("Pod-break Losses",         m["pod_loss"]),   # 3
        lbl("Wet Beans + Pulp",         m["wet"]),        # 4
        lbl("CME Exudate",              m["cme"]),        # 5
        lbl("Fermented Beans",          m["ferm"]),       # 6
        lbl("Drying Water Loss",        m["dry_water"]),  # 7
        lbl("Dried Beans",              m["dried"]),      # 8
        lbl("Roasting Volatile Loss",   m["roast_loss"]), # 9
        lbl("Roasted Beans",            m["roasted"]),    # 10
        lbl("Bean Shell",               m["shell"]),      # 11
        lbl("Winnowing Loss",           m["winnow"]),     # 12
        lbl("COCOA NIBS",               m["nibs"]),       # 13
    ]

    # Manual positions → mirrors R sinksRight=FALSE layout
    # x: processing column (0=input, 1=right edge)
    # y: vertical centre of node (0=top, 1=bottom)
    node_x = [0.01,  # 0  Whole Fruit
               0.18,  # 1  Cacao Husk
               0.18,  # 2  Placenta
               0.18,  # 3  Pod-break Losses
               0.18,  # 4  Wet Beans + Pulp
               0.42,  # 5  CME Exudate
               0.42,  # 6  Fermented Beans
               0.62,  # 7  Drying Water Loss
               0.62,  # 8  Dried Beans
               0.80,  # 9  Roasting Volatile Loss
               0.80,  # 10 Roasted Beans
               0.97,  # 11 Bean Shell
               0.97,  # 12 Winnowing Loss
               0.97,  # 13 COCOA NIBS
               ]
    node_y = [0.38,   # 0  Whole Fruit
               0.72,  # 1  Cacao Husk   (large, below centre)
               0.90,  # 2  Placenta
               0.96,  # 3  Pod-break Losses
               0.10,  # 4  Wet Beans + Pulp (top)
               0.48,  # 5  CME Exudate
               0.17,  # 6  Fermented Beans
               0.04,  # 7  Drying Water Loss
               0.22,  # 8  Dried Beans
               0.12,  # 9  Roasting Volatile Loss
               0.30,  # 10 Roasted Beans
               0.18,  # 11 Bean Shell
               0.27,  # 12 Winnowing Loss
               0.42,  # 13 COCOA NIBS
               ]

    node_cats = ["input","byproduct","byproduct","loss","process",
                 "byproduct","process","loss","process","loss",
                 "process","byproduct","loss","product"]
    link_cats = ["byproduct","byproduct","loss","process",
                 "byproduct","process","loss","process",
                 "loss","process","byproduct","loss","product"]

    sources = [0,0,0,0,  4,4,  6,6,  8,8,  10,10,10]
    targets = [1,2,3,4,  5,6,  7,8,  9,10, 11,12,13]
    values  = [max(v, 0.001) for v in [       # 0.001 keeps structure when a flow is 0
        m["husk"],      m["placenta"], m["pod_loss"], m["wet"],
        m["cme"],       m["ferm"],
        m["dry_water"], m["dried"],
        m["roast_loss"],m["roasted"],
        m["shell"],     m["winnow"],   m["nibs"],
    ]]

    fig = go.Figure(go.Sankey(
        arrangement="fixed",                   # honours our x/y coordinates
        node=dict(
            pad=18, thickness=22,
            line=dict(color="white", width=0.5),
            label=labels,
            color=[PAL[c] for c in node_cats],
            x=node_x,
            y=node_y,
            hovertemplate="%{label}<extra></extra>",
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=[rgba(PAL[c]) for c in link_cats],
            hovertemplate="<b>%{value:.1f} kg</b><extra></extra>",
        ),
    ))

fig.update_layout(
        title=dict(
            text=(f"<b>Cocoa Mass Flow — {variety_name}</b>"
                  f"<br><sup>Input: {T:.0f} kg whole fruit</sup>"),
            font=dict(size=20, family="Georgia, serif", color="#4E2A04"),
            x=0.5,
        ),
        font=dict(size=12, family="Arial, sans-serif", color="#2C1810"),
        paper_bgcolor="white",
        height=600,
        margin=dict(l=20, r=20, t=110, b=20),
    )
    return fig



# ── Sidebar — kg inputs (farmers weigh directly) ──────────────
with st.sidebar:
    st.markdown(
        '<div style="background:#4E2A04;color:white;padding:10px 14px;'
        'border-radius:6px;font-family:Georgia,serif;font-size:17px;'
        'margin-bottom:12px">🍫 Enter Your Data</div>',
        unsafe_allow_html=True,
    )

    variety = st.selectbox(
        "Cocoa Variety",
        ["CCN-51 (Ecuadorian)",
         "Nacional × Trinitario (Fine Aroma)",
         "Other / Unknown"],
    )

    total_kg = st.number_input(
        "Whole Fruit Input (kg)",
        min_value=0.0, value=0.0, step=10.0,
        help="Total weight of whole cocoa pods before any processing",
    )

    st.markdown("---")
    st.markdown("**Stage 1 — Pod Breaking**")
    st.caption("Weigh each fraction after opening pods")
    wet_kg      = st.number_input("Wet Beans + Pulp (kg)",  0.0, value=0.0, step=1.0)
    husk_kg     = st.number_input("Cacao Husk (kg)",         0.0, value=0.0, step=1.0)
    placenta_kg = st.number_input("Placenta (kg)",           0.0, value=0.0, step=0.5)
    st.caption("Pod-break losses = remainder (auto-computed)")

    st.markdown("**Stage 2 — Fermentation**")
    st.caption("Weigh after fermentation is complete")
    ferm_kg = st.number_input("Fermented Beans (kg)", 0.0, value=0.0, step=1.0)
    st.caption("CME exudate = wet beans − fermented (auto-computed)")

    st.markdown("**Stage 3 — Drying**")
    dried_kg = st.number_input("Dried Beans (kg)", 0.0, value=0.0, step=1.0)
    st.caption("Drying water loss = fermented − dried (auto-computed)")

    st.markdown("**Stage 4 — Roasting**")
    roasted_kg = st.number_input("Roasted Beans (kg)", 0.0, value=0.0, step=0.5)

    st.markdown("**Stage 5 — Winnowing**")
    nibs_kg  = st.number_input("Cocoa Nibs (kg)",  0.0, value=0.0, step=0.5)
    shell_kg = st.number_input("Bean Shell (kg)",  0.0, value=0.0, step=0.5)
    st.caption("Winnowing loss = roasted − nibs − shell (auto-computed)")

# ── Compute derived flows ─────────────────────────────────────
pod_loss   = total_kg  - wet_kg - husk_kg - placenta_kg
cme        = wet_kg    - ferm_kg
dry_water  = ferm_kg   - dried_kg
roast_loss = dried_kg  - roasted_kg
winnow     = roasted_kg - nibs_kg - shell_kg

errors, warns = [], []

def check_negative(val, label):
    if val < -0.05:
        errors.append(f"❌ **{label}** = {val:.1f} kg — outputs exceed inputs at this stage. Check your measurements.")

check_negative(pod_loss,   "Pod-break Losses")
check_negative(cme,        "CME Exudate")
check_negative(dry_water,  "Drying Water Loss")
check_negative(roast_loss, "Roasting Volatile Loss")
check_negative(winnow,     "Winnowing Loss")

tracked_out = (husk_kg + placenta_kg + max(pod_loss, 0) + max(cme, 0) +
               max(dry_water, 0) + max(roast_loss, 0) +
               shell_kg + max(winnow, 0) + nibs_kg)
gap = abs(total_kg - tracked_out)
if total_kg > 0 and gap > total_kg * 0.02:
    warns.append(
        f"⚠ Overall mass balance gap: **{gap:.1f} kg** "
        f"({gap/total_kg*100:.1f}% of input) — review your measurements."
    )

flows = dict(
    total      = total_kg,
    husk       = husk_kg,
    placenta   = placenta_kg,
    pod_loss   = max(pod_loss,   0),
    wet        = wet_kg,
    cme        = max(cme,        0),
    ferm       = ferm_kg,
    dry_water  = max(dry_water,  0),
    dried      = dried_kg,
    roast_loss = max(roast_loss, 0),
    roasted    = roasted_kg,
    shell      = shell_kg,
    winnow     = max(winnow,     0),
    nibs       = nibs_kg,
)

# ── Main panel ────────────────────────────────────────────────
st.markdown(
    '<h1 style="font-family:Georgia,serif;color:#4E2A04;margin-bottom:0">'
    'Cocoa Mass Flow Simulator</h1>'
    '<p style="color:#999;font-size:14px;margin-top:4px">'
    'Enter your processing measurements in the sidebar to visualise mass flows.</p>',
    unsafe_allow_html=True,
)

for e in errors:
    st.error(e, icon="❌")
for w in warns:
    st.warning(w, icon="⚠️")
if not errors and not warns and total_kg > 0:
    st.success("✓ Mass balance OK — all derived flows are positive.", icon="✅")

if total_kg == 0:
    st.info(
        "👈  Start by entering your **Whole Fruit Input (kg)** in the sidebar, "
        "then fill in each stage as you process your batch.",
        icon="ℹ️",
    )
else:
    if not errors:
        fig = build_sankey(flows, variety)
        st.plotly_chart(fig, use_container_width=True)

    # ── Legend ────────────────────────────────────────────────
    cols = st.columns(5)
    legend = [
        ("Raw material",     PAL["input"]),
        ("Process stream",   PAL["process"]),
        ("By-product",       PAL["byproduct"]),
        ("Loss",             PAL["loss"]),
        ("Final product",    PAL["product"]),
    ]
    for col, (label, color) in zip(cols, legend):
        col.markdown(
            f'<div style="display:flex;align-items:center;gap:6px;font-size:12px;color:#555">'
            f'<span style="width:14px;height:14px;background:{color};'
            f'border-radius:3px;display:inline-block;flex-shrink:0"></span>{label}</div>',
            unsafe_allow_html=True,
        )

    # ── Summary table ─────────────────────────────────────────
    st.markdown("---")
    st.markdown("### Mass Flow Summary")
    c1, c2, c3 = st.columns(3)

    def card(col, label, val, color):
        pct = val / total_kg * 100 if total_kg > 0 else 0
        col.markdown(
            f'<div style="background:#FAFAFA;border-left:4px solid {color};'
            f'padding:8px 12px;border-radius:4px;margin:4px 0;">'
            f'<div style="font-size:11px;color:#888;font-family:Arial">{label}</div>'
            f'<div style="font-size:20px;font-weight:bold;color:{color}">{val:.1f} kg</div>'
            f'<div style="font-size:12px;color:#999">{pct:.1f}% of input</div></div>',
            unsafe_allow_html=True,
        )

    with c1:
        st.markdown("**By-products**")
        card(c1, "Cacao Husk",  husk_kg,        PAL["byproduct"])
        card(c1, "Placenta",    placenta_kg,     PAL["byproduct"])
        card(c1, "CME Exudate", flows["cme"],    PAL["byproduct"])
        card(c1, "Bean Shell",  shell_kg,        PAL["byproduct"])
    with c2:
        st.markdown("**Losses**")
        card(c2, "Pod-break Loss",    flows["pod_loss"],   PAL["loss"])
        card(c2, "Drying Water",      flows["dry_water"],  PAL["loss"])
        card(c2, "Roasting Loss",     flows["roast_loss"], PAL["loss"])
        card(c2, "Winnowing Loss",    flows["winnow"],     PAL["loss"])
    with c3:
        st.markdown("**Final Product**")
        card(c3, "COCOA NIBS", nibs_kg, PAL["product"])
        if total_kg > 0:
            yield_pct = nibs_kg / total_kg * 100
            st.markdown(
                f'<div style="margin-top:12px;padding:10px 12px;'
                f'background:#E8F5E9;border-radius:6px;font-family:Arial">'
                f'<div style="font-size:11px;color:#888">Nib yield</div>'
                f'<div style="font-size:28px;font-weight:bold;color:{PAL["product"]}">'
                f'{yield_pct:.2f}%</div>'
                f'<div style="font-size:11px;color:#888">of whole fruit</div></div>',
                unsafe_allow_html=True,
            )

st.markdown("---")
st.markdown(
    '<p style="text-align:center;color:#bbb;font-size:11px">'
    'Cocoa Mass Flow Analysis · Smallholder Tool</p>',
    unsafe_allow_html=True,
)
