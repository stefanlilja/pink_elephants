from sqlalchemy import create_engine
from configparser import ConfigParser
import pandas as pd

def read_from_db():
    """
    Read and return both tables from the sql database as pandas DataFrames.

    Returns
    -------
    df_main : pandas.DataFrame
        location_ping table in pandas.DataFrame.
    
    df_time : pandas.DataFrame
        time table in pandas.DataFrame

    """
    config = ConfigParser()
    config.read('database.ini')
    conf = config['postgresql']

    engine = create_engine(f"postgresql://{conf['username']}:{conf['password']}@{conf['hostname']}/{conf['database']}")

    with engine.connect() as conn:
        df_main = pd.read_sql_table('location_ping', conn)
        df_time = pd.read_sql_table('time', conn)

    return df_main, df_time