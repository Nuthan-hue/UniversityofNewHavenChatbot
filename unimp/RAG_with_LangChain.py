from langchain.chains import RetrievalQA
from langchain import OpenAI

# Load the FAISS vector store
vector_store = FAISS.load_local("faiss_university_index", embedding=embedding_model)

# Initialize the GPT-3.5 model
llm = OpenAI(model_name="gpt-3.5-turbo", openai_api_key="your-openai-api-key")

# Create the retriever
retriever = vector_store.as_retriever(search_kwargs={"k": 3})

# Build the Retrieval-Augmented Generation (RAG) chain
qa_chain = RetrievalQA(llm=llm, retriever=retriever)

# Example Query
query = "What is the application deadline for Fall 2024?"
response = qa_chain.run(query)

print(f"Chatbot Response: {response}")
