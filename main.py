import os
import requests
import json
import re
from io import BytesIO
from PIL import Image
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

from dotenv import load_dotenv

load_dotenv()

PUBLIC_KEY = os.getenv("PUBLIC_KEY")

from smolagents import DuckDuckGoSearchTool, LiteLLMModel, ToolCallingAgent, CodeAgent


query = """
Describe the food in the image and calculate an estimate of the calories and kilojoules in the given image file. Answer in whole numbers only.
--
1. Scan the image for food items and provide a brief description of the food in the image.
2. Estimate the number of calories and kilojoules in the food in the image.
3. If the food is a packaged item, provide the brand and product name.
4. See if you can find the nutritional information for the food item.
5. Give the answer as a json object with the keys 'calories' and 'kilojoules'. For example, if the answer is 100 calories and 418 kilojoules, 
the json object would be: {"description": description, "calories": 100, "kilojoules": 418}.
--
"""

class DummyImage:
    def __init__(self, data: bytes):
        self.data = data

    def save(self, fp, format=None):
        """
        Mimics a save method.
        If fp is a filename (str), write the data to that file.
        Otherwise, assume fp is a file-like object and write the data.
        """
        if isinstance(fp, str):
            with open(fp, "wb") as f:
                f.write(self.data)
        else:
            fp.write(self.data)

def calculate_calorie(img):
    try:
        model = LiteLLMModel(model_id="gpt-4o-mini")
        agent = CodeAgent(
                tools=[DuckDuckGoSearchTool()],
                additional_authorized_imports=["json", "re"],
                model=model,
                add_base_tools=True,
                max_steps=5
            )

        response = agent.run(query, images = [img])
        return response

    except Exception as e:
        print(e)


def send(message, id, token):
    url = f"https://discord.com/api/interactions/{id}/{token}/callback"
    headers = {"Authorization": f"Bot {os.getenv('BOT_TOKEN')}",
               "Content-Type": "application/json"}

    callback_data = {
            "type": 4,
            "headers": headers,
            "data": {
                "content": message
            }
    }

    response = requests.post(url, json=callback_data)

def command_handler(body):
    try:
        command = body['data']['name']
        image_id = body['data']['options'][0]['value']
        image_url = body['data']['resolved']['attachments'][image_id]['url']
        print(image_url)

        if command != 'cals':
            return {
            'statusCode': 400,
            'body': json.dumps('Invalid command')
        }

        send('Calculating...', body['id'], body['token'])

        response = requests.get(image_url)
        img_data = BytesIO(response.content)
        
        img = Image.open(img_data)
        img = img.resize((512, int(512 * img.height / img.width)), Image.Resampling.LANCZOS)
        result = calculate_calorie(img)

        if result is None:
            update('Failed to calculate', body['token'], os.getenv('APP_ID'))
            return {
            'statusCode': 400,
            'body': json.dumps('Failed to calculate')
        }

        json_result = json.dumps(result)
        loaded_result = json.loads(json_result)
        result = f"{loaded_result['description']}\nCalories: {loaded_result['calories']}, Kilojoules: {loaded_result['kilojoules']}"
        print(f"Result: {result}")

        update(result, body['token'], os.getenv('APP_ID'))

        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
    except Exception as e:
        print(e)
        return {
            'statusCode': 400,
            'body': json.dumps(str(e))
        }


def update(message, token, app_id):
    url = f"https://discord.com/api/webhooks/{app_id}/{token}/messages/@original"

    data = {
        "content": message
    }

    response = requests.patch(url, json=data)

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        print(body)
        signature = event['headers']['x-signature-ed25519']
        timestamp = event['headers']['x-signature-timestamp']

        verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))

        message = timestamp + event['body']

        try:
            verify_key.verify(message.encode(), signature=bytes.fromhex(signature))
        except BadSignatureError:
            return {
                'statusCode': 401,
                'body': json.dumps('Unauthorized')
            }

        # handle the interaction
        t = body['type']

        if t == 1:
            return {
            'statusCode': 200,
            'body': json.dumps({"type": 1})
        }
        elif t == 2:
            return command_handler(body)
        else:
            return {
                'statusCode': 400,
                'body': json.dumps('Invalid request type')
            }

    except Exception as e:
        return {
            'statusCode': 400,
            'body': json.dumps(str(e))
        }

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python main.py <image>")
    else:
        
        response = requests.get(sys.argv[1])
        img_data = BytesIO(response.content)
        
        img = Image.open(img_data)

        img = Image.open(img_data)
        img = img.resize((512, int(512 * img.height / img.width)), Image.Resampling.LANCZOS)
        result = calculate_calorie(img)

        print (result)
