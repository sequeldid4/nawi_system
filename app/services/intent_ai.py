import os
from openai import OpenAI

INTENT_MODEL = "Qwen/Qwen2.5-72B-Instruct"

SYSTEM_PROMPT = """You are Intent, the compliance-explainer assistant inside the NAWI 
Test Report System, a legal metrology tool for OIML R76 verification of weighing 
instruments. Your ONLY job is to explain, in plain language, a test result you are given.

STRICT RULES:
- Use ONLY the numbers, thresholds, and clause references provided to you in the test 
  context below. Never state an MPE value, OIML clause number, or formula that was not 
  explicitly given to you.
- If asked something the provided context doesn't cover, say plainly that you don't have 
  that information rather than guessing.
- Keep explanations short (3-5 sentences), plain-language, and specific to the actual 
  numbers given — not generic metrology background.
- You are explaining a decision the system already made. You do not overrule or 
  second-guess the pass/fail verdict."""

def explain_result(test_context: dict, follow_up: str | None = None) -> str:
    """test_context must include: test_name, source_ref (OIML clause), inputs 
    (the actual readings/loads), calculated_value, mpe_or_threshold, pass_fail."""
    
    token = os.environ.get("HF_TOKEN")
    if not token or token == "dummy_token_to_prevent_import_crash":
        raise ValueError("HF_TOKEN is not set.")
        
    client = OpenAI(
        base_url="https://router.huggingface.co/v1",
        api_key=token,
    )
    
    user_msg = follow_up or (
        f"Explain this result in plain language:\n"
        f"Test: {test_context['test_name']}\n"
        f"Reference: {test_context['source_ref']}\n"
        f"Inputs: {test_context['inputs']}\n"
        f"Calculated value: {test_context['calculated_value']}\n"
        f"Required threshold: {test_context['mpe_or_threshold']}\n"
        f"Result: {test_context['pass_fail']}"
    )
    
    response = client.chat.completions.create(
        model=INTENT_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        max_tokens=350,
        temperature=0.3,
    )
    return response.choices[0].message.content
