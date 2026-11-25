"""서울시 버스 인프라 형평성 대시보드."""
from pathlib import Path
from html import escape
import geopandas as gpd
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium
from utils.model_factory import create_models
from utils.visualizer import Visualizer

st.set_page_config(page_title='서울시 버스 인프라 형평성', page_icon='🚌', layout='wide')
st.markdown('''<style>
.block-container{max-width:1800px;padding:1rem 1.2rem 2rem} [data-testid="stAppViewContainer"]{background:#f5f8f6;color:#17251d} .hero{background:#00502e;color:white;padding:18px 24px;border-radius:8px;margin-bottom:10px}.hero h1{color:white;font-size:30px;margin:0;padding:0}.hero p{margin:3px 0;color:white}.kpi,.detail,.rank{background:white;border:1px solid #d6e0da;border-radius:14px;padding:12px 16px;color:#17251d}.kpi b{font-size:26px;display:block}.kpi small{font-weight:600}.rank{padding:0;overflow:hidden;margin-bottom:10px}.rank h4{background:#edf7e9;color:#07552d;margin:0;padding:8px 12px;font-size:16px}.rank.low h4{background:#fff1e7;color:#c43c12}.rrow{display:flex;justify-content:space-between;padding:5px 12px;font-weight:650}.rrow span:last-child{color:#07552d}.low .rrow span:last-child{color:#c43c12}.detail h3{background:#07552d;color:white;padding:10px;margin:-12px -16px 12px;border-radius:12px 12px 0 0}.detail h2{font-size:32px;color:#111}.metricbox{border:1px solid #cbd8d0;border-radius:12px;padding:12px;margin:10px 0}.metricbox b{display:block;font-size:28px;color:#07552d}.info{display:flex;justify-content:space-between;border-bottom:1px solid #e5ebe7;padding:8px 0}.footer{background:white;border-radius:10px;padding:14px;color:#07552d;font-weight:600} .section{font-size:20px;font-weight:750;color:#123c26;margin:8px 0}
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
st.markdown(f'<div class="hero"><h1>🚌 서울시 버스 인프라 형평성 대시보드</h1><p>서울시 {len(df)}개 자치구별 버스 인프라 형평성 분석 · 기준일: {escape(date)}</p></div>',unsafe_allow_html=True)
for col,(label,value) in zip(st.columns(4), [('총 버스 정류소 수',f'{df.bus_stop_count.sum():,} 개'),('총 생활인구 수',f'{df.living_population.sum():,.0f} 명'),('서울시 자치구 수',f'{len(df)} 개'),('평균 형평성 점수',f'{df.equity_score.mean():.1f} 점')]):
    col.markdown(f'<div class="kpi"><small>{label}</small><b>{value}</b></div>',unsafe_allow_html=True)

if 'district_code' not in st.session_state:
    st.session_state.district_code=str(df.loc[df.district_name.eq('강남구'),'district_code'].iloc[0]) if df.district_name.eq('강남구').any() else str(df.district_code.iloc[0])
if 'map_district' not in st.session_state:
    st.session_state.map_district=None
if 'map_revision' not in st.session_state:
    st.session_state.map_revision=0
mapcol,detailcol,rankcol=st.columns([2.5,1.05,1.25],gap='small')
with mapcol:
    st.markdown('<div class="section">서울시 자치구별 분석 지도</div>',unsafe_allow_html=True)
    if st.button('서울 전체 보기'):
        st.session_state.map_district=None
        st.session_state.map_focus=None
        st.session_state.map_revision+=1
    selected=st.session_state.map_district
    st.caption('지도에서 원하는 자치구를 클릭하세요.' if selected is None else '정류장 아이콘을 클릭하면 이름과 ID를 확인할 수 있습니다.')
    event=st_folium(v.create_street_map(selected, focus=st.session_state.get('map_focus')),height=565,use_container_width=True,key=f'seoul-street-map-{st.session_state.map_revision}',returned_objects=['last_clicked'])
    click=event.get('last_clicked') if event else None
    if click:
        code=v.district_at(click['lat'],click['lng'])
        if code and code != selected:
            st.session_state.district_code=code
            st.session_state.map_district=code
            st.session_state.map_focus=(float(click['lat']),float(click['lng']))
            st.session_state.map_revision+=1
            st.rerun()
        elif not code:
            st.caption('서울시 자치구 내부를 클릭해 주세요.')
with detailcol:
    row=df.loc[df.district_code.eq(st.session_state.district_code)].iloc[0]
    rank=int(df.equity_score.rank(ascending=False,method='min').loc[row.name])
    district=v.districts[str(row.district_code)]
    resident='정보 없음' if district.population is None else f'{district.population:,.0f} 명'
    st.markdown(f'''<div class="detail"><h3>선택한 자치구</h3><h2>{escape(row.district_name)}</h2><div class="metricbox">종합 형평성 점수<b>{row.equity_score:.1f} 점</b>({len(df)}개 중 {rank}위)</div><div class="metricbox">생활인구 대비 공급수치<b>{row.stops_per_population:.1f} 개</b>(1만 명당 정류소 수)</div><div class="info">버스 정류소 수 <strong>{row.bus_stop_count:,} 개</strong></div><div class="info">생활인구 수 <strong>{row.living_population:,.0f} 명</strong></div><div class="info">면적 <strong>{row.area_km2:.1f} km²</strong></div><div class="info">주민등록 인구 <strong>{resident}</strong></div></div>''',unsafe_allow_html=True)
with rankcol:
    for metric,title,unit in [('equity_score','종합 형평성','점'),('stops_per_population','생활인구 대비 공급','개')]:
        ranked=df.sort_values([metric,'district_code'],ascending=[False,True]).reset_index(drop=True)
        for low in (False,True):
            subset=ranked.tail(3).iloc[::-1] if low else ranked.head(3)
            rows=''.join(f'<div class="rrow"><span>{i+1}. {escape(r.district_name)}</span><span>{r[metric]:.1f} {unit}</span></div>' for i,r in subset.iterrows())
            st.markdown(f'<div class="rank {"low" if low else ""}"><h4>{"↓" if low else "🏆"} {title} {"LOW" if low else "TOP"} 3</h4>{rows}</div>',unsafe_allow_html=True)
st.markdown('<div class="footer">More stops ≠ Higher equity　|　정류소 개수가 많다고 반드시 버스 인프라 형평성이 높은 것은 아닙니다.</div>',unsafe_allow_html=True)
