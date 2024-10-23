'''import openai

# Set the API key (You might want to load this securely instead of hardcoding)
openai.api_key = "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"

# Corrected API call
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, how can I use OpenAI?"}
    ]
)

# Accessing the content of the response
print(response['choices'][0]['message']['content'].strip())'''




'''import openai

# Set up your OpenAI API key
openai.api_key = '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'

response = openai.ChatCompletion.create(
  model="gpt-3.5-turbo-1106",  # Use "gpt-4" or "gpt-3.5-turbo" for chat models
  messages=[
    {"role": "system", "content": "You are a helpful assistant."},  # Optional system message
    {"role": "user", "content": "Write a short story about a robot learning emotions."}  # User prompt
  ],
  max_tokens=100,  # Limits the length of the response
  temperature=0.7  # Adjusts creativity level (0.0 - 1.0)
)

# Print the response from the assistant
print(response['choices'][0]['message']['content'].strip())

'''





import openai

# Set your OpenAI API key
#openai.api_key = 'your-openai-api-key'
openai.api_key = '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'

def chatbot(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=100,
        temperature=0.7
    )
    return response['choices'][0]['message']['content']

# Chatbot interaction
while True:
    user_input = input("You: ")
    if user_input.lower() in ['exit', 'quit']:
        break
    response = chatbot(user_input)
    print(f"Bot: {response}")

