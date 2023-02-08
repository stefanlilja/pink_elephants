# Imports
from sqlalchemy import create_engine
import pandas as pd
import os
from configparser import ConfigParser



# Function definitions
def data_file_dir():
    """
    Get file directory for data file

    Returns
    -------
    data_path : str
        File path to data file.

    """
    curr_path = os.path.dirname(os.path.realpath(__file__))
    data_path = curr_path + '\\data\\'
    
    return data_path





def read_data_from_csv(data_path):
    """
    Read data from file to pandas.DataFrame object

    Parameters
    ----------
    data_path : str
        File path to the CSV data file.

    Returns
    -------
    df : pandas.DataFrame
        DataFrame with all data from the file.

    """
    df = pd.read_csv(data_path + 'cleansed_elephants.csv', sep = ',')

    return df





def db_configuration(ini_file, section):
    """
    Configuration to the database

    Parameters
    ----------
    ini_file : str
        File name of ini-file with configuration data.
    section : str
        Section of the ini-file to look into.

    Returns
    -------
    conf : configparser.SectionProxy
        Configuration parser object to connect to the database.

    """
    config = ConfigParser()
    config.read(ini_file)
    conf = config[section]

    return conf





def create_engine_for_data(conf):
    """
    Creat engine for the data

    Parameters
    ----------
    conf : configparser.SectionProxy
        Configuration parser object to connect to the database.

    Returns
    -------
    engine : sqlalchemy.engine.base.Engine
        Engine object for connection with database.

    """
    engine = create_engine(f"postgresql://{conf['username']}:{conf['password']}@{conf['hostname']}/{conf['database']}")

    return engine





def create_clean_time_dataset(df):
    """
    Clean time data for insertion into the time table in the database 

    Parameters
    ----------
    df : pandas.DataFrame
        Raw dataset in pandas.DataFrame.

    Returns
    -------
    df_time : pandas.DataFrame
        Clean time data in pandas.DataFrame.

    """
    df_time = df[['timestamp', 'year', 'month', 'day', 'hour', 'minute']]
    df_time = df_time.rename(columns = {'timestamp': 'time_stamp'})
    df_time = df_time.drop_duplicates()

    return df_time





def create_clean_location_dataset(df):
    """
    Clean location data for insertion into the location table in the database  

    Parameters
    ----------
    df : pandas.DataFrame
        Raw dataset in pandas.DataFrame.

    Returns
    -------
    df_loc : pandas.DataFrame
        Clean location data in pandas.DataFrame.

    """
    df_loc = df[['lat', 'long', 'timestamp', 'external-temperature', 'tag_id']]
    df_loc = df_loc.rename(columns = {'lat': 'latitude',
                                      'long': 'longitude',
                                      'timestamp': 'time_stamp',
                                      'external-temperature': 'temperature'})

    return df_loc





def insert_into_db(engine, df_time, df_loc):
    """
    Insertion of data into database tables (time and location)

    Parameters
    ----------
    engine : sqlalchemy.engine.base.Engine
        Engine object for connection with database.
    df_time : pandas.DataFrame
        Clean time data in pandas.DataFrame.
    df_loc : pandas.DataFrame
        Clean location data in pandas.DataFrame.

    Returns
    -------
    None.

    """
    with engine.connect() as conn:
        df_time.to_sql('time', conn, if_exists = 'append', index = False)
        df_loc.to_sql('location_ping', conn, if_exists = 'append', index = False)





def main():
    """
    Main funtion / programmet
    """
    data_path = data_file_dir()
    df = read_data_from_csv(data_path)
    conf = db_configuration('database.ini', 'postgresql')
    engine = create_engine_for_data(conf)
    df_time = create_clean_time_dataset(df)
    df_loc = create_clean_location_dataset(df)
    insert_into_db(engine, df_time, df_loc)
    




# Main program
if __name__ == '__main__':
    main()

