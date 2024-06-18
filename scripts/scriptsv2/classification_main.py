from transformers import BertTokenizer, BertForSequenceClassification, Trainer, TrainingArguments
from sklearn.model_selection import train_test_split
import torch
from transformers import pipeline


# Positive and negative samples
positive_samples = [
    "The interest rate paid on death of the insured is X% on the lump sum amount.",
    "In the event of the policyholder's death, an interest rate of Y% will be applied to the lump sum payment.",
    # ... additional positive samples
]

negative_samples = [
    "The interest rate for the savings account is Z%.",
    "Interest rates for loans vary depending on the type of loan.",
    # ... additional negative samples
]

# Combine samples and create labels
texts = positive_samples + negative_samples
labels = [1] * len(positive_samples) + [0] * len(negative_samples)

# Split data into training and testing sets
train_texts, test_texts, train_labels, test_labels = train_test_split(texts, labels, test_size=0.2, random_state=42)

# Tokenizer and model initialization
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=2)

# Tokenize the texts
train_encodings = tokenizer(train_texts, truncation=True, padding=True, max_length=512)
test_encodings = tokenizer(test_texts, truncation=True, padding=True, max_length=512)

# Create a PyTorch dataset
class QADataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)

train_dataset = QADataset(train_encodings, train_labels)
test_dataset = QADataset(test_encodings, test_labels)



training_args = TrainingArguments(
    output_dir='./results',
    num_train_epochs=3,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    warmup_steps=500,
    weight_decay=0.01,
    logging_dir='./logs',
    logging_steps=10,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset,
)

trainer.train()



def split_document(document):
    return document.split('\n')  


def classify_sections(sections, tokenizer, model):
    relevant_sections = []
    for section in sections:
        inputs = tokenizer(section, return_tensors='pt', truncation=True, padding=True, max_length=512)
        outputs = model(**inputs)
        logits = outputs.logits
        prediction = torch.argmax(logits, dim=1).item()
        if prediction == 1:
            relevant_sections.append(section)
    return relevant_sections

# Example document
document = documents[0]
# Split the document
sections = split_document(document)

# Classify sections
relevant_sections = classify_sections(sections, tokenizer, model)

print("Relevant sections:", relevant_sections)



# Initialize the QnA pipeline using the GliNER model
qna_pipeline = pipeline('question-answering', model='knowledgator/gliner-multitask-large-v0.5')

def answer_questions(section, questions):
    answers = []
    for question in questions:
        result = qna_pipeline(question=question, context=section)
        answers.append(result['answer'])
    return answers

# Example questions
questions = [
    "What is the interest rate paid on the lump sum amount after death?",
]

# Answer questions using the GliNER model
for section in relevant_sections:
    answers = answer_questions(section, questions)
    print("Relevant section:", section)
    print("Answers:", answers)