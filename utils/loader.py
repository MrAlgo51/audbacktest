import pandas as pd

def load_price_data(path):
    df = pd.read_csv(path)
    
    # Make sure timestamp is datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Sort by timestamp just in case
    df = df.sort_values('timestamp').reset_index(drop=True)
    
    return df
