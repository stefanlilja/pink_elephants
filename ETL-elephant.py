import pandas as pd
import os

curr_path = os.path.dirname(os.path.realpath(__file__))
work_dir = curr_path + '/data/'

df = pd.read_csv('ThermochronTracking Elephants Kruger 2007.csv')

df = df.rename(
    columns={'tag-local-identifier': 'tag_id',
             'location-lat': 'lat',
             'location-long': 'long',
             })

df_new = df.copy()
df_new[['date', 'time']] = df_new.timestamp.str.split(" ", expand=True)
df_new[['year', 'month', 'day']] = df_new.date.str.split("-", expand=True)
df_new[['hour', 'minute']] = df_new.time.str.split(":", expand=True).iloc[:, [0, 1]]


df_db = df_new.drop(
    columns=['event-id',
             'visible',
             'sensor-type',
             'individual-local-identifier',
             'individual-taxon-canonical-name',
             'study-name',
             'date',
             'time'])
print(df_db)


df_db.to_csv(work_dir + 'cleansed_elephants.csv')

