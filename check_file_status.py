import openai

# Set your OpenAI API key
openai.api_key = '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'

# Retrieve file status using the file ID
file_id = "file-BjBDCx9iJe5LQVD7uaWjzx9A"  # Replace with your actual file ID

try:
    # Retrieve the file details
    file_status = openai.File.retrieve(file_id)

    # Print the status
    print(f"File Status: {file_status['status']}")
    print(f"File Details: {file_status}")

except Exception as e:
    print(f"An error occurred: {e}")