# Imports
import pandas as pd
from load_to_db import data_file_dir



# Function definitions
def read_raw_data_from_csv(work_dir):
    """
    Read raw data from CSV file 

    Parameters
    ----------
    work_dir : str
        File path to the CSV data file.

    Returns
    -------
    df : pandas.DataFrame
        DataFrame with all data from the file.

    """
    df = pd.read_csv(work_dir + 'ThermochronTracking Elephants Kruger 2007.csv')

    return df





def rename_columns(df):
    """
    Rename columns in the DataFrame

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame with data.

    Returns
    -------
    df : pandas.DataFrame
        DataFrame with data where columns are named as the columns in the database.

    """
    df = df.rename(columns = {'tag-local-identifier': 'tag_id',
                            'location-lat': 'lat',
                            'location-long': 'long'})
    
    return df





def split_timestamp(df):
    """
    Split timestamp values in the 'timestamp' column to 'year', 'month', 'day', 'hour', 'minute'

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame with data.

    Returns
    -------
    df_new : pandas.DataFrame
        DataFrame with timestamp column splitted into separate columns for year, month, day, hour, minute.

    """
    df_new = df.copy()
    df_new[['date', 'time']] = df_new.timestamp.str.split(" ", expand = True)
    df_new[['year', 'month', 'day']] = df_new.date.str.split("-", expand = True)
    df_new[['hour', 'minute']] = df_new.time.str.split(":", expand = True).iloc[:, [0, 1]]

    return df_new





def clean_data(df_new):
    """
    Clean dataframe from unnecessary columns

    Parameters
    ----------
    df_new : pandas.DataFrame
        DataFrame with data.

    Returns
    -------
    df_db : pandas.DataFrame
        DataFrame cleanded and ready for insertion into database.

    """
    df_db = df_new.drop(columns = ['event-id',
                                   'visible',
                                   'sensor-type',
                                   'individual-local-identifier',
                                   'individual-taxon-canonical-name',
                                   'study-name',
                                   'date',
                                   'time'])

    return df_db





def save_df_to_csv(df_db, work_dir, file_name):
    """
    Save cleanded data to CSV file

    Parameters
    ----------
    df_db : pandas.DataFrame
        DataFrame cleanded and ready for insertion into database.
    work_dir : str
        File path to the CSV data file.
    file_name : str
        Name of the file to save data to (should contain '.csv' at the end).

    Returns
    -------
    None.

    """
    df_db.to_csv(work_dir + file_name)




def main():
    """
    Main funtion / programmet
    """
    work_dir = data_file_dir()
    df = read_raw_data_from_csv(work_dir)
    df = rename_columns(df)
    df_new = split_timestamp(df)
    df_db = clean_data(df_new)
    save_df_to_csv(df_db, work_dir, 'cleansed_elephants.csv')





# Main program
if __name__ == '__main__':
    main()