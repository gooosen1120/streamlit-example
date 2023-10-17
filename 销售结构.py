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

def getbase(start,end):
    sql = "SELECT b.people,b.brand,a.store_code as '店号',a.store_name as '店名',a.level as '店铺级别' FROM (SELECT store_code,store_name ,level FROM salesInfo WHERE order_date>='"+str(start)+"' AND order_date<='"+str(end)+"' GROUP BY store_code) as a,people_info as b WHERE a.store_code = b.store_code"
    df = conn.query(sql)
    #st.text(sql)
    df = df.fillna('0')
    return df
def getall(start,end):
    sql = "SELECT store_code as '店号', sum(num) as '整体销量',sum(tprices) as '整体业绩',sum(price) as '整体吊牌额',sum(tprice)/sum(price) as '整体折扣',sum(tprices)/sum(num) as '整体客单价' FROM salesInfo WHERE order_date>='"+str(start)+"' AND order_date<='"+str(end)+"' GROUP BY store_code"
    df = conn.query(sql)
    df = df.fillna('0')
    return df
def getother(start,end):
    sql = "SELECT store_code as '店号', sum(num) as '其它销量',sum(tprices) as '其它业绩',sum(price) as '其它吊牌额',sum(tprice)/sum(price) as '其它折扣' FROM salesInfo WHERE order_date>='" + str(
        start) + "' AND order_date<='" + str(end) + "' and year <> 2023 and year <> 2022 GROUP BY store_code"
    df = conn.query(sql)
    df = df.fillna('0')
    return df

def getlastyear(start,end):
    lastyear = end.year-1
    sql = "SELECT a.store_code as '店号',a.往年销量,a.往年业绩,a.往年吊牌额,a.往年折扣,b.往年库存 FROM (SELECT store_code, sum(num) as '往年销量',sum(tprices) as '往年业绩',sum(price) as '往年吊牌额',sum(tprice)/sum(price) as '往年折扣' FROM salesInfo WHERE order_date>='"+str(start)+"' AND order_date<='"+str(end)+"' and year <> "+str(end.year)+" GROUP BY store_code) a,(SELECT store_code,sum(num) as '往年库存' FROM inventory WHERE year = "+str(lastyear)+" GROUP BY store_code) b WHERE a.store_code = b.store_code"
    #st.write(sql)
    df = conn.query(sql)
    df = df.fillna('0')
    return df

def getdf(start,end,season):

    sql = "SELECT a.store_code as '店号',a."+season+"销量,a."+season+"业绩,a."+season+"吊牌额,a."+season+"折扣,b."+season+"库存 FROM (SELECT store_code, sum(num) as '"+season+"销量',sum(tprices) as '"+season+"业绩',sum(price) as '"+season+"吊牌额',sum(tprice)/sum(price) as '"+season+"折扣' FROM salesInfo WHERE order_date>='"+str(start)+"' AND order_date<='"+str(end)+"' and seson = '"+str(season)+"' and year = "+str(end.year)+" GROUP BY store_code) a,(SELECT store_code,sum(num) as '"+season+"库存' FROM inventory WHERE season = '"+str(season)+"' and year = "+str(end.year)+"  GROUP BY store_code) b WHERE a.store_code = b.store_code"
    #st.write(sql)
    df = conn.query(sql)
    df = df.fillna('0')
    return df
start = st.date_input("开始日期")
end = st.date_input("结束日期")
sesons = st.multiselect(
    '选择季节',
    ['其它','往年','春季', '夏季', '秋季', '冬季'])
df = pd.DataFrame()
dfo = pd.DataFrame()
dfl = pd.DataFrame()
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
    df = getbase(start,end)
    df2 = getall(start,end)
    df = pd.merge(df, df2, on="店号", how='outer')
    tj = ['店号']
    if '其它' in sesons:
        dfo = getother(start,end)
        tj.append('其它业绩')
    if '往年' in sesons:
        dfl = getlastyear(start,end)
        tj.append('往年业绩')
    if '春季' in sesons:
        dfa = getdf(start,end,'春季')
        tj.append('春季业绩')
    if '夏季' in sesons:
        dfb = getdf(start,end,'夏季')
        tj.append('夏季业绩')
    if '秋季' in sesons:
        dfc = getdf(start,end,'秋季')
        tj.append('秋季业绩')
    if '冬季' in sesons:
        dfd = getdf(start,end,'冬季')
        tj.append('冬季业绩')
    if not dfo.empty:
        df = pd.merge(df,dfo,on = "店号", how='outer')
        df.eval('其它贡献率  = 其它业绩/整体业绩', inplace = True)
    if not dfl.empty:
        df = pd.merge(df, dfl, on = "店号", how='outer')
        df.eval('往年存销  = 往年库存/往年销量', inplace = True)
    if not dfa.empty:
        df = pd.merge(df, dfa, on = "店号", how='outer')
        df.eval('春季存销  = 春季库存/春季销量', inplace = True)
    if not dfb.empty:
        df = pd.merge(df, dfb, on = "店号", how='outer')
        df.eval('夏季存销  = 夏季库存/夏季销量', inplace = True)
    if not dfc.empty:
        df = pd.merge(df, dfc, on = "店号", how='outer')
        df.eval('秋季存销  = 秋季库存/秋季销量', inplace = True)
    if not dfd.empty:
        df = pd.merge(df, dfd, on = "店号", how='outer')
        df.eval('冬季存销  = 冬季库存/冬季销量', inplace = True)
    df.fillna(0, inplace=True)
    st.dataframe(df)
    #newdf = df[tj]
    #st.dataframe(newdf)
    tj.remove('店号')
    #st.bar_chart(data = newdf,x = '店号', y = tj)

    csv = cover_df(df)
    st.download_button(
        label = "下载",
        data = csv,
        file_name = 'a.csv',
        mime = 'text/csv'
    )