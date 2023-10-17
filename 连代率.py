from datetime import timedelta
from datetime import date
import calendar
import streamlit as st
import pandas as pd
conn = st.experimental_connection(
    "local_db",
    type="sql",
    url="mysql://root:il247486@101.42.5.49:3306/LAGOGO"
)
def getDf (start,end,title):
    temp = ""
    if title == "周":
        temp = ",store_name as '店名'"

    sql = "SELECT a.store_code as '店号'" + temp + ",a." + title + "开票数,b." + title + "销售件数,b." + title + "销售件数/a." + title + "开票数 as '" + title + "连带率' FROM (SELECT store_code,store_name,count(order_no) as '" + title + "开票数' FROM salesInfo WHERE id in (SELECT max(id) FROM salesInfo WHERE  order_date>='" + str(
        start) + "' AND order_date<='" + str(
        end) + "' GROUP BY order_no HAVING sum(num)>=1)  GROUP BY store_code) a, (SELECT store_code,sum(nums) as '" + title + "销售件数' FROM (SELECT store_code,sum(num) as 'nums' FROM salesInfo WHERE order_date>='" + str(
        start) + "' AND order_date<='" + str(
        end) + "' GROUP BY store_code,order_no HAVING sum(num)>=1) as x GROUP BY store_code) b WHERE a.store_code = b.store_code"


    df = conn.query(sql)
    sql = "SELECT a.store_code as '店号',a." + title + "2件以上开票数,b." + title + "2件以上销售件数 FROM (SELECT store_code,store_name,count(order_no) as '" + title + "2件以上开票数' FROM salesInfo WHERE id in (SELECT max(id) FROM salesInfo WHERE  order_date>='" + str(
        start) + "' AND order_date<='" + str(
        end) + "' GROUP BY order_no HAVING sum(num)>=2) GROUP BY store_code) a, (SELECT store_code,sum(nums) as '" + title + "2件以上销售件数' FROM (SELECT store_code,sum(num) as 'nums' FROM salesInfo WHERE order_date>='" + str(
        start) + "' AND order_date<='" + str(
        end) + "' GROUP BY store_code,order_no HAVING sum(num)>=2) as x GROUP BY store_code) b WHERE a.store_code = b.store_code"

    df2 = conn.query(sql)
    df = pd.merge(df, df2, on="店号", how='outer')
    sql = "SELECT a.店号,b.开票数/a.开票数 as '" + title + "连带比' FROM (SELECT store_code as '店号',store_name,count(order_no) as '开票数' FROM salesInfo WHERE id in (SELECT max(id) FROM salesInfo WHERE  order_date>='" + str(
        start) + "' AND order_date<='" + str(
        end) + "' GROUP BY order_no HAVING sum(num)>=1)GROUP BY store_code) a, (SELECT store_code as '店号',store_name,count(order_no) as '开票数' FROM salesInfo WHERE id in (SELECT max(id) FROM salesInfo WHERE order_date>='" + str(
        start) + "' AND order_date<='" + str(end) + "'  GROUP BY order_no HAVING sum(num)>=2) GROUP BY store_code) b WHERE a.店号 = b.店号"
    #st.write(sql)
    df3 = conn.query(sql)
    df = pd.merge(df, df3, on="店号", how='outer')
    df = df.fillna('0')
    return df

@st.cache_data
def cover_df(df):
    return df.to_csv().encode('utf_8_sig')
start = st.date_input("开始日期")
end = st.date_input("结束日期")
m = calendar.monthrange(start.year, start.month)
mstart = start.replace(day=1)
mend = start.replace(day=m[1])
#st.write(mstart)
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
if seek:
    df = getDf(start,end,'周')
    df2 = getDf(mstart,mend,'月')
    df = pd.merge(df, df2, on="店号", how='outer')
    #df.eval('连带比 = 2件以上开票数/开票数', inplace=True)
    st.dataframe(df)