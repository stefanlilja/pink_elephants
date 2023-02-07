import sqlalchemy
import pandas as pd
import os

curr_path = os.path.dirname(os.path.realpath(__file__))
data_path = curr_path + '\\data\\'

df = pd.read_csv(data_path + 'cleansed_elephants.csv', sep=',')

engine = sqlalchemy.create_engine('postgresql+psycopg2://postgres:postgres@localhost/elephant')

con = engine.connect()

insert = con.execute()

result = con.execute('SELECT * FROM time;')

print(df)

