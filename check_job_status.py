import openai

# Set your OpenAI API key
openai.api_key = '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'  # Replace with your OpenAI API key

# Check the status of the fine-tuning job
job_id = "ftjob-m4JgvdueZH1bfbEfazOgiwhH"  # Replace with your fine-tuning job ID
response = openai.FineTuningJob.retrieve(job_id)

# Print the status of the fine-tuning job
print(response)