from sqlalchemy import Table, Column, String, MetaData, create_engine, TIMESTAMP, Integer
import pandas as pd
import os
from configparser import ConfigParser

curr_path = os.path.dirname(os.path.realpath(__file__))
data_path = curr_path + '\\data\\'

df = pd.read_csv(data_path + 'cleansed_elephants.csv', sep=',')

config = ConfigParser()
config.read('database.ini')
conf = config['postgresql']

engine = create_engine(f"postgresql://{conf['username']}:{conf['password']}@{conf['hostname']}/{conf['database']}")

df_time = df[['timestamp', 'year', 'month', 'day', 'hour', 'minute']]
df_time = df_time.rename(columns={'timestamp': 'time_stamp'})
df_time.drop_duplicates(inplace=True)

df_loc = df[['lat', 'long', 'timestamp', 'external-temperature', 'tag_id']]
df_loc.rename(
    columns={
        'lat': 'latitude',
        'long': 'longitude',
        'timestamp': 'time_stamp',
        'external-temperature': 'temperature'
    },
    inplace=True
)

with engine.connect() as conn:
    df_time.to_sql('time', conn, if_exists='append', index=False)
    df_loc.to_sql('location_ping', conn, if_exists='append', index=False)

# meta = MetaData(engine)  
# time_table = Table('time', meta,  
#                        Column('time_stamp', TIMESTAMP),
#                        Column('year', Integer),
#                        Column('month', Integer),
#                        Column('day', Integer),
#                        Column('hour', Integer),
#                        Column('minute', Integer)
# )


# with engine.connect() as conn:
#     for i in range(len(df)):
#         insert_statement = time_table.insert().values(
#             time_stamp=df.timestamp[i],
#             year=df.year[i],
#             month=df.month[i],
#             day=df.day[i],
#             hour=df.hour[i],
#             minute=df.minute[i]
#             )
#         conn.execute(insert_statement)

