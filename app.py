from flask import Flask, request, abort
import requests
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent'
api_key = 'AIzaSyCy4iniVHcpVDHmd1J5_3ZkpmROEOm9-uo'

headers = {
    'Content-Type': 'application/json',
}

def getPrompt(concentration, metalName, waterSource):
    prompt = '''I found {concentration} ppm of {metalName} heavy metal in my water that I got from {waterSource}. What can I do to purify it? Return your answer in the JSON format specified below.
    {
    "label": "safe" | "not safe",
    "drinkability_score": 0-100,
    "ways_to_fix_source": [
        {
        "title": "string",
        "description": ["string", ...]
        },
        ...
    ],
    "purification_steps_for_houses": [
        {
        "title": "string",
        "description": ["string", ...]
        },
        ...
    ],
    "purification_steps_for_factories": [
        {
        "title": "string",
        "description": ["string", ...]
        },
        ...
    ]
    }
    - Don't include tildas, or new line characters in your answer. The answer should be a single line JSON object.
    - the label must be a String. either 'safe' or 'not safe'
    - drinkability_score: Number. a score from 0 to 100 of how safe it is to drink. Don't return fractions or text
    - ways_to_fix_source: this will be a list of purification steps for the water source. max 3 major ways. these steps must be related to the water source. example: "if water source is a well and we detect copper, what can we do to purify the entire well?"
    - purification_steps_for_houses: this will be a list of purification steps suitable for factories/industries. 3 major ways to purify water from the mentioned heavy metal.
    - purification_steps_for_factories: this will be a list of purification steps suitable for factories/industries. 3 major ways to purify water from the mentioned heavy metal.


    Don't include additional information in your answer apart from what this prompt specifies. don't add any extra notes, descriptions, before and after the JSON. Return only the JSON strictly.
    '''
    return prompt.replace("{concentration}", concentration).replace("{metalName}", metalName).replace("{waterSource}", waterSource)

def getAnswer(prompt):
    return {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }


@app.route('/')
def home():
    concentration = request.args.get('concentration')
    metal = request.args.get('metal')
    source = request.args.get('source')
    
    isRequestValid = True
    notMentionedItems = []

    if not concentration:
        isRequestValid = False
        notMentionedItems.append('Concentration')
    if not metal:
        isRequestValid = False
        notMentionedItems.append('Heavy Metal Name')
    if not source:
        isRequestValid = False
        notMentionedItems.append('Water source')
    
    tempString = ''
    for i in range(len(notMentionedItems)):
        if (i == 0):
            tempString = tempString + notMentionedItems[i]
        else:
            tempString = tempString + ', ' + notMentionedItems[i]
    

    if (isRequestValid == False):
        abort(400, description=f"Not Mentioned Items: {tempString} ")

    
    prompt = getPrompt(concentration, metal, source)
    response = requests.post(f'{url}?key={api_key}', headers=headers, json=getAnswer(prompt))

    if response.status_code != 200:
        abort(response.status_code, description=f"Error from API: {response.text}")

    print(response.json())
    json_res = json.loads(response.json()['candidates'][0]['content']['parts'][0]['text'])

    return json_res


@app.route('/about')
def about():
    name = request.args.get('name', 'stranger')  # Default to 'stranger' if no name is provided
    return f"Hi, {name}, this is the about page."


@app.route('/forbidden')
def forbidden():
    name = request.args.get('name')
    roll = request.args.get('roll')
    # If 'name' is not provided, return 400 Bad Request
    if not name:
        abort(400, description="Name parameter is required.")
    if not roll:
        abort(400, description="Roll number parameter is required.")
    
    return f"Hi, {name}, this is the about page. Your roll number is {roll}."


@app.route('/post-example', methods=['POST'])
def post_example():
    if request.is_json:
        data = request.get_json()
        name = data.get('name')
        
        if not name:
            abort(400, description="Name field is required in JSON payload.")
        
        return {"message": f"Hi, {name}, you've sent a POST request!"}
    else:
        abort(400, description="Request must be in JSON format.")



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)