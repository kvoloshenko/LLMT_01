# In this example, we first initialize a Sentence-BERT model
# and use it to generate embeddings for a list of sentences.
# Then, we normalize the embeddings and add them to a FAISS index.
# After adding the embeddings to the index, we can use it to perform similarity search.
# We encode the query phrase, normalize its embedding and then search the FAISS index
# to find the most similar sentences in the corpus.
# The results are sorted by their similarity to the query.
# Importing necessary libraries
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss


# Initializing a Sentence-BERT model
model = SentenceTransformer('all-MiniLM-L6-v2')

# A list of sentences
sentences = ['This is an example sentence', 'Another sentence', 'Yet another sentence', 'This is yet another example']

# Getting embeddings for the sentences
embeddings = model.encode(sentences)

# Normalizing the vectors (optional but usually improves the results)
embeddings = embeddings / np.linalg.norm(embeddings, axis=1)[:, np.newaxis]

# Constructing a FAISS index
index = faiss.IndexFlatL2(embeddings.shape[1])

# Adding the vectors to the FAISS index
index.add(embeddings)

# Now we can perform similarity search using the index
# For example, let's find the sentences in the corpus that are most similar to "example sentence"
query = "example sentence"
query_embedding = model.encode([query])
query_embedding = query_embedding / np.linalg.norm(query_embedding)

# Searching the index
D, I = index.search(query_embedding, k=2)

# Printing out the most similar sentences to the query
print("Sentences most similar to:", query)
for i in range(I.shape[1]):
    print(sentences[I[0, i]], "with a score of", D[0, i])



