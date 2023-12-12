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
table_name = 'datascience.monthly_closure'

# Replace 'read_user_bi' and 'read_user_risk' with the actual usernames
users_to_grant = ['read_user_bi', 'read_user_risk']

# Generate and execute the GRANT commands for each user
for user in users_to_grant:
    grant_command = f"GRANT SELECT ON TABLE {table_name} TO {user}"
    with engine_ds.connect() as connection:
        connection.execute(grant_command)
print("monthly_closure uploaded")
