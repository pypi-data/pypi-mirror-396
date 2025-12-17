from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import importlib.resources as pkg_resources

MODEL_DIR = pkg_resources.files("nl2cmd") / ".." / ".." / "model"

tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_DIR)

def ml_translate(text):
    prompt = "Translate English to canonical command: " + text
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(**inputs, max_length=64)
    result = tokenizer.decode(outputs[0], skip_special_tokens=True)

    if not result.isupper():
        return None
    return result
