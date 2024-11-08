import openai
import faiss
import numpy as np

# Step 1: Initialize OpenAI API Key
openai.api_key = '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'

# Step 2: Define Data and Generate Embeddings
# Your data
documents = [
    {"text": "Undergraduate: You have a high school diploma and want to increase your job opportunities and income. You’re a working adult seeking a bachelor’s degree. You’re a transfer student with a two-year degree looking to earn a four-year degree.  You want to boost your knowledge, skills, and confidence.", "metadata": {"heading": "Undergraduate"}},
    {"text": "Graduate: You want to continue your studies in your field of interest.  You’re a working adult looking to advance more rapidly in your career and increase your income.  You have specialized research interests or career goals.  You want to become a skilled professional in your field.", "metadata": {"heading": "Graduate"}},
    {"text": "Online Programs: With your busy life, you can’t physically be on campus, but you still want a college education.  You want online courses and programs that achieve the same educational objectives, are based on the same quality standards, and carry the same academic credit as their on-campus counterparts.", "metadata": {"heading": "Online Programs"}}
]

# Function to generate embedding for a given text
def generate_embedding(text):
    response = openai.Embedding.create(
        model="text-embedding-ada-002",
        input=text
    )
    return response['data'][0]['embedding']

# Generate embeddings and store metadata
embeddings = []
metadata = []

for doc in documents:
    embedding = generate_embedding(doc['text'])
    embeddings.append(embedding)
    metadata.append(doc['metadata'])

# Convert embeddings to a numpy array for FAISS
embeddings = np.array(embeddings).astype("float32")

# Step 3: Index Embeddings with FAISS
# Initialize FAISS index
dimension = embeddings.shape[1]  # This should match the embedding vector size
index = faiss.IndexFlatL2(dimension)  # L2 similarity

# Add embeddings to the index
index.add(embeddings)

# Store metadata in a dictionary for retrieval
metadata_dict = {i: metadata[i] for i in range(len(metadata))}

# Step 4: Define a Function to Retrieve Documents Based on Query
def search_faiss_index(query, index, k=2):
    # Generate embedding for the query
    query_embedding = np.array(generate_embedding(query)).reshape(1, -1).astype("float32")
    # Search the FAISS index for top-k similar embeddings
    distances, indices = index.search(query_embedding, k)
    return indices[0]  # Return the document IDs of the top matches

# Step 5: Define the RAG Function to Combine Retrieved Documents and Generate Answer
def generate_answer_with_context(retrieved_docs, user_question):
    # Combine the retrieved documents into a single context string
    retrieved_context = "\n".join([doc['text'] for doc in retrieved_docs])
    
    # Generate a response with OpenAI's GPT model
def generate_answer_with_context(retrieved_docs, user_question):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # or "gpt-4" if using GPT-4
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_question},
            #{"role": "assistant", "content": retrieved_docs}  # Context from retrieved documents
            {"role": "assistant", "content": f"Here is some context: {retrieved_docs}"}
        ]
    )
    return response.choices[0].message['content']

# Step 6: Define the Main RAG Function
def retrieve_and_generate_answer(user_question, index):
    # Step 6.1: Retrieve relevant documents
    top_k_indices = search_faiss_index(user_question, index, k=2)
    # Step 6.2: Gather the retrieved documents
    retrieved_docs = [{"text": documents[i]['text'], "metadata": metadata_dict[i]} for i in top_k_indices]
    # Step 6.3: Generate the final answer with context
    return generate_answer_with_context(retrieved_docs, user_question)

# Example Usage
user_query = " What is the data I gave to you"
final_answer = retrieve_and_generate_answer(user_query, index)
print("Generated Answer:", final_answer)
