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
sesons = st.multiselect(
    '选择季节',
    ['新品春', '新品夏', '新品秋', '新品冬'],
    ['新品春', '新品夏',])
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
    if '新品春' in sesons:
        sqla = "SELECT store_code as '店号',SUM(tprices) as '新品春业绩' FROM salesInfo  WHERE order_date>='"+str(start)+"' AND order_date<='"+str(end)+"' and year = '"+str(start.year)+"' and seson = '"+"春季"+"' GROUP BY store_code"
        dfa = conn.query(sqla)
    if '新品夏' in sesons:
        sqlb = "SELECT store_code as '店号',SUM(tprices) as '新品夏业绩' FROM salesInfo  WHERE order_date>='"+str(start)+"' AND order_date<='"+str(end)+"' and year = '"+str(start.year)+"' and seson = '"+"夏季"+"' GROUP BY store_code"
        dfb = conn.query(sqlb)
    if '新品秋' in sesons:
        sqlc = "SELECT store_code as '店号',SUM(tprices) as '新品秋业绩' FROM salesInfo  WHERE order_date>='"+str(start)+"' AND order_date<='"+str(end)+"' and year = '"+str(start.year)+"' and seson = '"+"秋季"+"' GROUP BY store_code"
        dfc = conn.query(sqlc)
    if '新品冬' in sesons:
        sqld = "SELECT store_code as '店号',SUM(tprices) as '新品冬业绩' FROM salesInfo  WHERE order_date>='"+str(start)+"' AND order_date<='"+str(end)+"' and year = '"+str(start.year)+"' and seson = '"+"冬季"+"' GROUP BY store_code"
        dfd = conn.query(sqld)

    sql = "SELECT a.店号,a.店名,a.店级,a.业绩,a.吊牌,a.折扣,b.业绩 as '上周' , (a.业绩/b.业绩-1) as 环比  ,c.业绩 as '同期', (a.业绩/c.业绩-1)*100  as '同比'  FROM (SELECT store_code as '店号',store_name as '店名',level as '店级',SUM(tprices) as '业绩',sum(price) as '吊牌',sum(tprice)/sum(price) as '折扣' FROM salesInfo WHERE order_date>='"+str(start)+"' AND order_date<='"+str(end)+"' GROUP BY store_code) a, (SELECT store_code as '店号',store_name as '店名',level as '店级',SUM(tprices) as '业绩' FROM salesInfo WHERE order_date>='"+str(lastStart)+"' AND order_date<='"+str(lastEnd)+"' GROUP BY store_code) b,(SELECT store_code as '店号',store_name as '店名',level as '店级',SUM(tprices) as '业绩' FROM salesInfo WHERE order_date>='"+str(lastYearstart)+"' AND order_date<='"+str(lastYearEnd)+"' GROUP BY store_code) c WHERE a.店号 = b.店号 and a.店号 = c.店号"
    #st.write(sql)
    df = conn.query(sql)
    if not dfa.empty:
        df = pd.merge(df,dfa,on = "店号", how='outer')
        df.eval('新品春贡献率  = 新品春业绩/业绩',inplace = True)
    if not dfb.empty:
        df = pd.merge(df, dfb, on = "店号", how='outer')
        df.eval('新品夏贡献率  = 新品夏业绩/业绩', inplace = True)
    if not dfc.empty:
        df = pd.merge(df, dfc, on = "店号", how='outer')
        df.eval('新品秋贡献率  = 新品秋业绩/业绩', inplace = True)
    if not dfd.empty:
        df = pd.merge(df, dfd, on = "店号", how='outer')
        df.eval('新品冬贡献率  = 新品冬业绩/业绩', inplace = True)
    df.fillna(0, inplace = True)
    st.dataframe(df)
    st.caption("店铺销售柱状图")
    st.bar_chart(df,x = "店名",y = "业绩")