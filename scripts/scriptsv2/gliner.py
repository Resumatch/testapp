from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

class GLiNERModel:
    def __init__(self, model_name="knowledgator/gliner-multitask-large-v0.5"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

    def extract_info(self, prompt, context):
        input_text = f"{prompt} [SEP] {context}"
        inputs = self.tokenizer.encode(input_text, return_tensors="pt")
        outputs = self.model.generate(inputs)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

    def answer_question(self, question, context):
        input_text = f"question: {question} context: {context}"
        inputs = self.tokenizer.encode(input_text, return_tensors="pt")
        outputs = self.model.generate(inputs)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)