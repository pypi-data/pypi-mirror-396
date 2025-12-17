from .guardrails_client import TumerykGuardrailsClient

client = TumerykGuardrailsClient()

login = client.login
get_policies = client.get_policies
set_policy = client.set_policy
tumeryk_completions = client.tumeryk_completions
tumeryk_completions_async = client.tumeryk_completions_async
get_base_url = client.get_base_url
set_base_url = client.set_base_url
set_token = client.set_token
set_model_score = client.set_model_score
