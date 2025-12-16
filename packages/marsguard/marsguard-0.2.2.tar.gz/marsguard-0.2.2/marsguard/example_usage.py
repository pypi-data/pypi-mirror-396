"""
Example usage of the MARSGuard SDK with enforced schema.
This script demonstrates the recommended way to construct a comprehensive project_spec for the SDK.
You should include all relevant fields in project_spec.
This is the recommended way to write project_spec, but you can write it differently as long as it expresses the same information.
"""

import logging
from marsguard import MarsGuardClient, AppModel, ModelSpec, GenerateGuardrailsRequest

# Configure logging to output to the console
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

if __name__ == "__main__":
    logging.info("Starting MARSGuard SDK example usage script.")

    # Instantiate the MarsGuardClient (uses a fixed backend URL internally)
    logging.info("Instantiating MarsGuardClient...")
    client = MarsGuardClient()

    # Recommended way to write project_spec
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

    # Construct the request object using the enforced schema
    logging.info("Building GenerateGuardrailsRequest object...")
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
    logging.info(f"Request object: {req!r}")

    # Call the backend and handle errors gracefully
    try:
        logging.info("Sending request to backend...")
        resp = client.generate_guardrails(req)
        logging.info("Received response from backend.")
        # Log the guardrails (the main result from the backend)
        logging.info("Guardrails response:")
        logging.info(resp.guardrails)
    except Exception as e:
        # Log any errors that occur (validation, network, or API errors)
        logging.error(f"Error occurred during guardrails generation: {e}")
