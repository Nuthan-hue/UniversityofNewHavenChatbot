import openai

# Set your OpenAI API key
openai.api_key = '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'

# Upload the file for fine-tuning
response = openai.File.create(
  file=open("chat_format_data.jsonl", "rb"),
  purpose="fine-tune"
)

# Print the response to see the file details
print(response["id"])