import openai

# Set the API key (You might want to load this securely instead of hardcoding)
openai.api_key = "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"

# Corrected API call
response = openai.ChatCompletion.create(
    model="ftjob-6o96JL6lYY97XuU9axCPhmfr",
    prompt="University of New Haven located at?",
    max_tokens=100 
)

# Accessing the content of the response
print(response['choices'][0]['message']['content'].strip())