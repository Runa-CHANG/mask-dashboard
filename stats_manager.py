# stats_manager.py
from multiprocessing import Manager
import pandas as pd
from datetime import datetime

def get_shared_stats():
    manager = Manager()
    shared_data = {
        'stats': manager.dict({
            'Without_Mask': 0,
            'With_Mask': 0,
            'Incorrectly_Worn_Mask': 0,
            'Partially_Worn_Mask': 0
        }),
        'history': manager.list()
    }
    return shared_data

def add_history_entry(shared_data, label):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    shared_data['history'].append({'timestamp': now, 'label': label})

def get_history_dataframe(shared_data):
    return pd.DataFrame(list(shared_data['history']))
