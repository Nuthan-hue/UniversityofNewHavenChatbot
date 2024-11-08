import json
import openai
import faiss
import numpy as np

# Initialize OpenAI API Key
openai.api_key = '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'

# Load document data from JSON file
with open("documents.json", "r") as f:
    documents = json.load(f)

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

embeddings = np.array(embeddings).astype("float32")

dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)

metadata_dict = {i: metadata[i] for i in range(len(metadata))}

def search_faiss_index(query, index, k=2):
    query_embedding = np.array(generate_embedding(query)).reshape(1, -1).astype("float32")
    distances, indices = index.search(query_embedding, k)
    return indices[0]

def generate_answer_with_context(retrieved_docs, user_question):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_question},
            {"role": "assistant", "content": f"Here is some context: {retrieved_docs}"}
        ]
    )
    return response.choices[0].message['content']

def retrieve_and_generate_answer(user_question, index):
    top_k_indices = search_faiss_index(user_question, index, k=2)
    retrieved_docs = [{"text": documents[i]['text'], "metadata": metadata_dict[i]} for i in top_k_indices]
    return generate_answer_with_context(retrieved_docs, user_question)

# Continuous input loop
with open("queries.txt", "a") as file:
    try:
        while True:
            print("Waiting for your input...")
            user_query = input("Enter your query: ")
            final_answer = retrieve_and_generate_answer(user_query, index)
            print("Generated Answer:", final_answer)
            # Write the query and answer to file
            file.write(f"Query: {user_query}\nAnswer: {final_answer}\n\n")
            file.flush()  # Ensure data is immediately written to file
    except KeyboardInterrupt:
        print("\nExiting program.")
