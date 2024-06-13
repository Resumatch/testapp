from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# Initialize the model
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

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
sample_embeddings = model.encode(sample_paragraphs, convert_to_tensor=True)
section_embeddings = model.encode(document_sections, convert_to_tensor=True)

# Convert embeddings to numpy arrays
sample_embeddings_np = sample_embeddings.cpu().detach().numpy()
section_embeddings_np = section_embeddings.cpu().detach().numpy()

# Initialize FAISS index
dimension = sample_embeddings_np.shape[1]  # Dimension of embeddings
index = faiss.IndexFlatL2(dimension)

# Add document section embeddings to the index
index.add(section_embeddings_np)

# Search for similar contexts
k = 5  # Number of nearest neighbors to retrieve
for i, sample_embedding in enumerate(sample_embeddings_np):
    D, I = index.search(np.array([sample_embedding]), k)
    print(f"Sample Paragraph {i+1}:")
    print(sample_paragraphs[i])
    print("Most similar sections:")
    for idx in I[0]:
        print(document_sections[idx])
    print("\n")