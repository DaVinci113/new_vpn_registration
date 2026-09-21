import os
from calendar import month

from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("HIDDIFY_API_KEY")

headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Hiddify-API-Key": api_key
}

plan = {"plan": {"volume": 500,
         "duration": "month",
                 "devices": 4},
        "trial": {"volume": 50,
             "duration": "month",
                  "devices": 1},
        }
