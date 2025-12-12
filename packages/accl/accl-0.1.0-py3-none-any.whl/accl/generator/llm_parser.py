
def parse_json_from_llm(text: str):
    """Extract JSON from LLM output that may contain ```json ... ``` or extra text."""
    import json, re

    if not isinstance(text, str):
        raise ValueError("Expected string from LLM")

    cleaned = text.strip()

    # 1) Remove leading/trailing code fences
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)

    # 2) If model wrapped JSON with prose, try to isolate the JSON part
    #    Find the first '{' or '[' and last matching '}' or ']'
    first_brace = cleaned.find("{")
    first_bracket = cleaned.find("[")
    candidates = [i for i in [first_brace, first_bracket] if i != -1]

    if candidates:
        start = min(candidates)
        last_brace = cleaned.rfind("}")
        last_bracket = cleaned.rfind("]")
        end = max(last_brace, last_bracket)
        if end > start:
            cleaned = cleaned[start:end+1]

    cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        fixed = re.sub(r"(?m)^(\s*)([A-Za-z_][A-Za-z0-9_]*)(\s*):",
                       r'\1"\2":', cleaned)
        try:
            return json.loads(fixed)
        except Exception as e:
            print("===== CLEANED LLM OUTPUT (for debugging) =====")
            print(cleaned)
            print("==============================================")
            raise e
