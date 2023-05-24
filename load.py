from firebase.firebase_functions import write_to_db
from functions import load_timestamp

import json

with open('active_ads_w_summaries_and_translations.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

#writes data to firestore
write_to_db(data)

#logs timestamp of run
load_timestamp()