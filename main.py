#fetching funtionality
from functions import get_last_timestamp, get_active_ads, summarize_ads, translate_summaries
import json

#get timestamp of last run from database
last_timestamp = get_last_timestamp()

#fetches active ads from jobstream api
active_ads = get_active_ads(last_timestamp=last_timestamp,occupations=['Z6TY_xDf_Yup','4zLr_jP5_peZ'], search_places=['AvNB_uwa_6n6'])

#here we should check if these adds are already in our data
#and if not, add them to our data

#summarizes the ads using open ai
active_ads_w_summaries = summarize_ads(active_ads)

#translates the summaries using google translate
active_ads_w_summaries_and_translations = translate_summaries(active_ads_w_summaries)

#store the ads in temporary json

with open('active_ads_w_summaries_and_translations.json', 'w', encoding='utf-8') as f:
    json.dump(active_ads_w_summaries_and_translations, f, ensure_ascii=False)

