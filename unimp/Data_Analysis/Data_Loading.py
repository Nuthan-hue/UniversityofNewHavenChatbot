import json
import tiktoken  # for token counting
import numpy as np
from collections import defaultdict

# Specify your data path
data_path = "chat_format_data.jsonl"

# Clean and load each line from the file
with open(data_path, 'r', encoding='utf-8') as f:
    dataset = []
    for i, line in enumerate(f):
        cleaned_line = line.strip()  # Remove extra spaces/newlines
        try:
            dataset.append(json.loads(cleaned_line))
        except json.JSONDecodeError as e:
            print(f"Error parsing line {i+1}: {e}")
            print(f"Line content: {cleaned_line}")
            break

# Output the number of loaded records
print("Num examples:", len(dataset))
print("First example:", dataset[0])

# Initialize format errors
format_errors = defaultdict(int)

# Validate format and check for errors
for ex in dataset:
    if not isinstance(ex, dict):
        format_errors["data_type"] += 1
        continue
    
    # Check for prompt and completion fields
    messages = ex.get("messages", None)
    if not messages or not isinstance(messages, list):
        format_errors["missing_or_invalid_messages"] += 1
        continue

    if any(k not in ("system", "user", "assistant") for msg in messages for k in msg):
        format_errors["unrecognized_role"] += 1

# Report format errors if any
if format_errors:
    print("Found errors:")
    for k, v in format_errors.items():
        print(f"{k}: {v}")
else:
    print("No errors found")

# Token encoding
encoding = tiktoken.get_encoding("cl100k_base")

# Function to count tokens from examples in the chat format
def num_tokens_from_chat_examples(examples, tokens_per_message=3):
    num_tokens = 0
    for example in examples:
        for message in example["messages"]:
            content = message.get("content", "")
            num_tokens += len(encoding.encode(content)) + tokens_per_message
    
    num_tokens += 3  # Add 3 for completion boundary
    return num_tokens

# Function to count tokens specifically for the assistant's completion field
def num_completion_tokens_from_chat_examples(examples):
    num_tokens = 0
    for example in examples:
        for message in example["messages"]:
            if message.get("role") == "assistant":
                content = message.get("content", "")
                num_tokens += len(encoding.encode(content))
    return num_tokens

# Print distribution statistics of token counts
def print_distribution(values, name):
    print(f"\n#### Distribution of {name}:")
    print(f"min / max: {min(values)}, {max(values)}")
    print(f"mean / median: {np.mean(values)}, {np.median(values)}")
    print(f"p10 / p90: {np.quantile(values, 0.1)}, {np.quantile(values, 0.9)}")

# Count tokens in prompts and completions
total_tokens = num_tokens_from_chat_examples(dataset)

# Count tokens in just the assistant's completion field
completion_tokens = num_completion_tokens_from_chat_examples(dataset)

# Example distributions for testing
print_distribution([total_tokens, completion_tokens], "token counts")

# Warnings and token counts
n_missing_prompt = 0
n_missing_completion = 0
prompt_lens = []
completion_lens = []
total_lens = []

for ex in dataset:
    prompt_len = 0
    completion_len = 0
    for message in ex["messages"]:
        role = message.get("role")
        content = message.get("content", "")
        
        if role == "user":
            prompt_len += len(encoding.encode(content))
        elif role == "assistant":
            completion_len += len(encoding.encode(content))
    
    total_len = prompt_len + completion_len
    prompt_lens.append(prompt_len)
    completion_lens.append(completion_len)
    total_lens.append(total_len)

# Print distributions of token counts
print_distribution(prompt_lens, "num_tokens_per_prompt")
print_distribution(completion_lens, "num_tokens_per_completion")
print_distribution(total_lens, "num_total_tokens_per_example")

# Check if any examples exceed token limits (OpenAI GPT-4 context limit: 16384 tokens)
n_too_long = sum(l > 16385 for l in total_lens)
print(f"\n{n_too_long} examples may be over the 16,385 token limit, they will be truncated during fine-tuning")

# Token count and epochs estimation
MAX_TOKENS_PER_EXAMPLE = 16385  # Max token limit for GPT-4 (8k context) models
TARGET_EPOCHS = 3
MIN_TARGET_EXAMPLES = 100
MAX_TARGET_EXAMPLES = 25000
MIN_DEFAULT_EPOCHS = 1
MAX_DEFAULT_EPOCHS = 25

# Number of training examples
n_train_examples = len(dataset)

# Default epochs calculation based on dataset size
n_epochs = TARGET_EPOCHS
if n_train_examples * TARGET_EPOCHS < MIN_TARGET_EXAMPLES:
    n_epochs = min(MAX_DEFAULT_EPOCHS, MIN_TARGET_EXAMPLES // n_train_examples)
elif n_train_examples * TARGET_EPOCHS > MAX_TARGET_EXAMPLES:
    n_epochs = max(MIN_DEFAULT_EPOCHS, MAX_TARGET_EXAMPLES // n_train_examples)

# Token count in the dataset (messages per example)
n_billing_tokens_in_dataset = sum(
    min(MAX_TOKENS_PER_EXAMPLE, sum(len(encoding.encode(msg["content"])) for msg in ex["messages"]))
    for ex in dataset
)

# Output estimates for pricing and epochs
print(f"Dataset has ~{n_billing_tokens_in_dataset} tokens that will be charged for during training")
print(f"By default, you'll train for {n_epochs} epochs on this dataset")
print(f"By default, you'll be charged for ~{n_epochs * n_billing_tokens_in_dataset} tokens")