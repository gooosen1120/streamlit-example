import datetime
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
def getbase():
    sql = "SELECT store_code as '店号',store_name as '店名' FROM inventory GROUP BY store_code"
    df = conn.query(sql)
    df = df.fillna('0')
    return df

def getAllSale(sn,size):
    sql = "SELECT store_code as '店号',sum(num) as 总销售数量 FROM salesInfo   WHERE sn like '%"+str(sn)+"%' AND size like '%"+size+"%' GROUP BY store_code"
    st.write(sql)
    df = conn.query(sql)
    df = df.fillna('0')
    return df

def getAllInve(sn,size):
    sql = "SELECT store_code as '店号',size_name as 尺寸名,sum(num) as 总库存数量 FROM inventory   WHERE sn like '%"+str(sn)+"%'  AND size like '%"+size+"%' GROUP BY store_code,size_name"
    st.write(sql)
    df = conn.query(sql)
    df = df.fillna('0')
    return df

def getLast(start,end,sn,title,size):
    sql = "SELECT store_code as '店号',sum(num) as "+str(title)+"销售数量 FROM salesInfo   WHERE sn like '%"+str(sn)+"%' AND size like '%"+size+"%'  AND order_date>='"+str(start)+"' AND order_date<='"+str(end)+"' GROUP BY store_code"
    #st.write(sql)
    df = conn.query(sql)
    df = df.fillna('0')
    return df

sn = st.text_input("款号")
sesons = st.multiselect(
    '选择尺码',
    ['155','160','165', '170'])
#st.write(len(sesons))
seek = st.button("查询")

today = datetime.date.today()
week_start = today -timedelta(days = today.weekday())
week_end = today +timedelta(days = 6-today.weekday())

this_month_end = datetime.date(today.year, today.month+1, 1)- datetime.timedelta(1)
this_month_start = datetime.date(today.year, today.month, 1)

last_month_end = datetime.date(today.year, today.month, 1) - datetime.timedelta(1)
last_month_start = datetime.date(last_month_end.year, last_month_end.month, 1)

def getall(sn,size):
    df = getbase()
    df2 = getAllSale(sn,str(size))
    df = pd.merge(df, df2, on = "店号", how = 'outer')
    df2 = getLast(week_start, week_end, sn, str(size)+'本周',str(size))
    df = pd.merge(df, df2, on = "店号", how = 'outer')
    df2 = getLast(this_month_start, this_month_end, sn, str(size)+'本月',str(size))
    df = pd.merge(df, df2, on = "店号", how = 'outer')
    df2 = getLast(last_month_start, last_month_end, sn, str(size)+'上月',str(size))
    df = pd.merge(df, df2, on = "店号", how = 'outer')
    df2 = getAllInve(sn,str(size))
    df = pd.merge(df, df2, on = "店号", how = 'outer')
    df = df.fillna(0)
    df = df.drop(df[(df.总库存数量 == 0)].index)
    return df

if seek:
    df = pd.DataFrame()
    df1 = pd.DataFrame()
    df2 = pd.DataFrame()
    df3 = pd.DataFrame()
    df4 = pd.DataFrame()
    if len(sesons) == 0:
        df = getall(sn, '')
    else:
        if '155' in sesons:
            df1 = getall(sn, '36')
        if '160' in sesons:
            df2 = getall(sn, '38')
        if '165' in sesons:
            df3= getall(sn, '40')
        if '170' in sesons:
            df4 = getall(sn, '42')
        df=getbase()
        if not df1.empty:
            df = pd.merge(df, df1, on = ["店号", '店名'], how = 'outer')
            df = df.fillna(0)
            df = df.drop(df[(df.总库存数量 == 0)].index)
        if not df2.empty:
            df = pd.merge(df, df2, on = ["店号", '店名'], how = 'outer')
            df = df.fillna(0)
            df = df.drop(df[(df.总库存数量 == 0)].index)
        if not df3.empty:
            df = pd.merge(df, df3, on = ["店号", '店名'], how = 'outer')
            df = df.fillna(0)
            st.dataframe(df)
            df = df.drop(df[(df.总库存数量 == 0)].index)
        if not df4.empty:
            df = pd.merge(df, df4, on = ["店号", '店名'], how = 'outer')
            df = df.fillna(0)
            df = df.drop(df[(df.总库存数量 == 0)].index)
    st.dataframe(df)