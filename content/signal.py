"""
Loads public-data CSVs in content/data/ and builds Plotly trace
dictionaries for the Signal section. Dark theme, amber accent.
"""

import csv
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

TEMPLATE = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font": {"family": "Inter, system-ui, sans-serif", "color": "#CBD5E1", "size": 13},
    "margin": {"l": 60, "r": 20, "t": 30, "b": 60},
    "xaxis": {"gridcolor": "#334155", "linecolor": "#334155", "zerolinecolor": "#334155"},
    "yaxis": {"gridcolor": "#334155", "linecolor": "#334155", "zerolinecolor": "#334155"},
}

AMBER = "#F59E0B"
AMBER_SCALE = [
    [0.0, "#0F172A"],
    [0.25, "#78350F"],
    [0.55, "#D97706"],
    [0.8, "#FBBF24"],
    [1.0, "#F59E0B"],
]


def _read(name):
    with open(DATA_DIR / name, newline="") as f:
        return list(csv.DictReader(f))


def _layout(title):
    return {**TEMPLATE, "title": {"text": title, "font": {"color": "#F8FAFC", "size": 15}, "x": 0.02}}


def nhs_charts():
    rows = _read("nhs_rtt.csv")
    specialties = [r["specialty"] for r in rows]
    waiting = [int(r["waiting_list"]) for r in rows]
    over_52 = [int(r["over_18_weeks"]) for r in rows]
    median = [float(r["median_weeks"]) for r in rows]

    treemap = {
        "data": [
            {
                "type": "treemap",
                "labels": specialties,
                "parents": [""] * len(specialties),
                "values": waiting,
                "textinfo": "label+value",
                "marker": {
                    "colors": median,
                    "colorscale": AMBER_SCALE,
                    "showscale": True,
                    "colorbar": {"title": "Median weeks", "tickfont": {"color": "#9CA3AF"}},
                    "line": {"color": "#0A0B0D", "width": 1},
                },
                "hovertemplate": "<b>%{label}</b><br>Waiting list: %{value:,.0f}<br>Median weeks: %{color:.1f}<extra></extra>",
            }
        ],
        "layout": _layout("NHS England waiting list by specialty"),
    }

    heatmap = {
        "data": [
            {
                "type": "bar",
                "x": specialties,
                "y": over_52,
                "marker": {"color": AMBER},
                "hovertemplate": "<b>%{x}</b><br>Waits > 18 weeks: %{y:,.0f}<extra></extra>",
            }
        ],
        "layout": _layout("Patients waiting over 18 weeks, by specialty"),
    }
    return treemap, heatmap


def dfe_charts():
    rows = _read("dfe_ks4.csv")
    regions = [r["region"] for r in rows]
    groups = ["all_pupils_a8", "fsm_a8", "non_fsm_a8"]
    group_labels = ["All pupils", "FSM eligible", "Non-FSM"]
    z = [[float(r[g]) for r in rows] for g in groups]

    heatmap = {
        "data": [
            {
                "type": "heatmap",
                "x": regions,
                "y": group_labels,
                "z": z,
                "colorscale": AMBER_SCALE,
                "hovertemplate": "<b>%{x}</b> — %{y}<br>Attainment 8: %{z:.1f}<extra></extra>",
                "colorbar": {"title": "A8", "tickfont": {"color": "#9CA3AF"}},
            }
        ],
        "layout": _layout("Key Stage 4 Attainment 8 by region and FSM status"),
    }

    gap = {
        "data": [
            {
                "type": "bar",
                "x": regions,
                "y": [float(r["disadvantage_gap"]) for r in rows],
                "marker": {"color": AMBER},
                "hovertemplate": "<b>%{x}</b><br>Disadvantage gap: %{y:.1f}<extra></extra>",
            }
        ],
        "layout": _layout("Disadvantage gap in Attainment 8, by region"),
    }
    return heatmap, gap


def nato_charts():
    rows = _read("nato_spend.csv")
    rows = [r for r in rows if r["country"] != "United States"]
    countries = [r["country"] for r in rows]
    spend = [float(r["spend_usd_bn"]) for r in rows]
    gdp = [float(r["gdp_share_pct"]) for r in rows]

    treemap = {
        "data": [
            {
                "type": "treemap",
                "labels": countries,
                "parents": [""] * len(countries),
                "values": spend,
                "textinfo": "label+value",
                "marker": {
                    "colors": gdp,
                    "colorscale": AMBER_SCALE,
                    "showscale": True,
                    "colorbar": {"title": "% GDP", "tickfont": {"color": "#9CA3AF"}},
                    "line": {"color": "#0A0B0D", "width": 1},
                },
                "hovertemplate": "<b>%{label}</b><br>Spend: $%{value:.1f}B<br>%GDP: %{color:.2f}%<extra></extra>",
            }
        ],
        "layout": _layout("European NATO defence spend (USD bn) · shade = % GDP"),
    }

    scatter = {
        "data": [
            {
                "type": "bar",
                "x": countries,
                "y": gdp,
                "marker": {"color": [AMBER if g >= 2.0 else "#78350F" for g in gdp]},
                "hovertemplate": "<b>%{x}</b><br>%GDP: %{y:.2f}%<extra></extra>",
            }
        ],
        "layout": {**_layout("Defence spend as % of GDP (NATO 2% target)"), "shapes": [{
            "type": "line", "x0": -0.5, "x1": len(countries) - 0.5, "y0": 2.0, "y1": 2.0,
            "line": {"color": AMBER, "dash": "dash", "width": 1},
        }]},
    }
    return treemap, scatter


def energy_charts():
    rows = _read("energy_mix.csv")
    countries = [r["country"] for r in rows]
    sources = ["gas", "nuclear", "wind", "solar", "hydro", "biomass", "coal", "other"]
    z = [[float(r[s]) for r in rows] for s in sources]

    heatmap = {
        "data": [
            {
                "type": "heatmap",
                "x": countries,
                "y": [s.capitalize() for s in sources],
                "z": z,
                "colorscale": AMBER_SCALE,
                "hovertemplate": "<b>%{x}</b> — %{y}<br>%{z:.1f}% of generation<extra></extra>",
                "colorbar": {"title": "% mix", "tickfont": {"color": "#9CA3AF"}},
            }
        ],
        "layout": _layout("European electricity generation mix (% by source)"),
    }

    renew = {
        "data": [
            {
                "type": "bar",
                "x": countries,
                "y": [float(r["wind"]) + float(r["solar"]) + float(r["hydro"]) for r in rows],
                "marker": {"color": AMBER},
                "hovertemplate": "<b>%{x}</b><br>Renewable (wind+solar+hydro): %{y:.1f}%<extra></extra>",
            }
        ],
        "layout": _layout("Share of renewables (wind + solar + hydro) by country"),
    }
    return heatmap, renew


def ai_charts():
    rows = _read("ai_adoption.csv")
    countries = [r["country"] for r in rows]
    sectors = ["health", "defense", "education", "public_management", "energy"]
    sector_labels = ["Health", "Defense", "Education", "Public mgmt", "Energy"]
    z = [[float(r[s]) for r in rows] for s in sectors]

    heatmap = {
        "data": [
            {
                "type": "heatmap",
                "x": countries,
                "y": sector_labels,
                "z": z,
                "colorscale": AMBER_SCALE,
                "hovertemplate": "<b>%{x}</b> — %{y}<br>Readiness index: %{z}<extra></extra>",
                "colorbar": {"title": "Index", "tickfont": {"color": "#9CA3AF"}},
                "zmin": 30,
                "zmax": 85,
            }
        ],
        "layout": _layout("Public-sector AI readiness · country × sector (composite 0–100)"),
    }

    by_sector = {}
    for s, label in zip(sectors, sector_labels):
        by_sector[label] = sum(float(r[s]) for r in rows) / len(rows)
    treemap = {
        "data": [
            {
                "type": "treemap",
                "labels": list(by_sector),
                "parents": [""] * len(by_sector),
                "values": list(by_sector.values()),
                "textinfo": "label+value",
                "marker": {
                    "colors": list(by_sector.values()),
                    "colorscale": AMBER_SCALE,
                    "showscale": False,
                    "line": {"color": "#0A0B0D", "width": 1},
                },
                "hovertemplate": "<b>%{label}</b><br>Average readiness: %{value:.1f}<extra></extra>",
            }
        ],
        "layout": _layout("Average public-sector AI readiness by target sector"),
    }
    return heatmap, treemap


def all_charts():
    nhs_a, nhs_b = nhs_charts()
    dfe_a, dfe_b = dfe_charts()
    nato_a, nato_b = nato_charts()
    energy_a, energy_b = energy_charts()
    ai_a, ai_b = ai_charts()
    return {
        "health": {
            "title": "Health",
            "eyebrow": "NHS England",
            "summary": "Waiting lists, median weeks and 18-week breach volumes by specialty.",
            "source": {"label": "NHS England Referral to Treatment", "url": "https://www.england.nhs.uk/statistics/statistical-work-areas/rtt-waiting-times/"},
            "primary": nhs_a,
            "secondary": nhs_b,
        },
        "education": {
            "title": "Education",
            "eyebrow": "UK Department for Education",
            "summary": "Key Stage 4 Attainment 8 by region and free-school-meal status.",
            "source": {"label": "DfE Key Stage 4 performance", "url": "https://explore-education-statistics.service.gov.uk/find-statistics/key-stage-4-performance"},
            "primary": dfe_a,
            "secondary": dfe_b,
        },
        "defense": {
            "title": "Defense",
            "eyebrow": "NATO",
            "summary": "European NATO defence spend, absolute and as share of GDP.",
            "source": {"label": "NATO Defence Expenditure release", "url": "https://www.nato.int/cps/en/natohq/news_226465.htm"},
            "primary": nato_a,
            "secondary": nato_b,
        },
        "energy": {
            "title": "Energy",
            "eyebrow": "Ember · ENTSO-E",
            "summary": "Electricity generation mix across Europe.",
            "source": {"label": "Ember European Electricity Review", "url": "https://ember-energy.org/"},
            "primary": energy_a,
            "secondary": energy_b,
        },
        "ai": {
            "title": "AI",
            "eyebrow": "EC AI Watch · OECD AI · Eurostat",
            "summary": "Composite public-sector AI readiness index across target sectors and European geographies.",
            "source": {"label": "EC AI Watch · OECD AI Observatory · Eurostat", "url": "https://ai-watch.ec.europa.eu/"},
            "primary": ai_a,
            "secondary": ai_b,
        },
    }


def as_json():
    return json.dumps(all_charts(), separators=(",", ":"))
