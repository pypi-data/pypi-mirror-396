import json
import os
from datetime import datetime

def save_questions_to_json(questions, filename="stat_prob_questions.json", template="unknown"):
    """
    Saves questions with template + meta + LLM question.
    """
        # Ensure the data directory exists
    os.makedirs("data", exist_ok=True)

    # Create unique timestamp prefix
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Build final unique filename
    unique_filename = f"{timestamp}_{filename}"
    
    full_path = os.path.join("data", unique_filename)


    output = {
        "template": template,
        "questions": questions
    }

    with open(full_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=4, ensure_ascii=False)

    print(f"\n💾 Saved {len(questions)} questions to {unique_filename}")
