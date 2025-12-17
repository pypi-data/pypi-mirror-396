from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

MODEL_ID = "nagashreens05/nl2cmd-flan-t5"

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_ID)

def ml_translate(text):
    prompt = "Translate English to canonical command: " + text
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(**inputs, max_length=64)
    result = tokenizer.decode(outputs[0], skip_special_tokens=True)

    if not result.isupper():
        return None
    return result
