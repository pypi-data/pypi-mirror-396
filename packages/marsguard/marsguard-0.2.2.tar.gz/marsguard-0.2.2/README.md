# MARSGuard Python SDK

A modular Python SDK for generating guardrails via the MARSGuard backend API. This SDK enforces request/response schemas using Pydantic and provides robust error handling with custom exceptions.

## Features

- Enforced request/response schema (Pydantic models)
- Modular, easy-to-use client interface
- Structured error handling with custom exceptions
- Minimal dependencies

## Installation

```bash
pip install marsguard
```

## SDK Structure

- **marsguard.sdk.MarsGuardClient**: Main client for interacting with the backend API.
- **marsguard.schemas.AppModel**: Model for application details.
- **marsguard.schemas.ModelSpec**: Model for LLM provider and model name.
- **marsguard.schemas.GenerateGuardrailsRequest**: Request schema for generating guardrails.
- **marsguard.schemas.MinimalGuardrailsResponse**: Response schema for generated guardrails.
- **marsguard.exceptions**: Structured exception hierarchy for robust error handling.

## Usage Example

Below is the recommended way to use the SDK, including a comprehensive `project_spec` template with dummy values. You can adapt this structure to your own use case.

```python
import logging
from marsguard import MarsGuardClient, AppModel, ModelSpec, GenerateGuardrailsRequest

    client = MarsGuardClient()

    # Recommended way to write project_spec: use dummy values and comments specifying what should be present
    project_spec = {
        "audience": {
            "user_types": ["user_type1", "user_type2"],  # List of user types (e.g., "patient", "doctor", "admin")
            "roles": ["role1", "role2"],  # Roles allowed to interact with the app (e.g., "anonymous_web_user")
            "age_band": "age_band_value",  # Age group of the audience (e.g., "18_plus", "all_ages")
            "trust_level": "trust_level_value"  # Trust level of the users (e.g., "low", "medium", "high")
        },
        "jurisdictions": ["Country1", "Country2"],  # List of jurisdictions/countries where the app is used
        "risk_profile": {
            "level": "risk_level_value",  # Overall risk level (e.g., "low", "medium", "high")
            "data_sensitivity": ["type1", "type2"],  # Types of sensitive data handled (e.g., "pii", "health")
            "threat_model_notes": "Notes on possible threats or risks"  # Notes on threat model
        },
        "interaction": {
            "mode": "interaction_mode",  # Mode of interaction (e.g., "chat", "voice")
            "uses_rag": False,  # Whether Retrieval-Augmented Generation (RAG) is used
            "tools_enabled": ["tool1", "tool2"]  # List of enabled tools/features
        },
        "content_rules": {
            "allowed_topics": [
                "topic1",
                "topic2"
            ],  # Topics the assistant is allowed to discuss
            "blocked_topics": [
                "blocked_topic1",
                "blocked_topic2"
            ],  # Topics the assistant must not discuss
            "languages": ["lang1", "lang2"],  # Supported languages/locales (e.g., "en-IN")
            "style": {
                "tone": "desired_tone",  # Tone of responses (e.g., "Neutral and informative")
                "max_response_tokens": 100,  # Maximum tokens in a response
                "allow_i_dont_know": True  # Whether the assistant can say "I don't know"
            }
        },
        "custom_restrictions": {
            "banned_terms": [
                "banned_term1",
                "banned_term2"
            ],  # Terms that must never appear in responses
            "org_policy_text": "Organization policy text for compliance"  # Organization policy text for compliance
        },
        "relaxation_factor": 0.0  # Optional: how much to relax guardrails (0 = strict, 1 = relaxed)
    }

    req = GenerateGuardrailsRequest(
        app=AppModel(
            name="My App",  # Name of your project
            description="Short description of what the app does"  # Optional description
        ),
        domain="YourDomain",  # The domain/context for the guardrails
        custom="Custom instructions or restrictions for the assistant",  # Any extra custom description
        model=ModelSpec(provider="provider_name", name="model_name"),  # LLM model to use
        project_spec=project_spec  # Recommended: detailed project specification as above
    )

    try:
        resp = client.generate_guardrails(req)
    except Exception as e:
```

See [`marsguard/example_usage.py`](marsguard/example_usage.py) for a complete, well-documented example.

## Error Handling

The SDK raises structured exceptions for robust error handling:

- `MarsGuardValidationError`: Raised for invalid request or response schema.
- `MarsGuardAPIError`: Raised for API errors (non-2xx HTTP responses). Includes status code and response text.
- `MarsGuardNetworkError`: Raised for network/connection errors.

Example:

```python
from marsguard.exceptions import MarsGuardAPIError, MarsGuardValidationError, MarsGuardNetworkError

try:
    resp = client.generate_guardrails(req)
except MarsGuardValidationError as ve:
    print("Validation error:", ve)
except MarsGuardAPIError as ae:
    print(f"API error {ae.status_code}: {ae.response_text}")
except MarsGuardNetworkError as ne:
    print("Network error:", ne)
```

## API Reference

- **MarsGuardClient**: Main entry point for backend interaction.
- **AppModel, ModelSpec, GenerateGuardrailsRequest**: Pydantic models for request construction.
- **MinimalGuardrailsResponse**: Pydantic model for response.
- **Exceptions**: All exceptions are in `marsguard.exceptions`.

See the source code and docstrings for detailed API documentation.

## Dependencies

- pydantic >=2.0,<3.0
- requests >=2.28,<3.0

