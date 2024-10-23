import openai

# Set your OpenAI API key
openai.api_key = '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'  # Replace with your OpenAI API key

# Initiate fine-tuning with the uploaded training file
response = openai.FineTuningJob.create(
  training_file="file-BjBDCx9iJe5LQVD7uaWjzx9A",  # Replace with the actual file ID you got from file upload
  model="gpt-3.5-turbo"  # Ensure this model is available for fine-tuning
)

# Print the response to see the fine-tuning job details
print(response)