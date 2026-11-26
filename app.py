"""서울시 버스 정류장 형평성 분석."""
from pathlib import Path
from html import escape
import geopandas as gpd
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium
from utils.model_factory import create_models
from utils.visualizer import Visualizer

st.set_page_config(page_title='서울시 버스 정류장 형평성 분석', page_icon='🚌', layout='wide')
st.markdown('''<style>
.block-container{max-width:1800px;padding:1rem 1.2rem 2rem} [data-testid="stAppViewContainer"]{background:#f5f8f6;color:#17251d} .hero{background:#d3f2a4;color:#07552d;padding:18px 24px;border-radius:8px;margin-bottom:10px}.hero h1{color:#07552d;font-size:30px;margin:0;padding:0}.hero p{margin:3px 0;color:#07552d}.kpi,.detail,.rank{background:white;border:1px solid #b9cfc0;border-radius:14px;padding:12px 16px;color:#17251d}.kpi b{font-size:18px;display:block}.kpi small{font-weight:600}.rank{padding:0;overflow:hidden;margin-bottom:10px}.rank h4{background:#edf7e9;color:#07552d;margin:0;padding:8px 12px;font-size:16px}.rank.low h4{background:#fff1e7;color:#c43c12}.rrow{display:flex;justify-content:space-between;padding:5px 12px;font-weight:650}.rrow span:last-child{color:#07552d}.low .rrow span:last-child{color:#c43c12}.detail h3{background:#d3f2a4;color:#07552d;padding:10px;margin:-12px -16px 12px;border-radius:12px 12px 0 0}.detail h2{font-size:32px;color:#111}.metricbox{border:1px solid #cbd8d0;border-radius:12px;padding:12px;margin:10px 0}.metricbox b{display:block;font-size:28px;color:#07552d}.info{display:flex;justify-content:space-between;border-bottom:1px solid #e5ebe7;padding:8px 0}.footer{background:white;border-radius:10px;padding:14px;color:#07552d;font-weight:600} .section{font-size:20px;font-weight:750;color:#123c26;margin:8px 0}
/* Keep existing dashboard visible during Streamlit reruns. */
[data-testid="stAppViewContainer"] .stale-element,
[data-testid="stAppViewContainer"] [data-stale="true"],
[data-testid="stAppViewContainer"] [data-testid="stElementContainer"][data-stale="true"] {
    opacity: 1 !important;
    transition: none !important;
}
/* Match the toolbar and buttons to the light dashboard. */
[data-testid="stHeader"], [data-testid="stToolbar"] {background:#f5f8f6 !important;color:#07552d !important;}
[data-testid="stHeader"] button, [data-testid="stToolbar"] button {color:#07552d !important;}
[data-testid="stButton"] button {background:#ffffff !important;color:#07552d !important;border:1px solid #b9cfc0 !important;}
[data-testid="stButton"] button:hover {background:#eaf4e9 !important;}
.block-container {padding-top:4rem !important;}

/* Responsive layout: viewport-based typography and map sizing. */
.block-container {max-width: 100%; padding-inline: clamp(12px, 1.4vw, 32px);}
.hero {padding: clamp(12px, 1.2vw, 26px);}
.hero h1 {font-size: clamp(21px, 2vw, 40px); line-height: 1.25;}
.hero p, .detail, .rank, .footer {font-size: clamp(12px, .9vw, 19px);}
.section {font-size: clamp(16px, 1.25vw, 25px);}
.kpi, .detail {padding: clamp(8px, .8vw, 18px); min-width: 0;}
.kpi small {font-size: clamp(11px, .8vw, 16px);}
.kpi b {font-size: clamp(15px, 1.15vw, 24px); overflow-wrap: anywhere;}
.detail h3 {font-size: clamp(18px, 1.4vw, 29px); margin: 0 0 12px; border-radius: 8px;}
.detail h2 {font-size: clamp(24px, 2vw, 40px);}
.metricbox b {font-size: clamp(20px, 1.7vw, 34px);}
.rank h4 {font-size: clamp(13px, 1vw, 21px);}
.rrow, .info {gap: 6px; flex-wrap: wrap;}
.rrow span:last-child, .info strong {white-space: nowrap;}
[data-testid="stButton"] button, [data-testid="stTextInput"] input {font-size: clamp(13px, .9vw, 18px);}
[data-testid="stColumn"] {min-width: 0 !important;}
iframe[title*="st_folium"] {width: 100% !important; height: clamp(520px, 76vh, 1100px) !important; display: block;}
@media (max-width: 1050px) {
  [data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"] .right-panel):not(:has([data-testid="stHorizontalBlock"] .right-panel)) {flex-wrap: wrap !important;}
  [data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"] .right-panel):not(:has([data-testid="stHorizontalBlock"] .right-panel)) > [data-testid="stColumn"] {flex: 1 1 100% !important; width: 100% !important;}
}
@media (max-width: 700px) {
  [data-testid="stHorizontalBlock"] {flex-wrap: wrap !important;}
  [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {flex: 1 1 100% !important; width: 100% !important;}
  [data-testid="stHorizontalBlock"]:has(.kpi):not(:has([data-testid="stHorizontalBlock"] .kpi)) > [data-testid="stColumn"] {flex: 1 1 45% !important; width: 45% !important;}
  iframe[title*="st_folium"] {height: clamp(340px, 58vh, 600px) !important;}
  .block-container {padding-inline: 10px;}
}

/* Light search widgets, including dark browser themes. */
[data-testid="stTextInput"] [data-baseweb="input"],
[data-testid="stTextInput"] [data-baseweb="base-input"],
[data-testid="stTextInput"] input,
[data-testid="stSelectbox"] [data-baseweb="select"] > div {
 background: #ffffff !important; color: #07552d !important;
}
[data-testid="stTextInput"] [data-baseweb="input"],
[data-testid="stSelectbox"] [data-baseweb="select"] > div {border: 1px solid #b9cfc0 !important;}
[data-testid="stTextInput"] input::placeholder {color:#65796d !important; opacity:1;}
[data-testid="stSelectbox"] [data-baseweb="select"] *,
[data-testid="stWidgetLabel"] p {color:#07552d !important;}
[data-baseweb="popover"] [role="listbox"], [data-baseweb="popover"] [role="option"] {background:#fff !important;color:#07552d !important;}
[data-baseweb="popover"] [role="option"]:hover {background:#eaf4e9 !important;}
/* Only the toolbar row, never its ancestor rows. */
@media (min-width: 701px) {
 [data-testid="stHorizontalBlock"]:has(.map-heading):not(:has([data-testid="stHorizontalBlock"] .map-heading)) {align-items:center !important; gap:8px !important;}
 [data-testid="stHorizontalBlock"]:has(.map-heading):not(:has([data-testid="stHorizontalBlock"] .map-heading)) > [data-testid="stColumn"]:nth-child(1),
 [data-testid="stHorizontalBlock"]:has(.map-heading):not(:has([data-testid="stHorizontalBlock"] .map-heading)) > [data-testid="stColumn"]:nth-child(2),
 [data-testid="stHorizontalBlock"]:has(.map-heading):not(:has([data-testid="stHorizontalBlock"] .map-heading)) > [data-testid="stColumn"]:nth-child(4) {flex:0 0 auto !important;width:auto !important;}
 [data-testid="stHorizontalBlock"]:has(.map-heading):not(:has([data-testid="stHorizontalBlock"] .map-heading)) > [data-testid="stColumn"]:nth-child(3) {flex:1 1 0 !important;width:0 !important; min-width:0 !important;}
 .map-heading {margin:0;}
}

/* Light selectbox: BaseWeb may apply the dark background to nested controls. */
[data-testid="stSelectbox"] [data-baseweb="select"],
[data-testid="stSelectbox"] [data-baseweb="select"] div,
[data-testid="stSelectbox"] [role="combobox"],
[data-testid="stSelectbox"] input {background-color:#fff !important;color:#07552d !important;}
[data-testid="stSelectbox"] [data-baseweb="select"] > div {border-color:#b9cfc0 !important;}
[data-testid="stSelectbox"] svg {fill:#07552d !important;color:#07552d !important;}
/* Compact ranking cards; leave all Streamlit column widths untouched. */
.rank {margin-bottom:0; border-radius:10px; font-size:clamp(11px,.78vw,15px); line-height:1.2;}
.rank h4 {padding:clamp(4px,.45vh,7px) 10px; font-size:clamp(12px,.85vw,16px); line-height:1.2;}
.rrow {padding:clamp(2px,.35vh,5px) 10px; gap:4px; line-height:1.2;}
[data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .rank) {gap:0.35rem;}
@media (max-width:700px) {.rank h4,.rrow {padding-block:6px;}}


/* Dropdown portal is outside the selectbox itself. */
[data-baseweb="popover"], [data-baseweb="popover"] > div,
[data-baseweb="popover"] [data-baseweb="menu"],
[data-baseweb="popover"] [role="listbox"],
[data-baseweb="popover"] [role="option"],
[data-baseweb="popover"] li,
[data-baseweb="popover"] li * {background-color:#fff !important;color:#07552d !important;}
[data-baseweb="popover"] [role="option"]:hover,
[data-baseweb="popover"] [role="option"][aria-selected="true"],
[data-baseweb="popover"] li:hover {background-color:#eaf4e9 !important;color:#07552d !important;}
[data-testid="stSelectbox"] [data-baseweb="select"] > div:focus-within {border-color:#82ad90 !important;}
.rank-stack {display:grid;grid-template-rows:repeat(4,minmax(min-content,1fr));gap:8px;min-height:clamp(420px,59vh,820px);}
.rank-stack .rank {display:flex;flex-direction:column;height:auto;min-height:max-content;margin:0;overflow:visible;box-sizing:border-box;}
.rank-stack .rank h4 {padding:7px 10px;border-radius:9px 9px 0 0;}
.rank-stack .rrow {flex:1 0 auto;align-items:center;padding:5px 10px;line-height:1.35;}
@media(max-width:1050px){.rank-stack{min-height:0;grid-template-rows:repeat(4,auto);}}

/* Shared desktop body height; all three panels begin in the same row. */
:root {--body-height:clamp(720px, 82vh, 1050px);}
iframe[title*="st_folium"] {height:var(--body-height) !important;width:100% !important;}
.detail,.right-panel {box-sizing:border-box;min-height:var(--body-height);display:flex;flex-direction:column;}
.detail .info {flex:1;align-items:center;}
.right-panel {gap:8px;}
.right-panel .section {margin:0;}
.kpi-grid {display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;}
.rank-stack {flex:1;min-height:0;grid-template-rows:repeat(4,minmax(max-content,1fr));}
.rank-stack .rank {min-height:0;}
[data-testid="stSelectbox"] [data-baseweb="select"] *,
[data-baseweb="popover"], [data-baseweb="popover"] *,
[role="listbox"], [role="listbox"] *, [role="option"], [role="option"] * {background-color:#fff !important;color:#07552d !important;}
[role="option"]:hover, [role="option"]:hover *, [role="option"][aria-selected="true"], [role="option"][aria-selected="true"] * {background-color:#eaf4e9 !important;}
@media(max-width:1050px){.detail,.right-panel{min-height:0}.rank-stack{grid-template-rows:repeat(4,auto)} iframe[title*="st_folium"]{height:clamp(340px,65vh,720px) !important;}}

/* Equal explicit border-box heights, independent of iframe title. */
@media (min-width:1051px) {
 :root {--body-height:clamp(860px, 90vh, 1200px);}
 .detail,.right-panel {height:var(--body-height);min-height:0;box-sizing:border-box;}
 .right-panel .rank-stack {flex:1 1 0;min-height:0;grid-template-rows:repeat(4,minmax(0,1fr));}
 .right-panel .rank {min-height:0;overflow:auto;}
 [data-testid="stCustomComponentV1"]:has(iframe), iframe[title*="st_folium"], iframe[title*="streamlit_folium"] {height:var(--body-height) !important;min-height:var(--body-height) !important;max-height:var(--body-height) !important;display:block;box-sizing:border-box;}
}
</style>''', unsafe_allow_html=True)

@st.cache_resource
def load_dashboard():
    base=Path(__file__).resolve().parent/'data'/'processed'
    stops=pd.read_csv(base/'bus_stops.csv',encoding='utf-8-sig',dtype={'stop_id':str,'district_code':str})
    geo=gpd.read_file(base/'districts.geojson').to_crs(4326)
    geo['district_code']=geo['district_code'].astype(str)
    bus,districts=create_models(stops,geo)
    return Visualizer(districts,bus)

v=load_dashboard()
df=v.prepare_map_data()
df['district_code']=df['district_code'].astype(str)
date=str(df.population_date.iloc[0])
if len(date)==8 and date.isdigit(): date=f'{date[:4]}-{date[4:6]}-{date[6:]}'
st.markdown(f'<div class="hero"><h1>🚌 서울시 버스 정류장 형평성 분석</h1><p>서울시 {len(df)}개 자치구별 버스 인프라 형평성 분석 · 기준일: {escape(date)}</p></div>',unsafe_allow_html=True)
if 'district_code' not in st.session_state:
    st.session_state.district_code=str(df.loc[df.district_name.eq('강남구'),'district_code'].iloc[0]) if df.district_name.eq('강남구').any() else str(df.district_code.iloc[0])
if 'map_district' not in st.session_state:
    st.session_state.map_district=None
if 'map_revision' not in st.session_state:
    st.session_state.map_revision=0
def request_search():
    st.session_state['_search_requested'] = True

controls=st.columns([2.6,0.9,2.5,0.65],gap='small',vertical_alignment='center')
with controls[0]:
    st.markdown('<div class="section map-heading">서울 자치구별 분석 지도</div>',unsafe_allow_html=True)
with controls[1]:
    reset=st.button('전체보기')
with controls[2]:
    query=st.text_input('정류장 또는 자치구 검색',placeholder='정류장 이름 / ID / 자치구',label_visibility='collapsed', key='search_query', on_change=request_search)
with controls[3]:
    clicked_search=st.button('검색', use_container_width=True)
search = st.session_state.pop('_search_requested', False) or clicked_search
if reset:
    st.session_state.map_district=None
    st.session_state.map_focus=None
    st.session_state.pop('selected_stop_id',None)
    st.session_state.map_revision+=1
if query.strip():
    q=query.strip().casefold()
    matches=[x for x in v.bus_stops if q in str(x.stop_name).casefold() or q==str(x.stop_id).casefold()]
    matches.sort(key=lambda x:(str(x.stop_name).casefold()!=q and str(x.stop_id).casefold()!=q,str(x.stop_name),str(x.stop_id)))
    district_match=df[df.district_name.str.casefold().eq(q)]
    if not district_match.empty:
        if search:
            code=str(district_match.iloc[0].district_code)
            st.session_state.update(district_code=code,map_district=code,map_focus=None,selected_stop_id=None)
            st.session_state.map_revision+=1
    elif matches:
        idx=st.selectbox('검색 결과 (정류장 이름 · ID · 자치구)',range(len(matches)),format_func=lambda i:f'{matches[i].stop_name} · {matches[i].stop_id} · {v.districts[str(matches[i].district_code)].district_name}',key='stop_choice_'+q)
        move = st.button('선택 정류장으로 이동')
        if search or move:
            stop=matches[idx]
            code=str(stop.district_code)
            st.session_state.update(district_code=code,map_district=code,map_focus=(float(stop.latitude),float(stop.longitude)),selected_stop_id=str(stop.stop_id))
            st.session_state.map_revision+=1
    elif search:
        st.warning('검색 결과가 없습니다.')
mapcol,detailcol,rankcol=st.columns([2.5,1.05,1.25],gap="small",vertical_alignment="top")
with mapcol:
    selected=st.session_state.map_district
    street_map=v.create_street_map(selected, focus=st.session_state.get('map_focus'), selected_stop_id=st.session_state.get('selected_stop_id'))
    from branca.element import Element
    street_map.get_root().header.add_child(Element('<style>html,body{height:100%;margin:0}.folium-map{height:100vh !important;}</style>'))
    event=st_folium(street_map,height=860,use_container_width=True,key=f'seoul-street-map-{st.session_state.map_revision}',returned_objects=['last_clicked'])
    click=event.get('last_clicked') if event else None
    if click:
        code=v.district_at(click['lat'],click['lng'])
        if code and code != selected:
            st.session_state.selected_stop_id=None
            st.session_state.district_code=code
            st.session_state.map_district=code
            st.session_state.map_focus=(float(click['lat']),float(click['lng']))
            st.session_state.map_revision+=1
            st.rerun()
with detailcol:
    row=df.loc[df.district_code.eq(st.session_state.district_code)].iloc[0]
    rank=int(df.equity_score.rank(ascending=False,method='min').loc[row.name])
    district=v.districts[str(row.district_code)]
    resident='정보 없음' if district.population is None else f'{district.population:,.0f} 명'
    st.markdown(f'''<div class="detail"><h3>선택 자치구</h3><h2>{escape(row.district_name)}</h2><div class="metricbox">종합 형평성 점수<b>{row.equity_score:.1f} 점</b>({len(df)}개 중 {rank}위)</div><div class="metricbox">생활인구 대비 공급수치<b>{row.stops_per_population:.1f} 개</b>(1만 명당 정류소 수)</div><div class="info">버스 정류소 수 <strong>{row.bus_stop_count:,} 개</strong></div><div class="info">생활인구 수 <strong>{row.living_population:,.0f} 명</strong></div><div class="info">면적 <strong>{row.area_km2:.1f} km²</strong></div><div class="info">주민등록 인구 <strong>{resident}</strong></div></div>''',unsafe_allow_html=True)
with rankcol:
    kpis=[]
    for label,value in [('총 버스 정류소 수',f'{df.bus_stop_count.sum():,} 개'),('총 생활인구 수',f'{df.living_population.sum():,.0f} 명'),('서울시 자치구 수',f'{len(df)} 개'),('평균 형평성 점수',f'{df.equity_score.mean():.1f} 점')]:
        kpis.append(f'<div class="kpi"><small>{label}</small><b>{value}</b></div>')
    rank_cards=[]
    for metric,title,unit in [('equity_score','종합 형평성','점'),('stops_per_population','생활인구 대비 공급','개')]:
        ranked=df.sort_values([metric,'district_code'],ascending=[False,True]).reset_index(drop=True)
        for low in (False,True):
            subset=ranked.tail(3).iloc[::-1] if low else ranked.head(3)
            rows=''.join(f'<div class="rrow"><span>{i+1}. {escape(r.district_name)}</span><span>{r[metric]:.1f} {unit}</span></div>' for i,r in subset.iterrows())
            rank_cards.append(f'<div class="rank {"low" if low else ""}"><h4>{"↓" if low else "🏆"} {title} {"LOW" if low else "TOP"} 3</h4>{rows}</div>')
    st.markdown('<div class="right-panel"><div class="section">서울시 요약 정보</div><div class="kpi-grid">'+''.join(kpis)+'</div><div class="section">형평성 순위</div><div class="rank-stack">'+''.join(rank_cards)+'</div></div>',unsafe_allow_html=True)
st.markdown('<div class="footer">More stops ≠ Higher equity　|　정류소 개수가 많다고 반드시 버스 인프라 형평성이 높은 것은 아닙니다.</div>',unsafe_allow_html=True)
