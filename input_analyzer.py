import spacy
from flask import Flask, request, jsonify

#Initialze the NLP model + language
nlp = spacy.load('en_core_web_sm')

#Initialize Flask API
app = Flask(__name__)


def parse_transaction(text):
    # return a dictionary
    doc = nlp(text)
    transaction = {"Description":""}

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
            # print()
            # for child in token.subtree:

            #     print(child.text,end=' ')
            #     print(child.dep_,child.pos_)

            # print()
            # print()
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
    
    for transaction in text.split('\n'):
        print(transaction)
        result["transactions"].append(parse_transaction(transaction))
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)