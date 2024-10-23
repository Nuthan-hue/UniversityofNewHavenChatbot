import openai

# Set the API key (securely)
openai.api_key = "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"

user_question = input("Enter your question: ")

# Corrected API call to use the fine-tuned model
response = openai.ChatCompletion.create(
    model="ft:gpt-3.5-turbo-0125:personal::ALEChPAI",  # Use the fine-tuned model ID
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": user_question}
    ],
    max_tokens=100
)

# Accessing the content of the response
print(response['choices'][0]['message']['content'].strip())