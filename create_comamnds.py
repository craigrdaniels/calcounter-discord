import os

import requests
from dotenv import load_dotenv

load_dotenv()

APP_ID = os.getenv("APP_ID")
BOT_TOKEN = os.getenv("BOT_TOKEN")


url = f"https://discord.com/api/v10/applications/{APP_ID}/commands"


json = [
    {
        "name": "cals",
        "description": "Calculate an estimate of the calories and kilojoules in this image",
        "options": [
            {
                "name": "image",
                "description": "Provide the image to calculate the calories and kilojoules",
                "type": 11,
                "required": True
            }
        ]
    },
    {
        "name": "log",
        "description": "Log an estimate of the calories and kilojoules in this image",
        "options": [
            {
                "name": "image",
                "description": "Provide the image to calculate the calories and kilojoules",
                "type": 11,
                "required": True
            }
        ]
    },
]

response = requests.put(url, headers={
    'Authorization': f'Bot {BOT_TOKEN}'
    }, json=json)


print(response.json())
