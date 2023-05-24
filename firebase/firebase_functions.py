import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Use a service account.
#combis-jobs-etl specific service account key. 
# Generated from firebase console > settings > users and permissions > service accounts

def get_db():
  cred = credentials.Certificate('firebase/service-account-key.json')

  # Check if the app is already initialized
  if not firebase_admin._apps:
      app = firebase_admin.initialize_app(cred)
  else:
      app = firebase_admin.get_app()

  return firestore.client()

def write_to_db(data):
  db = get_db()
  for entry in data:
    doc_ref = db.collection('translated_jobs').document(entry['id'])
    doc_ref.set(entry)
