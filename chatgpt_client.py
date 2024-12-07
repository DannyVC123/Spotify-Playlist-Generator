import json

import openai

class ChatGPTClient:
    def __init__(self, api_key):
        openai.api_key = api_key
        self.model = 'gpt-4o-mini'
    
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
        messages = [
            {
                'role': 'user',
                'content': full_prompt
            }
        ]

        response = openai.chat.completions.create(model=self.model, temperature=0.1, max_tokens=3000, messages=messages)
        content = response.choices[0].message.content

        tracks_json = json.loads(content[content.find("[") : content.rfind("]") + 1])
        return tracks_json

