from firebase_admin import firestore
from firebase.firebase_functions import get_db
from datetime import datetime
import time
import requests
import json
import openai
from googleapiclient.discovery import build

from config import OPENAI_API_KEY,translate_api

collection_name = "runlog"

db = get_db()

def load_timestamp():
  timestamp = datetime.now()
  formatted_time = timestamp.strftime("%Y-%m-%d %H:%M:%S")

  data = {'last_run_timestamp': formatted_time}
  #if ever needed manual timestamp for e.g. testing
  #data = {'last_run_timestamp': "2023-05-23 13:22:39"}


  doc_ref = db.collection(collection_name).document() # auto-generate id
  doc_ref.set(data) #pushes current timestamp in to collection of run timestamps

def get_last_timestamp():
    doc_ref = db.collection(collection_name).order_by('last_run_timestamp', direction=firestore.Query.DESCENDING).limit(1)
    docs = doc_ref.get()
    for doc in docs:
        return doc.to_dict()['last_run_timestamp']
    return None

def get_jobs_since_timestamp(timestamp):
    doc_ref = db.collection(collection_name).where('last_run_timestamp', '>', timestamp)
    docs = doc_ref.get()
    return docs

#gets active ads from jobstream api
def get_active_ads(last_timestamp,occupations,search_places):
    api_url = 'https://jobstream.api.jobtechdev.se/stream'
    search_places = ['AvNB_uwa_6n6'] #stockholm

    last_timestamp = datetime.fromisoformat(last_timestamp).strftime("%Y-%m-%dT%H:%M:%S")

    params = {'date': last_timestamp, 'location-concept-id': search_places, 'occupation-concept-id': occupations}
    headers = {'Accept': 'application/json'}

    response = requests.get(api_url, headers=headers, params=params)
    response.raise_for_status()
    list_of_ads = json.loads(response.content.decode('utf8'))

    # iterate through each ad in the original list
    active_ads = [{
        "id": ad['id'],
        "af_url": ad['webpage_url'],
        "title": ad['headline'],
        "application_deadline": ad['application_deadline'],
        "employment_type": ad['employment_type']['label'],
        "description": ad['description']['text'],
        "salary_description": ad['salary_description'],
        "application_mail": ad['application_details']['email'],
        "application_url": ad['application_details']['url'],
        "occupation_label": ad['occupation']['label'],
        "workplace_region": ad['workplace_address']['region'],
        "workplace_coordinates": ad['workplace_address']['coordinates'],
        "publication_date": ad['publication_date'],
        "last_publication_date": ad['publication_date'],
        "timestamp": ad['timestamp']
    } for ad in list_of_ads if not ad.get('removed')]

    return active_ads

def summarize_ads(active_ads):
    openai.api_key = OPENAI_API_KEY

    for ad in active_ads:
        MODEL = "gpt-3.5-turbo"
        description = ad['description']

        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            try:
                response = openai.ChatCompletion.create(
                    model=MODEL,
                    messages=[
                        {"role": "system", "content": "Please summarize the following job description in English and limit the summary to 200 words:"},
                        {"role": "user", "content": "Description: " + description},
                    ],
                    max_tokens=220,
                )
                summary = response["choices"][0]["message"]["content"].strip()
                ad['summary_en'] = summary
                break  # Break out of the retry loop if successful
            except Exception as e:
                print(f"Attempt {attempt} failed. Retrying...")
                time.sleep(1)  # Wait for 1 second before retrying

        else:
            # Reached maximum attempts without success
            ad['summary_en'] = "Could not get response"

    return active_ads


def translate_summaries(active_ads):
    translate_client = build("translate", "v2", developerKey=translate_api)
    for ad in active_ads:
        summary = ad['summary_en']
        translation = translate_client.translations().list(q=summary, target='ar').execute()
        summary_ar = translation['translations'][0]['translatedText']
        ad['summary_ar'] = summary_ar
    return active_ads

