'''
This function recieves an API request with user inputted transactions. It then
parses the transaction and returns a JSON object with the reciever, sender,
currency, items, and amount of each transaction
'''

import json
from flask import Flask, request, jsonify
from octoai.text_gen import ChatMessage, ChatCompletionResponseFormat
from octoai.client import OctoAI
from pydantic import BaseModel

#Initialize Flask API
app = Flask(__name__)


def octoai_api(text):
    class Output(BaseModel):
        sender: str
        reciever: str
        amount : float
        items : str
        currency : str

    client = OctoAI(
        api_key="eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjNkMjMzOTQ5In0.eyJzdWIiOiJjYmFjYWVkOC1jMzBiLTQ0NGItODUxMC0yYjZiOWU1NzEwMDQiLCJ0eXBlIjoidXNlckFjY2Vzc1Rva2VuIiwidGVuYW50SWQiOiIyNGY1NDNmYS00OWZiLTQ3NDEtYmEwYi1jNmRlOWU4NWVmOGEiLCJ1c2VySWQiOiIxZDM2NWEwYy1jMWI3LTQ3ZWQtYTk0YS1lZDU1YzY1NmZkYTYiLCJhcHBsaWNhdGlvbklkIjoiYTkyNmZlYmQtMjFlYS00ODdiLTg1ZjUtMzQ5NDA5N2VjODMzIiwicm9sZXMiOlsiRkVUQ0gtUk9MRVMtQlktQVBJIl0sInBlcm1pc3Npb25zIjpbIkZFVENILVBFUk1JU1NJT05TLUJZLUFQSSJdLCJhdWQiOiIzZDIzMzk0OS1hMmZiLTRhYjAtYjdlYy00NmY2MjU1YzUxMGUiLCJpc3MiOiJodHRwczovL2lkZW50aXR5Lm9jdG8uYWkiLCJpYXQiOjE3MTk1OTA5MDh9.VX-4a9SQZpJTLQrY_5nk5sv8hv5pi69TIfw_dh9zdiidrdFMsnybTsHXdc-zShx4auQxzuQnjgUvHKMgBe8cdOIm-HDuG0fduIR0mxStsI-8SVsKbSCkJcgLyhphFg92L8U45XKfBnjyU-Rq87zvBjrk1Hn7Ki-XHOUX5JfJ-8paZk_4orpNO3X8xZfDDeamYZ_6hxJRRoooaJ3ifLxyG4E7Epzww44XydlRKQmWr12ItqmqtUsof0CWVuO8xMQN_tOS5plA08TGsWZ05FMAcsEg11Osa3jJlViPKaPBtK4sQm_Zwnn0s9JJDxkR8AXGom4w4TmzVG4jWxIiozc_gg"
    )
    model_output=client.text_gen.create_chat_completion(
        # and return a JSON which that has key='transactions' 
        # and value is a list of dictionaries of each transaction
        model="meta-llama-3-8b-instruct",
        messages=[
            ChatMessage(
                content="Extract the receiver, sender, currency, amount, and items from the given text for each transaction. If there are N senders in one transaction, make N transactions. Use context clues. Return only in a JSON format with no other content at all.",
                role="system"
            ), # This is the instructions for the model
            ChatMessage(
                content=text,
                role="user"
            ) # This is the user input
        ],
        max_tokens=512,
        presence_penalty=0,
        temperature=0,
        top_p=1,
        response_format=ChatCompletionResponseFormat(
            type="json_object",
            schema=Output.model_json_schema(),
        ),
    )

    # print(model_output.choices[0].message.content)
    return model_output.choices[0].message.content


@app.route('/analyze_text', methods=['POST'])
def analyze_text():
    data = request.get_json()
    if 'text' not in data:
        return jsonify({"error": "No text provided"}), 400
    

    result={"transactions": []}
    text = data['text']

    result["transactions"]= json.loads(octoai_api(text))


    #TODO: have to rethink this with flask sessions later
    for transaction in result["transactions"]:
        if transaction["receiver"].lower() in ['i','my','me','you']:
            transaction["amount"] *= -1
    # print(result)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)