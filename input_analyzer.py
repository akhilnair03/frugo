import spacy
import json
from spacy.language import Language
from spacy.tokens import Doc
from flask import Flask, request, jsonify
from octoai.text_gen import ChatMessage, ChatCompletionResponseFormat
from octoai.client import OctoAI
from pydantic import BaseModel

#Initialze the NLP model + language
nlp = spacy.load('en_core_web_sm')

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
    x=client.text_gen.create_chat_completion(
        #  and return a JSON which that has key='transactions' and value is a list of dictionaries of each transaction
        model="meta-llama-3-8b-instruct",
        messages=[
            ChatMessage(
                content="Extract the receiver, sender, currency, amount, and items from the given text for each transaction. If there are N senders in one transaction, make N transactions. Use context clues. Return only in a JSON format with no other content at all",
                role="system"
            ), #This is the instructions for the model
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

    # print(x.choices[0].message.content)
    return x.choices[0].message.content

# def test(text):
    doc = nlp(text)
    transactions=[]
    # for sent in doc.sents:
    #     print(sent.text)
    #     print('****')


    '''
    Logic: Just keep reading through and building a transaction. Once a full
    transaction is found then understand the transaction over and move onto the next 
    '''
    for token in doc:
        print(f"Token: {token.text}, is_sent_start: {token.is_sent_start}")
        transaction = {
            "sender": None,
            "amount": None,
            "currency": None,
            "description": ""
        }
        
        # # Flags to identify if we have seen certain key elements
        seen_currency,seen_amount,seen_sender,seen_reciever = False,False,False,False
        # if token.dep_ == "nsubj" # 
        
        # # Identify named entities for amounts and currencies
        # for ent in sent.ents:
        #     if ent.label_ == "MONEY":
        #         transaction["amount"] = ent.text
        #         seen_amount = True

        # # Use dependency parsing and pattern matching for more general extraction
        # for token in sent:
        #     if token.dep_ in ("nsubj", "nsubjpass"):
        #         if token.text.lower() == 'i':
        #             transaction["sender"] = "user"
        #         else:
        #             transaction["sender"] = token.text
        #     if token.text in ["$", "€", "¥", "£", "₹"]:
        #         transaction["currency"] = token.text
        #         seen_currency = True

        #     # Capture descriptions based on noun phrases and prepositional objects
        #     if token.dep_ in ("dobj", "pobj", "attr") and token.pos_ == "NOUN":
        #         # If we see a conjunction, capture the whole phrase
        #         if token.head.dep_ in ("prep", "dative", "pobj") or token.dep_ == "conj":
        #             noun_phrase = " ".join([child.text for child in token.subtree])
        #             transaction["description"] += " " + noun_phrase
        #         elif token.dep_ == "pobj":
        #             transaction["description"] += " " + token.text
        
        # # Post-process to clean up the transaction dictionary
        # if transaction["amount"] and seen_currency and seen_amount:
        #     transactions.append(transaction)

    return transactions

def parse_transaction(text):
    # return a dictionary
    doc = nlp(text)
    transaction = {
        "Description":"",
        "sender":None,
        "amount":None,
        "reciever":None,
        "currency":None
    }

    currencies = {
        "$": "US dollar",
        "€": "Euro",
        "¥": "Yen"
    }   

    for token in doc:
        print(token.text,token.dep_,token.pos_,token.ent_type_)
        if token.dep_== "nsubj": # this means this token DOES the verb
            if token.text.lower() in ['i','my']:
                transaction["sender"] = "user"
            else:
                transaction["sender"] = token.text
        elif token.dep_ == "poss": #indirect object
            if token.text.lower() in ['i','my']:
                transaction["reciever"] = "user"
            else:
                transaction["reciever"] = token.text
        elif token.text in currencies: #Check for currency type
            transaction["currency"] = currencies[token.text]
        elif token.pos_ == "NUM":
            transaction["amount"] = float(token.text)
        elif token.dep_ == "pobj":
            # noun_phrase=""
            # for child in token.subtree:
            #     if child.dep_ != "poss":
            #         noun_phrase+=' '+child.text

            noun_phrase = " ".join([child.text for child in token.subtree])
            transaction["Description"] += noun_phrase

    if transaction["sender"] != "user":
        transaction["amount"] *= -1

    return transaction


@app.route('/analyze_text', methods=['POST'])
def analyze_text():
    data = request.get_json()
    if 'text' not in data:
        return jsonify({"error": "No text provided"}), 400
    

    result={"transactions": []}
    text = data['text']

    result["transactions"]= json.loads(octoai_api(text))
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)