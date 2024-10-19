import json
import tiktoken # for token counting
import numpy as np
from collections import defaultdict
data_path = "prompt_completion_data.jsonl"

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



format_errors = defaultdict(int)

for ex in dataset:
    if not isinstance(ex, dict):
        format_errors["data_type"] += 1
        continue
    
    # Check for prompt and completion fields
    prompt = ex.get("prompt", None)
    completion = ex.get("completion", None)
    
    if not prompt or not isinstance(prompt, str):
        format_errors["missing_or_invalid_prompt"] += 1
        
    if not completion or not isinstance(completion, str):
        format_errors["missing_or_invalid_completion"] += 1
        
    # If there are unrecognized keys
    if any(k not in ("prompt", "completion") for k in ex):
        format_errors["unrecognized_key"] += 1

if format_errors:
    print("Found errors:")
    for k, v in format_errors.items():
        print(f"{k}: {v}")
else:
    print("No errors found")


encoding = tiktoken.get_encoding("cl100k_base")

# Function to count tokens in "prompt" and "completion" fields
def num_tokens_from_examples(examples, tokens_per_message=3):
    num_tokens = 0
    for example in examples:
        # Count tokens in the prompt
        prompt = example.get("prompt", "")
        num_tokens += len(encoding.encode(prompt)) + tokens_per_message
        
        # Count tokens in the completion
        completion = example.get("completion", "")
        num_tokens += len(encoding.encode(completion)) + tokens_per_message
    
    num_tokens += 3  # Add 3 for completion boundary (as in chat format)
    return num_tokens

# Function to count tokens specifically in the "completion" field
def num_completion_tokens_from_examples(examples):
    num_tokens = 0
    for example in examples:
        completion = example.get("completion", "")
        num_tokens += len(encoding.encode(completion))
    return num_tokens

# Function to print distribution statistics of token counts
def print_distribution(values, name):
    print(f"\n#### Distribution of {name}:")
    print(f"min / max: {min(values)}, {max(values)}")
    print(f"mean / median: {np.mean(values)}, {np.median(values)}")
    print(f"p10 / p90: {np.quantile(values, 0.1)}, {np.quantile(values, 0.9)}")

# Example usage with dataset (assumed list of examples with "prompt" and "completion")
# dataset = [{"prompt": "Some question?", "completion": "Some answer."}, ...]

# Count tokens in prompts and completions
total_tokens = num_tokens_from_examples(dataset)

# Count tokens in just the completions
completion_tokens = num_completion_tokens_from_examples(dataset)

# Example distributions for testing
print_distribution([total_tokens, completion_tokens], "token counts")

#	•	GPT-3.5 has a limit of 4096 tokens.
#	•	GPT-4 (8k context) has a limit of 8192 tokens.
#	•	GPT-4 (32k context) has a limit of 32,768 tokens.



# Warnings and token counts
n_missing_prompt = 0
n_missing_completion = 0
prompt_lens = []
completion_lens = []
total_lens = []

for ex in dataset:
    prompt = ex.get("prompt", None)
    completion = ex.get("completion", None)
    
    # Check if prompt or completion is missing
    if not prompt:
        n_missing_prompt += 1
    if not completion:
        n_missing_completion += 1
    
    # Count tokens for prompt, completion, and total
    prompt_len = len(encoding.encode(prompt)) if prompt else 0
    completion_len = len(encoding.encode(completion)) if completion else 0
    total_len = prompt_len + completion_len
    
    # Append lengths to respective lists
    prompt_lens.append(prompt_len)
    completion_lens.append(completion_len)
    total_lens.append(total_len)

# Print warnings for missing prompt or completion
print("Num examples missing prompt:", n_missing_prompt)
print("Num examples missing completion:", n_missing_completion)

# Print distributions of token counts
print_distribution(prompt_lens, "num_tokens_per_prompt")
print_distribution(completion_lens, "num_tokens_per_completion")
print_distribution(total_lens, "num_total_tokens_per_example")

# Check if any examples exceed token limits (OpenAI GPT-4 context limit: 16384 tokens)
n_too_long = sum(l > 16385 for l in total_lens)
print(f"\n{n_too_long} examples may be over the 16,385 token limit, they will be truncated during fine-tuning")


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

# Token count in the dataset (prompt + completion per example)
n_billing_tokens_in_dataset = sum(
    min(MAX_TOKENS_PER_EXAMPLE, len(encoding.encode(ex["prompt"])) + len(encoding.encode(ex["completion"])))
    for ex in dataset
)

# Output estimates for pricing and epochs
print(f"Dataset has ~{n_billing_tokens_in_dataset} tokens that will be charged for during training")
print(f"By default, you'll train for {n_epochs} epochs on this dataset")
print(f"By default, you'll be charged for ~{n_epochs * n_billing_tokens_in_dataset} tokens")