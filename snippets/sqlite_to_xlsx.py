import pandas as pd
import sqlite3

# Read sqlite query results into a pandas DataFrame
con = sqlite3.connect("bot.db")
user_name = 'abc'
df = pd.read_sql_query('''SELECT 
datetime,
emotions,
energy,
attention,
conscientiousness,
planning,
stress,
regime,
body,
comment,
rating
FROM records WHERE user_name='%s' ''' % user_name, con)

# Verify that result of SQL query is stored in the dataframe
print(df.head())

#df.to_csv('dump.csv', encoding='utf-8', sep='\t')
df.to_excel('dump.xlsx', index=None, header=True)

con.close()
