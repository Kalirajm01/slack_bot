from fastapi import FastAPI, Request
from pydantic import BaseModel
import torch
from transformers import BertTokenizer, BertForSequenceClassification
import uvicorn

app = FastAPI()

model_name = 'facebook/bart-large-mnli'
saved_model_path = '../../trained_model/trained_bert_model.pth'
num_labels = 4
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
# model = BertForSequenceClassification.from_pretrained(model_name)

model = BertForSequenceClassification.from_pretrained(
    model_name, num_labels=num_labels)

# Load the saved state_dict with device mapping
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model.load_state_dict(torch.load(saved_model_path, map_location=device))
model.eval()


class TextRequest(BaseModel):
    text: str


@app.post('/predict')
async def predict(request: TextRequest):
    input_text = request.text
    print("Input TexT")
    print(input_text)
    # Tokenize the input text
    tokenized_input = tokenizer(
        input_text, padding=True, truncation=True, return_tensors="pt").to(device)
    print("Tokenized Input")
    print(tokenized_input)
    # Pass the tokenized input to the model
    with torch.no_grad():
        output = model(**tokenized_input)

    # Retrieve the logits from the model output
    logits = output.logits

    # Convert logits to probabilities using softmax
    probabilities = torch.softmax(logits, dim=1)

    # Get the predicted class index
    predicted_class_index = torch.argmax(probabilities, dim=1).item()
    print(predicted_class_index)
    return {"predicted_class_index": predicted_class_index}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
