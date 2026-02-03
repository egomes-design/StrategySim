import random
import streamlit as st
import pandas as pd

st.set_page_config(page_title='Mobile Growth Strategy Simulation (Ansoff)', layout='wide')

st.markdown(
    """
    <style>
    .page-banner {
        border-radius: 14px;
        padding: 22px 22px;
        margin: 8px 0 18px 0;
        background-size: cover;
        background-position: center;
        color: white;
    }
    .page-banner h2 { color: white !important; margin: 0; }
    .page-banner p { color: white !important; margin: 6px 0 0 0; }
    </style>
    """,
    unsafe_allow_html=True
)


def clamp(val, lo, hi):
    return max(lo, min(hi, val))


def go_to(page_name):
    st.session_state.page = page_name
    st.rerun()


# ----------------------------
# Session state defaults
# ----------------------------
if 'started' not in st.session_state:
    st.session_state.started = False
if 'page' not in st.session_state:
    st.session_state.page = 'welcome'
if 'company_name' not in st.session_state:
    st.session_state.company_name = 'Orion Mobile'
if 'quarter' not in st.session_state:
    st.session_state.quarter = 1
if 'max_quarters' not in st.session_state:
    st.session_state.max_quarters = 6
if 'budget' not in st.session_state:
    st.session_state.budget = 100
if 'history' not in st.session_state:
    st.session_state.history = []
if 'shock_queue' not in st.session_state:
    st.session_state.shock_queue = []
if 'last_shock' not in st.session_state:
    st.session_state.last_shock = None
if 'capabilities' not in st.session_state:
    st.session_state.capabilities = {
        'Brand': 55,
        'R&D': 55,
        'Supply Chain': 55,
        'Retail & Carrier Channels': 55,
        'Software & Services': 50,
        'Enterprise Sales': 40,
    }
if 'kpis' not in st.session_state:
    st.session_state.kpis = {
        'Revenue Index': 100.0,
        'Gross Margin %': 34.0,
        'Market Share %': 8.0,
        'Cash': 100.0,
        'Risk': 20.0,
        'Optionality': 20.0,
    }


MOVE_CATALOG = {
    'A': {
        'name': 'Win the core smartphone business',
        'ansoff': 'Market penetration',
        'desc': 'Improve conversion, retention, pricing, and unit economics in current segments. Examples: carrier promos, cost-down, reliability, mid-cycle refresh.'
    },
    'B': {
        'name': 'Expand into new markets and channels',
        'ansoff': 'Market development',
        'desc': 'Take current phones into new geographies or channels. Examples: India growth push, LATAM distributors, online D2C store, new carrier partnerships.'
    },
    'C': {
        'name': 'Build the next offering for current customers',
        'ansoff': 'Product development',
        'desc': 'New products or major upgrades for existing customers. Examples: foldables, camera AI stack, wearables bundle, OS features, premium services.'
    },
    'D': {
        'name': 'Enter a new arena',
        'ansoff': 'Diversification',
        'desc': 'New customers and new economics. Examples: enterprise mobility suite, device financing, refurbished marketplace, IoT edge devices, AR glasses.'
    }
}


SHOCK_CARDS = [
    {
        'title': 'Chipset shortage hits flagship builds',
        'text': 'Lead times spike. Flagship availability and channel fill rates drop for two quarters.',
        'effects': {'Supply Chain': -8, 'Revenue Index': -4.5, 'Risk': 6}
    },
    {
        'title': 'Carrier shifts promo dollars to a rival',
        'text': 'A key carrier partner reduces co-op marketing and store placement this quarter.',
        'effects': {'Retail & Carrier Channels': -6, 'Market Share %': -0.6, 'Revenue Index': -2.5}
    },
    {
        'title': 'Privacy regulation slows feature launches',
        'text': 'Compliance work increases and your release cadence slows this quarter.',
        'effects': {'Software & Services': -5, 'Gross Margin %': -1.0, 'Risk': 4}
    },
    {
        'title': 'Competitor launches a disruptive camera feature',
        'text': 'Perceived innovation gap shows up in reviews and social buzz.',
        'effects': {'Brand': -5, 'Market Share %': -0.5, 'Optionality': -2}
    },
    {
        'title': 'FX swing boosts profitability in one region',
        'text': 'A currency move benefits your cost base and margins this quarter.',
        'effects': {'Gross Margin %': 1.2, 'Cash': 6}
    }
]


def init_shocks():
    shock_pool = SHOCK_CARDS.copy()
    random.shuffle(shock_pool)
    st.session_state.shock_queue = shock_pool


def draw_shock():
    if len(st.session_state.shock_queue) == 0:
        init_shocks()
    return st.session_state.shock_queue.pop(0)


def apply_shock(card):
    st.session_state.last_shock = card
    fx = card.get('effects', {})
    for k, v in fx.items():
        if k in st.session_state.capabilities:
            st.session_state.capabilities[k] = clamp(st.session_state.capabilities[k] + float(v), 0, 100)
        elif k in st.session_state.kpis:
            st.session_state.kpis[k] = float(st.session_state.kpis[k]) + float(v)


def score_allocation(alloc):
    total = sum(alloc.values())
    if total <= 0:
        return {'valid': False, 'msg': 'Allocate points across A/B/C/D.'}
    if total != st.session_state.budget:
        return {'valid': False, 'msg': 'Your allocation must sum to ' + str(st.session_state.budget) + '.'}
    return {'valid': True, 'msg': 'OK'}


def advance_quarter(alloc):
    budget = float(st.session_state.budget)
    a = alloc['A'] / budget
    b = alloc['B'] / budget
    c = alloc['C'] / budget
    d = alloc['D'] / budget

    st.session_state.capabilities['Brand'] = clamp(st.session_state.capabilities['Brand'] + (6*a + 2*b + 3*c + 1*d), 0, 100)
    st.session_state.capabilities['R&D'] = clamp(st.session_state.capabilities['R&D'] + (1*a + 2*b + 7*c + 4*d), 0, 100)
    st.session_state.capabilities['Supply Chain'] = clamp(st.session_state.capabilities['Supply Chain'] + (4*a + 2*b + 1*c + 2*d), 0, 100)
    st.session_state.capabilities['Retail & Carrier Channels'] = clamp(st.session_state.capabilities['Retail & Carrier Channels'] + (4*a + 7*b + 1*c + 1*d), 0, 100)
    st.session_state.capabilities['Software & Services'] = clamp(st.session_state.capabilities['Software & Services'] + (1*a + 2*b + 6*c + 5*d), 0, 100)
    st.session_state.capabilities['Enterprise Sales'] = clamp(st.session_state.capabilities['Enterprise Sales'] + (0*a + 1*b + 2*c + 8*d), 0, 100)

    cap = st.session_state.capabilities
    kpi = st.session_state.kpis

    div_fit = (cap['Enterprise Sales'] * 0.6 + cap['Software & Services'] * 0.4) / 100.0
    div_penalty = max(0.0, (0.55 - div_fit))

    core_eff = (cap['Supply Chain'] * 0.35 + cap['Retail & Carrier Channels'] * 0.35 + cap['Brand'] * 0.30) / 100.0
    innovation = (cap['R&D'] * 0.55 + cap['Software & Services'] * 0.45) / 100.0
    channel = (cap['Retail & Carrier Channels'] / 100.0)

    base_growth = 0.8 + 3.8*a + 3.2*b + 2.6*c + 2.2*d
    capability_bonus = 1.8*core_eff + 1.2*channel + 1.4*innovation
    noise = random.uniform(-0.9, 0.9)
    rev_delta = base_growth + capability_bonus + noise
    kpi['Revenue Index'] = max(40.0, kpi['Revenue Index'] * (1.0 + rev_delta/100.0))

    share_delta = (0.08 + 1.3*a + 1.1*b + 0.6*c + 0.4*d) * (0.55 + 0.45*channel) + random.uniform(-0.25, 0.25)
    kpi['Market Share %'] = clamp(kpi['Market Share %'] + share_delta, 0.5, 40.0)

    margin_delta = (0.20 + 2.0*a - 1.3*c - 0.6*d + 0.4*b) + (core_eff - 0.55) * 3.0 + random.uniform(-0.6, 0.6)
    kpi['Gross Margin %'] = clamp(kpi['Gross Margin %'] + margin_delta, 10.0, 60.0)

    cash_delta = (rev_delta * 0.55) + (margin_delta * 0.45) - (c*8.0 + d*10.0) + random.uniform(-3.0, 3.0)
    kpi['Cash'] = clamp(kpi['Cash'] + cash_delta, 0.0, 200.0)

    opt_delta = (2.0*c + 3.0*d) * (0.40 + 0.60*innovation) + random.uniform(-0.8, 0.8)
    kpi['Optionality'] = clamp(kpi['Optionality'] + opt_delta, 0.0, 100.0)

    risk_delta = (2.0*d + 0.6*c + 0.4*b - 1.2*a) + (div_penalty * 16.0)
    if kpi['Cash'] < 35:
        risk_delta += 6.0
    risk_delta += random.uniform(-1.0, 1.2)
    kpi['Risk'] = clamp(kpi['Risk'] + risk_delta, 0.0, 100.0)

    card = draw_shock()
    apply_shock(card)

    st.session_state.history.append(
        {
            'quarter': st.session_state.quarter,
            'alloc': alloc,
            'kpis': dict(st.session_state.kpis),
            'capabilities': dict(st.session_state.capabilities),
            'shock': card
        }
    )

    st.session_state.quarter += 1


def kpi_cards():
    k = st.session_state.kpis
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric('Revenue Index', str(round(k['Revenue Index'], 1)))
        st.metric('Market Share %', str(round(k['Market Share %'], 2)))
    with c2:
        st.metric('Gross Margin %', str(round(k['Gross Margin %'], 1)))
        st.metric('Cash', str(round(k['Cash'], 1)))
    with c3:
        st.metric('Optionality', str(round(k['Optionality'], 1)))
        st.metric('Risk', str(round(k['Risk'], 1)))


def shock_box():
    card = st.session_state.last_shock
    if not card:
        return
    st.markdown('### External event')
    st.info(card['title'] + '  ' + card['text'])


def render_sidebar():
    with st.sidebar:
        st.markdown('### Simulation')
        st.write('Company')
        st.write(st.session_state.company_name)
        st.write('Quarter')
        st.write(str(min(st.session_state.quarter, st.session_state.max_quarters)) + ' of ' + str(st.session_state.max_quarters))
        st.write('Budget')
        st.write(str(st.session_state.budget) + ' points')

        st.markdown('---')
        st.markdown('### Navigate')
        if st.button('Welcome'):
            st.session_state.started = False
            go_to('welcome')
        if st.button('Decisions'):
            st.session_state.started = True
            go_to('decisions')
        if st.button('Results'):
            st.session_state.started = True
            go_to('results')

        st.markdown('---')
        if st.button('Reset run'):
            st.session_state.started = False
            st.session_state.page = 'welcome'
            st.session_state.quarter = 1
            st.session_state.history = []
            st.session_state.last_shock = None
            st.session_state.capabilities = {
                'Brand': 55,
                'R&D': 55,
                'Supply Chain': 55,
                'Retail & Carrier Channels': 55,
                'Software & Services': 50,
                'Enterprise Sales': 40,
            }
            st.session_state.kpis = {
                'Revenue Index': 100.0,
                'Gross Margin %': 34.0,
                'Market Share %': 8.0,
                'Cash': 100.0,
                'Risk': 20.0,
                'Optionality': 20.0,
            }
            init_shocks()
            st.rerun()


if len(st.session_state.shock_queue) == 0:
    init_shocks()

render_sidebar()


# ----------------------------
# WELCOME PAGE
# ----------------------------
if (not st.session_state.started) or (st.session_state.page == 'welcome'):
    bg_img_url = 'https://images.unsplash.com/photo-1521737604893-d14cc237f11d?auto=format&fit=crop&w=2400&q=80'

    st.markdown(
        """
        <style>
        .welcome-hero {
            width: 100%;
            border-radius: 16px;
            padding: 64px 48px;
            margin: 8px 0 24px 0;
            background-image:
                linear-gradient(rgba(0,0,0,0.60), rgba(0,0,0,0.60)),
                url(""" + bg_img_url + """);
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            color: white;
        }
        .welcome-hero h1, .welcome-hero p { color: white !important; }
        </style>

        <div class="welcome-hero">
            <h1>Mobile Growth Strategy Simulation</h1>
            <p style="font-size: 1.1rem; max-width: 960px; line-height: 1.65;">
                You are running a fictitious phone maker with real-world constraints: fast cycles, hard supply chains,
                brutal competition, and limited resources. Use the Ansoff model to decide how to grow.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown('#### What you do each quarter')
    st.write('Allocate 100 points across four moves that map cleanly to the Ansoff matrix. Your choices change capabilities, which then drive outcomes. Each quarter also includes a mobile-industry shock.')

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown('**A  Market penetration**')
        st.write(MOVE_CATALOG['A']['name'])
        st.markdown('**B  Market development**')
        st.write(MOVE_CATALOG['B']['name'])
    with col_b:
        st.markdown('**C  Product development**')
        st.write(MOVE_CATALOG['C']['name'])
        st.markdown('**D  Diversification**')
        st.write(MOVE_CATALOG['D']['name'])

    st.markdown('#### Start')
    st.session_state.company_name = st.text_input('Your company name', value=st.session_state.company_name)

    if st.button('Start simulation', type='primary'):
        st.session_state.started = True
        st.session_state.page = 'decisions'
        st.rerun()

    st.stop()


# ----------------------------
# DECISIONS PAGE
# ----------------------------
if st.session_state.page == 'decisions':
    decisions_img = 'https://images.unsplash.com/photo-1553877522-43269d4ea984?auto=format&fit=crop&w=2400&q=80'
    st.markdown(
        """
        <div class="page-banner" style="background-image: linear-gradient(rgba(0,0,0,0.52), rgba(0,0,0,0.52)), url(""" + decisions_img + """);">
          <h2>Decisions</h2>
          <p>Allocate points across A/B/C/D. Make tradeoffs. Submit to advance to results.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.session_state.quarter > st.session_state.max_quarters:
        st.success('Simulation complete. Go to Results to review the full run.')
        if st.button('Go to Results', type='primary'):
            go_to('results')
        st.stop()

    st.markdown('### Current performance')
    kpi_cards()

    st.markdown('### Allocation for Quarter ' + str(st.session_state.quarter))
    st.caption('Budget must sum to ' + str(st.session_state.budget) + ' points.')

    default_alloc = {'A': 25, 'B': 25, 'C': 25, 'D': 25}
    if len(st.session_state.history) > 0:
        default_alloc = dict(st.session_state.history[-1]['alloc'])

    col1, col2 = st.columns([2, 1])
    with col1:
        alloc = {}
        for key in ['A', 'B', 'C', 'D']:
            st.markdown('**' + key + '  ' + MOVE_CATALOG[key]['name'] + '**')
            st.caption(MOVE_CATALOG[key]['ansoff'] + '  ' + MOVE_CATALOG[key]['desc'])
            alloc[key] = st.slider(
                'Points to ' + key,
                min_value=0,
                max_value=st.session_state.budget,
                value=int(default_alloc.get(key, 0)),
                step=5,
                key='slider_' + key
            )

    with col2:
        total = sum([alloc.get('A', 0), alloc.get('B', 0), alloc.get('C', 0), alloc.get('D', 0)])
        remaining = st.session_state.budget - total
        st.markdown('### Budget')
        st.metric('Points remaining', str(remaining))
        st.markdown('---')
        st.markdown('### Capabilities')
        for ck in st.session_state.capabilities:
            st.progress(int(clamp(st.session_state.capabilities[ck], 0, 100)))
            st.caption(ck + '  ' + str(int(st.session_state.capabilities[ck])))

    verdict = score_allocation(alloc)
    if not verdict['valid']:
        st.warning(verdict['msg'])
    else:
        if st.button('Submit allocation and view results', type='primary'):
            advance_quarter(alloc)
            go_to('results')

    st.stop()


# ----------------------------
# RESULTS PAGE
# ----------------------------
if st.session_state.page == 'results':
    results_img = 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=2400&q=80'
    st.markdown(
        """
        <div class="page-banner" style="background-image: linear-gradient(rgba(0,0,0,0.52), rgba(0,0,0,0.52)), url(""" + results_img + """);">
          <h2>Results</h2>
          <p>Review outcomes, shocks, and trends. Then decide what to change next quarter.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown('### Current performance')
    kpi_cards()
    shock_box()

    st.markdown('### Trends')
    if len(st.session_state.history) == 0:
        st.info('No quarters played yet. Go to Decisions to submit an allocation.')
        if st.button('Go to Decisions', type='primary'):
            go_to('decisions')
        st.stop()

    trend_df = pd.DataFrame(
        {
            'Quarter': [h['quarter'] for h in st.session_state.history],
            'Revenue Index': [h['kpis']['Revenue Index'] for h in st.session_state.history],
            'Market Share %': [h['kpis']['Market Share %'] for h in st.session_state.history],
            'Gross Margin %': [h['kpis']['Gross Margin %'] for h in st.session_state.history],
            'Cash': [h['kpis']['Cash'] for h in st.session_state.history],
            'Risk': [h['kpis']['Risk'] for h in st.session_state.history],
            'Optionality': [h['kpis']['Optionality'] for h in st.session_state.history],
        }
    ).sort_values('Quarter')

    st.line_chart(trend_df.set_index('Quarter'))

    st.markdown('### Quarter narrative')
    last = st.session_state.history[-1]
    alloc = last['alloc']
    shock = last['shock']

    a_pts = alloc['A']
    b_pts = alloc['B']
    c_pts = alloc['C']
    d_pts = alloc['D']
    big_move = max([('A', a_pts), ('B', b_pts), ('C', c_pts), ('D', d_pts)], key=lambda x: x[1])[0]

    driver_map = {
        'A': 'your core focus improved execution and near-term efficiency',
        'B': 'market expansion increased reach but added channel complexity',
        'C': 'product bets built innovation and optionality but weighed on near-term margin',
        'D': 'diversification created option value but required new capabilities'
    }

    st.write(
        'In Quarter ' + str(last['quarter']) + ', your largest bet was **' + big_move + '**. '
        'Overall, ' + driver_map.get(big_move, 'your allocation shifted the operating balance') + '. '
        'An external event also hit the industry: **' + shock['title'] + '**.'
    )

    with st.expander('See quarter details'):
        st.dataframe(trend_df, use_container_width=True)
        for h in st.session_state.history[::-1]:
            st.markdown('**Quarter ' + str(h['quarter']) + '**')
            st.write('Allocation  A ' + str(h['alloc']['A']) + '  B ' + str(h['alloc']['B']) + '  C ' + str(h['alloc']['C']) + '  D ' + str(h['alloc']['D']))
            st.write('Shock  ' + h['shock']['title'])

    colx, coly = st.columns([1, 1])
    with colx:
        if st.session_state.quarter <= st.session_state.max_quarters:
            if st.button('Next quarter decisions', type='primary'):
                go_to('decisions')
        else:
            st.success('You have completed all quarters. Use Reset in the sidebar to run again.')
    with coly:
        if st.button('Back to Welcome'):
            st.session_state.started = False
            go_to('welcome')

    st.stop()
