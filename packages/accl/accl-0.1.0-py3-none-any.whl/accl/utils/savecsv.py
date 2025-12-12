import csv

def save_questions_to_csv(questions, filename="questions_output.csv"):
    """
    Save generated questions into a CSV file.
    :param questions: list of question dicts returned by LLM
    :param filename: output CSV filename
    """
    fieldnames = [
        "index",
        "strand",
        "subtopic",
        "question",
        "numbers",
        "expected_answer",
        "explanation",
    ]

    with open(filename, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for idx, q in enumerate(questions, start=1):
            writer.writerow({
                "index": idx,
                "strand": q.get("strand", ""),
                "subtopic": q.get("subtopic", ""),
                "question": q.get("question", ""),
                "numbers": str(q.get("numbers", "")),
                "expected_answer": q.get("expected_answer", ""),
                "explanation": q.get("explanation", ""),
            })

    print(f"\n✅ Saved {len(questions)} questions to: {filename}")
