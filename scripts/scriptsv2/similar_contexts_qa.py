from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from transformers import pipeline

# Initialize the models
embedding_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
qa_model = pipeline("question-answering", model="distilbert-base-uncased-distilled-squad")

# Sample paragraphs and document sections
sample_paragraphs = [
    "sample paragraph1 ",
    "sample paragraph1",
    # Add all 30 sample paragraphs
]

#Siddhant - create this one from 'clues'
document_sections = [
    "target candidate contexts1",
    "target candidate contexts2",
    # Add all document sections from your lengthy documents
]


# Generate embeddings
sample_embeddings = embedding_model.encode(sample_paragraphs, convert_to_tensor=True)
section_embeddings = embedding_model.encode(document_sections, convert_to_tensor=True)

# Convert embeddings to numpy arrays
sample_embeddings_np = sample_embeddings.cpu().detach().numpy()
section_embeddings_np = section_embeddings.cpu().detach().numpy()

# Initialize FAISS index
dimension = sample_embeddings_np.shape[1]  # Dimension of embeddings
index = faiss.IndexFlatL2(dimension)

# Add document section embeddings to the index
index.add(section_embeddings_np)

# Define a function for QA with similarity search
def get_answer(question, sample_embedding, k=5, threshold=0.3):
    # Search for similar contexts
    D, I = index.search(np.array([sample_embedding]), k)
    
    # Check if the top result is below the threshold
    if D[0][0] > threshold:
        return "none"
    
    # Prepare context
    context = " ".join([document_sections[idx] for idx in I[0]])
    
    # Get the answer using the QA model
    answer = qa_model(question=question, context=context)
    
    # Check the confidence score
    if answer['score'] < 0.1:
        return "none"
    
    return answer['answer']

# Example usage
question = "What is the capital of France?"
for i, sample_paragraph in enumerate(sample_paragraphs):
    sample_embedding = sample_embeddings_np[i]
    answer = get_answer(question, sample_embedding)
    print(f"Sample Paragraph {i+1}:")
    print(sample_paragraph)
    print("Answer:", answer)
    print("\n")