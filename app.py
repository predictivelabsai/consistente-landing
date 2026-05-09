"""
Consistente — multipage FastHTML landing site.

Dark, slate-amber palette, enterprise-first. Content lives in content/*.py;
routes are thin composition layers over components.py primitives.
"""

from fasthtml.common import (
    fast_app, serve, Div, Span, A, P, Ul, Li, Section, Article, Header,
    NotStr, Script, Style, H1, H2, H3, Button,
)

from components import (
    page, Hero, Pillar, MetricTile, CaseStudyCard, CTASection, NewsSection,
    Section_, Heading, Eyebrow, Pill, Button_,
    CONTACT_EMAIL,
)
from content.case_studies import ALL as ALL_CASES, BID_DERIVED, NAMED_PRECEDENTS
from content.team import TEAM
from content import signal as signal_mod
from content import news as news_mod

news_mod.start_background_refresh()


app, rt = fast_app(live=False, static_path=".", pico=False)


# ---------- /  Home ----------

@rt("/")
def home():
    pillars = [
        ("01", "Document intelligence", "Extraction and retrieval over regulatory filings, clinical protocols, tender packs and legal corpora — with auditable citation trails."),
        ("02", "Applied forecasting", "Demand, revenue and operational forecasting that fuses internal records with open data, satellite and alternative signals."),
        ("03", "Geospatial & mobility", "Origin-destination matrices, anomaly detection and situation pictures, built on open data and published as reference implementations."),
        ("04", "Agentic workflows", "Multi-step LLM agents that run inside your security boundary, instrumented for evaluation and human review."),
    ]

    logos_row = [
        "Microsoft (ISD)", "ARM Holdings", "DBRS Morningstar", "London Stock Exchange Group",
        "Nando's", "Indurent (Blackstone)",
    ]

    home_cases = [c for c in ALL_CASES if c["id"] in ("uk-traffic-od", "nordic-health-rwd", "microsoft-isd")]

    return page(
        "Consistent AI for enterprise outcomes",
        "/",
        Hero(),

        Section_(
            Eyebrow("Precedent"),
            Heading(2, "Delivered inside institutions that take correctness seriously.", cls="mt-4 max-w-3xl"),
            Div(
                *[Div(name, cls="text-ink-muted text-sm md:text-base font-medium border border-line rounded-full px-4 py-2") for name in logos_row],
                cls="mt-10 flex flex-wrap gap-3",
            ),
            cls="border-b border-line",
        ),

        Section_(
            Div(
                Eyebrow("Capabilities"),
                Heading(2, "Four capabilities, composed to fit the programme.", cls="mt-4 max-w-4xl"),
                P("We don't ship a platform. We ship a team that brings a platform's discipline to every engagement — reproducible pipelines, versioned models, inspectable prompts.", cls="mt-5 text-ink-muted text-lg max-w-3xl"),
                cls="mb-14",
                id="capabilities",
            ),
            Div(
                *[Pillar(n, t, b) for n, t, b in pillars],
                cls="grid md:grid-cols-2 lg:grid-cols-4 gap-5",
            ),
        ),

        Section_(
            Div(
                Eyebrow("Where we work"),
                Heading(2, "Built around four enterprise verticals — and growing.", cls="mt-4 max-w-4xl"),
                cls="mb-14",
            ),
            Div(
                _sector_card("Defense & public security", "Decision support inside defence, justice and critical infrastructure — with clear boundaries between AI assistance and human authority."),
                _sector_card("Health & life sciences", "Real-world evidence, protocol design and hospital operations — on privacy-preserving, regulatory-grade pipelines."),
                _sector_card("Public management & mobility", "Traffic, planning and municipal analytics — built on open data and shipped with reference implementations."),
                _sector_card("Financial services", "Rating, forecasting and document intelligence at enterprise scale."),
                cls="grid md:grid-cols-2 gap-5",
            ),
            cls="border-y border-line bg-bg-elevated/40",
        ),

        Section_(
            Div(
                Eyebrow("Selected work"),
                Heading(2, "What the programmes look like.", cls="mt-4 max-w-3xl"),
                cls="mb-14 flex flex-col md:flex-row md:items-end md:justify-between gap-4",
                id="case-studies",
            ),
            Div(
                *[CaseStudyCard(c, compact=True) for c in home_cases],
                cls="grid md:grid-cols-3 gap-5",
            ),
        ),

        Section_(
            Div(
                Div(
                    Eyebrow("Signal"),
                    Heading(2, "We read the data our clients work with — every day.", cls="mt-4 max-w-3xl"),
                    P(
                        "Enterprise delivery starts with the public data. A live view of NHS waiting lists, European defence spend, school attainment gaps, energy mix and AI readiness — the canvases our programmes run against.",
                        cls="mt-5 text-ink-muted text-lg max-w-2xl leading-relaxed",
                    ),
                    cls="md:w-2/5",
                    id="signal",
                ),
                Div(
                    Div(id="signal-teaser", cls="w-full h-[360px]"),
                    cls="md:w-3/5 p-3 rounded-2xl bg-bg-elevated border border-line",
                ),
                cls="flex flex-col md:flex-row gap-10 items-stretch",
            ),
            cls="border-y border-line",
        ),

        NewsSection(
            category="home",
            title="What's moving in AI and enterprise technology.",
            subtitle="A rolling mix from AI, enterprise, healthcare and financial-services feeds. Refreshed hourly; links open in a new tab.",
        ),

        CTASection(),

        body_extra=[
            Script(src="https://cdn.plot.ly/plotly-2.35.2.min.js"),
            Script(NotStr(f"window.PLOTLY_TEASER = {_teaser_json()};")),
            Script(src="/static/signal.js"),
            Script(src="/static/three-hero.js", type="module"),
        ],
    )


def _sector_card(title, body):
    return Div(
        Div(
            Span(title, cls="text-ink text-xl font-medium tracking-tight"),
            cls="flex items-center mb-3",
        ),
        P(body, cls="text-ink-muted text-sm leading-relaxed"),
        cls="p-7 rounded-2xl border border-line bg-bg-elevated hover:border-accent/50 transition-all",
    )


def _teaser_json():
    import json
    from content import signal as s
    nhs, _ = s.nhs_charts()
    nhs["layout"]["title"]["text"] = "NHS England waiting list · treemap by specialty"
    nhs["layout"]["margin"] = {"l": 0, "r": 0, "t": 30, "b": 0}
    return json.dumps(nhs)


# ---------- /team ----------

@rt("/team")
def team():
    return page(
        "Team",
        "/team",
        Section_(
            Eyebrow("Team"),
            Heading(1, "A small group, bound by the discipline the work demands.", cls="mt-5 max-w-4xl"),
            P("We are deliberately small — senior engineers and scientists who own delivery end-to-end. We extend through a vetted partner network when a programme needs specialist clearance, language or capacity.",
              cls="mt-8 text-xl text-ink-muted max-w-3xl leading-relaxed"),
            cls="pt-24",
        ),
        Section_(
            Div(
                *[_member_card(m) for m in TEAM],
                cls="grid md:grid-cols-2 gap-5",
            ),
        ),
        CTASection(headline="Looking to join us?", body="We work with hand-picked partners and occasional specialist contractors. If your background fits the capabilities on this site, tell us.", cta_label="Write to us"),
    )


def _member_card(m):
    return Article(
        Div(
            Div(m["initials"], cls="w-14 h-14 rounded-full bg-bg-raised border border-line flex items-center justify-center text-ink font-mono text-sm"),
            Div(
                Heading(3, m["name"], cls="mb-1"),
                P(m["role"], cls="text-accent text-sm font-mono"),
            ),
            cls="flex items-center gap-4 mb-5",
        ),
        P(m["bio"], cls="text-ink-muted leading-relaxed mb-6"),
        A(
            Span("LinkedIn", cls="text-sm"),
            Span("→", cls="text-sm"),
            href=m["linkedin"],
            target="_blank",
            cls="inline-flex items-center gap-2 text-ink hover:text-accent transition-colors",
        ),
        cls="p-8 rounded-2xl bg-bg-elevated border border-line",
    )


# ---------- /contact ----------

@rt("/contact")
def contact():
    return page(
        "Contact",
        "/contact",
        Section_(
            Eyebrow("Contact"),
            Heading(1, "Brief us on the programme.", cls="mt-5 max-w-4xl"),
            P("We work with enterprise buyers across the UK, the Nordics, the Benelux and the Baltics, and selectively with regulated enterprise clients. Tell us the problem — we'll tell you if we can help.",
              cls="mt-8 text-xl text-ink-muted max-w-3xl leading-relaxed"),
            cls="pt-24",
        ),
        Section_(
            Div(
                Div(
                    Eyebrow("Write to us"),
                    Heading(2, CONTACT_EMAIL, cls="mt-4 break-all"),
                    P("We read every brief personally. A short note on the buyer, the problem and the deadline is enough to start.",
                      cls="mt-5 text-ink-muted leading-relaxed"),
                    Div(
                        Button_("Email " + CONTACT_EMAIL, href=f"mailto:{CONTACT_EMAIL}", primary=True),
                        cls="mt-8",
                    ),
                    cls="p-10 rounded-2xl bg-bg-elevated border border-line",
                ),
                Div(
                    Div(
                        H3("Registered office", cls="text-sm font-mono tracking-widest uppercase text-ink-muted mb-3"),
                        P("Consistente Ltd", cls="text-ink"),
                        P("Rävala pst 6", cls="text-ink-muted"),
                        P("10145 Tallinn", cls="text-ink-muted"),
                        P("Estonia", cls="text-ink-muted"),
                        P("Registry code 14972741", cls="text-ink-dim text-sm mt-3 font-mono"),
                        cls="mb-10",
                    ),
                    Div(
                        H3("Channels", cls="text-sm font-mono tracking-widest uppercase text-ink-muted mb-3"),
                        A("Email", href=f"mailto:{CONTACT_EMAIL}", cls="block text-ink hover:text-accent mb-2"),
                    ),
                    cls="p-10 rounded-2xl bg-bg-elevated border border-line",
                ),
                cls="grid md:grid-cols-2 gap-5",
            ),
        ),
    )


if __name__ == "__main__":
    serve()
