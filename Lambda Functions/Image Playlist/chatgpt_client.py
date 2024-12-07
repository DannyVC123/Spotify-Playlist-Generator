import json

from web_service import WebService

class ChatGPTClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.model = 'gpt-4o-mini'

        self.base_url = 'https://api.openai.com/v1/chat/completions'
    
    def get_recommendations_json(self, user_prompt, limit=10):
        base_prompt = '''You are an assistant that only responds in JSON. Create a list of {limit} unique songs based off the following statement: "{user_prompt}". Include "title", "artist", "album". An example response is:"
[
    {{
        "title": "Hey Jude",
        "artist": "The Beatles",
        "album": "The Beatles (White Album)"
    }}
]"'''
        full_prompt = base_prompt.format(limit=limit + 5, user_prompt=user_prompt)

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": full_prompt
                }
            ],
            "temperature": 0.1,
            "max_tokens": 3000
        }

        status_codes = [429, 500, 503]
        response = WebService.call(self.base_url, 'post', status_codes, good_codes=False, headers=headers, data=json.dumps(payload))
        response_body = response.json()

        if response.status_code in [401, 403, 429, 500, 503]:
            print(response.status_code)
            print(response_body)
            return None

        content = response_body['choices'][0]['message']['content']
        tracks_json = json.loads(content[content.find("[") : content.rfind("]") + 1])
        print(tracks_json)
        return tracks_json

