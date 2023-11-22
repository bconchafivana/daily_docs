import pandas as pd
from db_conn import engine_ds , engine_public, conn
from queryes import daily_query, query_mem

#read documents per each day
daily = pd.read_sql(daily_query, engine_public)

#financing factoring maybe is not good, so we keep just the one in mem
daily = daily.drop(columns = ['financing_factoring'])
#documents per each day
docs = str(tuple(daily.document_id.tolist()))

mem = pd.read_sql(query_mem + docs, conn)

output = pd.merge(mem, daily, left_on = 'document_id', right_on = 'document_id')

output.to_sql('monthly_closure', engine_ds, index=False, if_exists='replace')
print("monthly_closure uploaded")