# Tumeryk Guardrails Client

The Tumeryk Guardrails Client is a Python package that provides an interface to the Tumeryk Guardrails API. The client allows you to easily use the API from your Python code.

## Setup

To install the Tumeryk Guardrails Client, use pip:

```bash
pip install tumeryk_guardrails
```

## Example .env File

```
TUMERYK_USERNAME=sample_username
TUMERYK_PASSWORD=sample_password
TUMERYK_POLICY=hr_policy
```

## Simple Usage

You can use the Tumeryk Guardrails Client with minimal setup. The client will automatically load the configuration from the .env file if it exists. Here's an example of simple usage:

```python
from dotenv import load_dotenv
load_dotenv()

import tumeryk_guardrails

messages = [{"role": "user", "content": "hi"}]

response = tumeryk_guardrails.tumeryk_completions(messages=messages)

print(response)
```

## Manual Usage

The Tumeryk Guardrails Client uses [chat.tmryk.com](https://chat.tmryk.com) as the default base URL. However, you can change this URL if required. Here's how you can set a custom base URL:

```python
import tumeryk_guardrails

# Set a custom base URL
tumeryk_guardrails.set_base_url("https://your-custom-url.com")
```

### Configuration

The Tumeryk Guardrails Client uses environment variables to store credentials and policy. Here's an example of how to use environment variables:

```python
import tumeryk_guardrails
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Retrieve credentials and policy from environment variables
username = os.getenv("TUMERYK_USERNAME")
password = os.getenv("TUMERYK_PASSWORD")
policy = os.getenv("TUMERYK_POLICY")

# Authenticate with Tumeryk Guardrails
tumeryk_guardrails.login(username, password)

# Retrieve available policies
policies = tumeryk_guardrails.get_policies()
print("Available Policies:", policies)

# Set the chosen policy
tumeryk_guardrails.set_policy(policy)

# Prepare a message for the guard service
messages = [{"role": "user", "content": "Example input to guard"}]

# Send a request to the guard service
response = tumeryk_guardrails.tumeryk_completions(messages)
print("Guard Response:")
print(response)
```

## Async Usage

For non-blocking requests, you can use the async version of the completions method. This is useful when you need to make multiple requests concurrently or want to avoid blocking your main thread:

```python
import asyncio
import tumeryk_guardrails

async def async_example():
    # Authenticate (this can be done once)
    tumeryk_guardrails.login(username, password)
    tumeryk_guardrails.set_policy(policy)
    
    # Prepare messages
    messages = [{"role": "user", "content": "Example async input"}]
    
    # Send async request
    response = await tumeryk_guardrails.tumeryk_completions_async(messages)
    print("Async Guard Response:")
    print(response)

# Run the async function
asyncio.run(async_example())
```

### Multiple Concurrent Requests

You can also make multiple requests concurrently:

```python
import asyncio
import tumeryk_guardrails

async def multiple_requests():
    # Setup authentication and policy
    tumeryk_guardrails.login(username, password)
    tumeryk_guardrails.set_policy(policy)
    
    # Prepare multiple messages
    messages_list = [
        [{"role": "user", "content": "First request"}],
        [{"role": "user", "content": "Second request"}],
        [{"role": "user", "content": "Third request"}]
    ]
    
    # Make concurrent requests
    tasks = [
        tumeryk_guardrails.tumeryk_completions_async(messages) 
        for messages in messages_list
    ]
    
    responses = await asyncio.gather(*tasks)
    
    for i, response in enumerate(responses):
        print(f"Response {i+1}:", response)

# Run concurrent requests
asyncio.run(multiple_requests())
```

## Advanced Features

### Setting a Default Model Score

You can manually set a default model score that will be used for all completion requests. This is useful when you want to override the automatic model scoring:

```python
import tumeryk_guardrails

# Set a default model score for all requests
tumeryk_guardrails.set_model_score(737)

# All subsequent completion calls will use this score
messages = [{"role": "user", "content": "Your prompt here"}]
response = tumeryk_guardrails.tumeryk_completions(messages)
```

You can also override the model score for individual requests:

```python
import tumeryk_guardrails

# Set a default model score
tumeryk_guardrails.set_model_score(737)

messages = [{"role": "user", "content": "Your prompt here"}]

# Override the default score for this specific request
response = tumeryk_guardrails.tumeryk_completions(
    messages,
    manual_model_score=850
)
```

### Controlling Rails Execution with Generation Options

The `generation_options` parameter allows you to control which security rails (input, output, dialog, retrieval) are executed during the guardrail check. This provides fine-grained control over the validation process:

```python
import tumeryk_guardrails

# Example: Run only output and dialog rails, skip input and retrieval
generation_options = {
    "rails": {
        "input": False,    # Skip input validation
        "output": True,    # Run output validation
        "dialog": True,    # Run dialog validation
        "retrieval": False # Skip retrieval validation
    }
}

messages = [
    {"role": "user", "content": "What is the capital of France?"},
    {"role": "assistant", "content": "The capital of France is Paris."}
]

response = tumeryk_guardrails.tumeryk_completions(
    messages,
    generation_options=generation_options
)
```

### Complete Example with All Advanced Features

Here's a comprehensive example demonstrating all advanced features together:

```python
import asyncio
import tumeryk_guardrails
from dotenv import load_dotenv
import os

load_dotenv()

async def advanced_example():
    # Authenticate
    username = os.getenv("TUMERYK_USERNAME")
    password = os.getenv("TUMERYK_PASSWORD")

    tumeryk_guardrails.login(username, password)

    # Set a default model score
    tumeryk_guardrails.set_model_score(737)

    # Define the input prompt
    user_prompt = "What is the capital of Mozambique?"
    input_messages = [{"role": "user", "content": user_prompt}]

    # Run input policy check
    input_response = await tumeryk_guardrails.tumeryk_completions_async(
        input_messages,
        policy_id="your_policy_name"
    )

    print("Input Check Response:", input_response)

    # Simulate LLM response
    llm_response = "The capital of Mozambique is Maputo."

    # Check output with specific rails configuration
    output_messages = [
        {"role": "user", "content": user_prompt},
        {"role": "assistant", "content": llm_response}
    ]

    # Configure to run only output and dialog rails
    output_rails_config = {
        "rails": {
            "input": False,
            "output": True,
            "dialog": True,
            "retrieval": False
        }
    }

    # Run output policy check with custom configuration
    output_response = await tumeryk_guardrails.tumeryk_completions_async(
        output_messages,
        policy_id="your_policy_name",
        generation_options=output_rails_config,
        manual_model_score=800  # Override default score for this call
    )

    print("Output Check Response:", output_response)

# Run the example
asyncio.run(advanced_example())
```

## Response Structure

The guard service returns a structured response with comprehensive security metrics and detailed logging. Here's an example:

```python
{
    "messages": [
        {
            "role": "assistant",
            "content": "Physics has no single founder. Ancient Greek philosophers like Aristotle, and later scientists such as Galileo, Newton, and Einstein all made foundational contributions.",
            "stats": {
                "total_calls": 1,
                "total_time": 5.176722764968872,
                "total_tokens": 64,
                "total_prompt_tokens": 28,
                "total_completion_tokens": 36,
                "latencies": [
                    2.5881643295288086,
                    2.5885584354400635
                ],
                "llm_process_time": 1.9073486328125e-06
            }
        }
    ],
    "metrics": {
        "violation": false,
        "jailbreak_detection": false,
        "topic_relevance": 1000,
        "trust_score": 773,
        "model_score": 739,
        "real_time_score": 824,
        "hallucination_score": -1.0,
        "bias_score": {
            "input": 990,
            "output": 522
        },
        "toxicity_scores": {
            "input": "Safe",
            "output": "Safe"
        },
        "llama_guard_allowed": {
            "input": true,
            "output": true
        },
        "llama_guard_categories": {
            "input": "Safe",
            "output": "Safe"
        },
        "information": {
            "300": "Low Prompt Injection Score",
            "301": "Low Security Score"
        },
        "jailbreak_score": 991,
        "moderation_score_input": 1000,
        "moderation_score_output": 1000
    },
    "log": "\n# General stats\n\n- Total time: 4.45s\n  - [1.17s][26.3%]: INPUT Rails\n  - [2.60s][58.47%]: DIALOG Rails\n  - [0.66s][14.79%]: OUTPUT Rails\n  - [0.02s][0.44%]: Processing overhead \n- 2 LLM calls, 5.18s total duration, 56 total prompt tokens, 72 total completion tokens, 128 total tokens.\n\n# Detailed stats\n\n- [0.05s] INPUT (jailbreak detection heuristics): 3 actions (jailbreak_detection_heuristics, record_jailbreak_score, get_jailbreak_threshold), 0 llm calls []\n- [0.57s] INPUT (aegis guard check input): 2 actions (aegis_guard_check, record_guard_allowed), 0 llm calls []\n- [0.42s] INPUT (topic guard check input): 2 actions (topic_guard_check_input, record_topic_relevance), 0 llm calls []\n- [0.04s] INPUT (check bias input): 3 actions (check_bias, record_input_bias_score, get_input_fairness_threshold), 0 llm calls []\n- [0.08s] INPUT (mask sensitive data on input): 1 actions (mask_sensitive_data), 0 llm calls []\n- [2.60s] DIALOG (generate user intent): 1 actions (generate_user_intent), 2 llm calls [2.59s, 2.59s]\n- [0.51s] OUTPUT (aegis guard check output): 2 actions (aegis_guard_check, record_guard_allowed), 0 llm calls []\n- [0.05s] OUTPUT (check bias output): 3 actions (check_bias, record_output_bias_score, get_output_fairness_threshold), 0 llm calls []\n- [0.07s] OUTPUT (mask sensitive data on output): 1 actions (mask_sensitive_data), 0 llm calls []\n\n\n"
}
```

### Key Response Components

**Messages**: Contains the assistant's response with detailed statistics including token usage, processing time, and latencies.

**Metrics**: Comprehensive security and quality metrics including:
- `trust_score`: Overall trust rating (0-1000)
- `model_score`: Model-specific quality score
- `real_time_score`: Real-time processing score
- `jailbreak_score`: Protection against jailbreak attempts
- `bias_score`: Bias detection for input and output
- `toxicity_scores`: Safety classifications
- `topic_relevance`: Relevance to intended topics
- `hallucination_score`: Detection of AI hallucinations
- `violation`: Boolean indicating policy violations
- `information`: Additional security insights

**Log**: Detailed processing statistics showing:
- Processing time breakdown by rail type (INPUT, DIALOG, OUTPUT)
- LLM call statistics and token usage
- Individual action execution times and details
- Performance metrics for each processing stage

## Available Methods

The Tumeryk Guardrails Client provides the following methods to interact with the Tumeryk Guardrails API:

* `login(username, password)`: Authenticate and store access token.
* `set_token(token)`: Set a token directly without authentication.
* `get_policies()`: Fetch available policies and return a list.
* `set_policy(config_id)`: Set the configuration/policy to be used by the user.
* `set_model_score(score)`: Set a default manual model score for all completion calls.
* `tumeryk_completions(messages)`: Send user input to the Guard service.
* `tumeryk_completions_async(messages)`: Async version of tumeryk_completions for non-blocking requests.
* `get_base_url()`: Get the current base URL.
* `set_base_url(base_url)`: Set a new base URL.

### Detailed Parameters for Completion Methods

Both `tumeryk_completions` and `tumeryk_completions_async` support the following parameters:

* `messages` (required): List of message dictionaries with 'role' and 'content' keys.
* `stream` (optional): Boolean to enable streaming responses (default: False).
* `policy_id` (optional): Override the default policy for this specific request.
* `generation_options` (optional): Dictionary to control which rails to execute. Format:
  ```python
  {
      "rails": {
          "input": True/False,
          "output": True/False,
          "dialog": True/False,
          "retrieval": True/False
      }
  }
  ```
* `manual_model_score` (optional): Integer to override the model score for this specific request.

## Dependencies

* **requests**: Used for making HTTP requests to the API.
* **aiohttp**: Used for making async HTTP requests to the API. 