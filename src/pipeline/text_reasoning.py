from anthropic import AnthropicBedrock


def get_bedrock_client() -> AnthropicBedrock:
    """Return AnthropicBedrock client. aws_region must be explicit — does not read ~/.aws/config."""
    return AnthropicBedrock(
        aws_region="us-east-1"
        # Uses same credential chain as boto3: env vars, ~/.aws/credentials, instance profile
    )


def enhance_prompt_with_reasoning(
    client: AnthropicBedrock,
    base_prompt: str,
    product: dict,
    dry_run: bool = False,
) -> str:
    """Optionally enhance image prompt via Claude Sonnet 4.6. Falls back to base_prompt on error."""
    if dry_run:
        return base_prompt
    try:
        message = client.messages.create(
            model="anthropic.claude-sonnet-4-6",
            max_tokens=256,
            system=(
                "You are a packaging design expert. Improve the following image generation "
                "prompt for better visual quality. Return ONLY the improved prompt text, nothing else."
            ),
            messages=[{"role": "user", "content": base_prompt}],
        )
        enhanced = message.content[0].text.strip()
        return enhanced if enhanced else base_prompt
    except Exception:
        return base_prompt  # Always fall back — text reasoning is enhancement, not critical path
