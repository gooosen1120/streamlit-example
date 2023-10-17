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
def getbase(start,end,title):
    sql = "SELECT c.品牌,c.店铺,c.季节,c."+title+"销量,c."+title+"业绩,c."+title+"折扣,c."+title+"业绩/d.总业绩*100 as "+title+"销售占比 from(SELECT a.store_name as '店铺',b.brand as '品牌',sum(num) as '"+title+"销量',sum(tprices) as '"+title+"业绩',sum(tprices)/sum(price*num) as '"+title+"折扣',seson as '季节' FROM salesInfo as a,people_info as b WHERE a.store_code = b.store_code and a.order_date>='"+str(start)+"' AND a.order_date<='"+str(end)+"' GROUP BY b.brand,a.store_name,a.seson) as c,(SELECT a.store_name as '店铺',b.brand as '品牌',sum(tprices) as '总业绩' FROM salesInfo as a,people_info as b WHERE a.store_code = b.store_code and a.order_date>='"+str(start)+"' AND a.order_date<='"+str(end)+"' GROUP BY b.brand,a.store_name) as d WHERE c.品牌 = d.品牌 AND c.店铺 = d.店铺 and "+title+"销量 <> 0"
    df = conn.query(sql)
    df = df.fillna('0')
    return df

start = st.date_input("开始日期")
end = st.date_input("结束日期")
lastStart = start - timedelta(days=7)
lastEnd = end - timedelta(days=7)


df = pd.DataFrame()
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
