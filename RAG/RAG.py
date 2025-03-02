import json
import openai
import faiss
import numpy as np
import os

# Initialize OpenAI API Key
openai.api_key = 'Open-Ai-Key'

# Load document data from JSON file
def load_documents(file_path):
    """Load documents from a JSON file."""
    with open(file_path, "r") as f:
        return json.load(f)

def generate_embedding(text):
    """Generate text embedding using OpenAI's embedding model."""
    response = openai.Embedding.create(
        model="text-embedding-ada-002",
        input=text
    )
    return response['data'][0]['embedding']

def create_faiss_index(embeddings):
    """
    Create and populate a FAISS index with the provided embeddings.
    """
    embeddings = np.array(embeddings).astype("float32")
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    print("Number of vectors before adding to the index:", index.ntotal)
    index.add(embeddings)
    print("Number of vectors after adding to the index:", index.ntotal)
    return index

def search_faiss_index(query, index, k=2):
    """
    Search the FAISS index for the top-k nearest neighbors to the query.
    """
    query_embedding = np.array(generate_embedding(query)).reshape(1, -1).astype("float32")
    distances, indices = index.search(query_embedding, k)
    print("Distances:", distances)
    print("Indices:", indices[0])
    return indices[0]

def generate_answer_with_context(retrieved_docs, user_question):
    """
    Generate a response using OpenAI GPT-3.5 Turbo, given retrieved documents and the user question.
    """
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_question},
            {"role": "assistant", "content": f"Here is some context: {retrieved_docs}"}
        ]
    )
    return response.choices[0].message['content']

def retrieve_and_generate_answer(user_question, index, documents, metadata_dict):
    """
    Retrieve relevant documents based on the query and generate an answer using GPT.
    """
    print("\n--- Retrieving and Generating Answer ---")
    top_k_indices = search_faiss_index(user_question, index, k=2)
    retrieved_docs = [
        {"text": documents[i]['text'], "metadata": metadata_dict[i]} for i in top_k_indices
    ]
    print(f"Retrieved Documents: {retrieved_docs}")
    return generate_answer_with_context(retrieved_docs, user_question)

def save_embeddings(file_path, embeddings, metadata):
    """Save embeddings and metadata to a file."""
    with open(file_path, "w") as f:
        json.dump({"embeddings": embeddings, "metadata": metadata}, f)

def load_embeddings(file_path):
    """Load embeddings and metadata from a file."""
    with open(file_path, "r") as f:
        data = json.load(f)
    return data["embeddings"], data["metadata"]

def main():
    # File paths
    document_file = "/Users/nuthankishoremaddineni/Desktop/UNHChatbot/web_scraping/myfirst/myfirst/spiders/rag_data.json"
    embeddings_file = "embeddings.json"
    
    # Load documents
    documents = load_documents(document_file)
    
    # Check if embeddings file exists
    embeddings = []
    metadata = []
    if os.path.exists(embeddings_file):
        regenerate = input("Embeddings file exists. Do you want to regenerate embeddings? (yes/no): ").strip().lower()
        if regenerate == "no":
            embeddings, metadata = load_embeddings(embeddings_file)
        else:
            print("\n--- Generating Embeddings ---")
            for doc in (documents):
                embedding = generate_embedding(doc['text'])
                embeddings.append(embedding)
                metadata.append(doc['metadata'])
                #if i == 5:  # Limit for testing
                #    break
            save_embeddings(embeddings_file, embeddings, metadata)
    else:
        print("\n--- Generating Embeddings ---")
        for doc in (documents):
            embedding = generate_embedding(doc['text'])
            embeddings.append(embedding)
            metadata.append(doc['metadata'])
        save_embeddings(embeddings_file, embeddings, metadata)

    # Create FAISS index
    print("\n--- Creating FAISS Index ---")
    index = create_faiss_index(np.array(embeddings).astype("float32"))
    metadata_dict = {i: metadata[i] for i in range(len(metadata))}

    # Continuous Query Input Loop
    with open("queries.txt", "a") as file:
        try:
            while True:
                user_query = input("Enter your query: ")
                final_answer = retrieve_and_generate_answer(user_query, index, documents, metadata_dict)
                print("\nGenerated Answer:", final_answer)
                
                # Log query and answer
                file.write(f"Query: {user_query}\nAnswer: {final_answer}\n\n")
                file.flush()
        except KeyboardInterrupt:
            print("\nExiting program.")

if __name__ == "__main__":
    main()
