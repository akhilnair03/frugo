import spacy

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")

# Sample text
text = "I paid for my quesadilla"

# Process the text
doc = nlp(text)

# Iterate over tokens
for token in doc:
    print(f"Text: {token.text}")
    print(f"Lemma: {token.lemma_}")
    print(f"POS: {token.pos_}")
    print(f"Tag: {token.tag_}")
    print(f"Dependency: {token.dep_}")
    print(f"Shape: {token.shape_}")
    print(f"Is Alpha: {token.is_alpha}")
    print(f"Is Stop: {token.is_stop}")
    print(f"Head: {token.head.text}")
    print(f"Entity Type: {token.ent_type_}")
    print(f"Entity IOB: {token.ent_iob_}")
    print(f"Character Offset: {token.idx}")
    print("-" * 20)