import yake
from sentence_transformers import SentenceTransformer, util
import re

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


def extract_key_phrases(samples):
    language = "en"
    max_ngram_size = 3
    deduplication_threshold = 0.9
    numOfKeywords = 20

    custom_kw_extractor = yake.KeywordExtractor(lan=language, n=max_ngram_size, dedupLim=deduplication_threshold, top=numOfKeywords, features=None)
    key_phrases = []
    for sample in samples:
        keywords = custom_kw_extractor.extract_keywords(sample)
        key_phrases.extend([kw[0] for kw in keywords])
    return list(set(key_phrases))

positive_key_phrases = extract_key_phrases(positive_samples)
negative_key_phrases = extract_key_phrases(negative_samples)

print("Positive key phrases:", positive_key_phrases)
print("Negative key phrases:", negative_key_phrases)


def split_document(document):
    return document.split('\n')



def filter_sections(sections, positive_key_phrases, negative_key_phrases):
    filtered_sections = []
    for section in sections:
        if any(phrase in section for phrase in positive_key_phrases) and not any(phrase in section for phrase in negative_key_phrases):
            filtered_sections.append(section)
    return filtered_sections



# Example document
document = documents[0]

# Split the document
sections = split_document(document)

# Filter sections using positive and negative key phrases
filtered_sections = filter_sections(sections, positive_key_phrases, negative_key_phrases)

print("Filtered sections:", filtered_sections)






# Initialize S-BERT model
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# Encode positive samples
positive_embeddings = model.encode(positive_samples)

def is_relevant_context(section, positive_embeddings, model, threshold=0.75):
    section_embedding = model.encode(section)
    similarities = util.pytorch_cos_sim(section_embedding, positive_embeddings)
    return any(similarity > threshold for similarity in similarities[0])

def extract_interest_rate(text):
    pattern = re.compile(r'(\d+(\.\d+)?%)')
    matches = pattern.findall(text)
    return [match[0] for match in matches]

# Check for relevant context and extract interest rates
for section in filtered_sections:
    if is_relevant_context(section, positive_embeddings, model):
        interest_rates = extract_interest_rate(section)
        if interest_rates:
            print("Relevant section:", section)
            print("Extracted interest rates:", interest_rates)





