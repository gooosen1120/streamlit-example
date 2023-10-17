from datetime import timedelta
from datetime import date
import streamlit as st
import pandas as pd
conn = st.experimental_connection(
    "local_db",
    type="sql",
    url="mysql://root:il247486@101.42.5.49:3306/LAGOGO"
)

@st.cache_data
def cover_df(df):
    return df.to_csv().encode('utf_8_sig')
start = st.date_input("开始日期")
end = st.date_input("结束日期")
genre = st.radio(
    "查询分类",
    ('按品牌汇总', '按人员汇总'))
lastStart = start - timedelta(days=7)
lastEnd = end - timedelta(days=7)
weekNo = start.isocalendar().week
lastYearstart = date.fromisocalendar(start.year-1, weekNo, 1)
lastYearEnd =  date.fromisocalendar(start.year-1, weekNo, 7)

df = pd.DataFrame()
dfa = pd.DataFrame()
dfb = pd.DataFrame()
dfc = pd.DataFrame()
dfd = pd.DataFrame()
col1,col2 = st.columns(2)
with col1 :
    seek = st.button('查询')

with col2:
    csv = cover_df(df)
    st.download_button(
        label="下载",
        data=csv,
        file_name='a.csv',
        mime='text/csv'
    )
if seek:
    if genre == "按品牌汇总":
        #st.write(sql)
        sql = "SELECT a.品牌,a.业绩,a.吊牌,a.折扣,b.业绩 as '上周' , (a.业绩/b.业绩-1) as 环比 ,c.业绩 as '同期', (a.业绩/c.业绩-1)*100 as '同比' , d.业绩 as '新品业绩',d.业绩/a.业绩 as '新品贡献率' FROM (SELECT brand as '品牌',SUM(salesInfo.tprices) as '业绩',sum(price) as '吊牌',sum(tprices)/sum(price) as '折扣' FROM salesInfo ,people_info WHERE order_date>='" + str(
            start) + "' AND order_date<='" + str(
            end) + "' AND salesInfo.store_code = people_info.store_code GROUP BY brand) a, (SELECT brand as '品牌',SUM(tprices) as '业绩' FROM salesInfo,people_info WHERE order_date>='" + str(
            lastStart) + "' AND order_date<='" + str(
            lastEnd) + "' AND salesInfo.store_code = people_info.store_code GROUP BY brand) b,(SELECT brand as '品牌',SUM(tprices) as '业绩' FROM salesInfo,people_info WHERE order_date>='" + str(
            lastYearstart) + "' AND order_date<='" + str(
            lastYearEnd) + "' AND salesInfo.store_code = people_info.store_code GROUP BY brand) c,(SELECT brand as '品牌',SUM(salesInfo.tprices) as '业绩' FROM salesInfo ,people_info WHERE order_date>='"+str(start)+"' AND order_date<='"+str(end)+"' AND salesInfo.store_code = people_info.store_code AND year = '" + str(
            start.year) + "' GROUP BY brand) d WHERE a.品牌 = b.品牌 and a.品牌 = c.品牌 and a.品牌 = d.品牌"
        #st.write(sql)
    if genre == "按人员汇总":
        sql = "SELECT a.主管,a.业绩,a.吊牌,a.折扣,b.业绩 as '上周' , (a.业绩/b.业绩-1) as 环比 ,c.业绩 as '同期', (a.业绩/c.业绩-1)*100 as '同比' , d.业绩 as '新品业绩',d.业绩/a.业绩 as '新品贡献率' FROM (SELECT people_info.people as '主管',SUM(salesInfo.tprices) as '业绩',sum(price) as '吊牌',sum(tprices)/sum(price) as '折扣' FROM salesInfo ,people_info WHERE order_date>='" + str(
            start) + "' AND order_date<='" + str(
            end) + "' AND salesInfo.store_code = people_info.store_code GROUP BY people_info.people) a, (SELECT people_info.people as '主管',SUM(tprices) as '业绩' FROM salesInfo,people_info WHERE order_date>='" + str(
            lastStart) + "' AND order_date<='" + str(
            lastEnd) + "' AND salesInfo.store_code = people_info.store_code GROUP BY people_info.people) b,(SELECT people_info.people as '主管',SUM(tprices) as '业绩' FROM salesInfo,people_info WHERE order_date>='" + str(
            lastYearstart) + "' AND order_date<='" + str(
            lastYearEnd) + "' AND salesInfo.store_code = people_info.store_code GROUP BY people_info.people) c,(SELECT people_info.people as '主管',SUM(salesInfo.tprices) as '业绩' FROM salesInfo ,people_info WHERE order_date>='"+str(start)+"'  AND order_date<='"+str(end)+"' AND salesInfo.store_code = people_info.store_code AND year = '" + str(
            start.year) + "' GROUP BY people_info.people) d WHERE a.主管 = b.主管 and a.主管 = c.主管 and a.主管 = d.主管"
    df = conn.query(sql)
    st.dataframe(df)
