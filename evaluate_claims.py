import csv
import os
import re
from openai import OpenAI

# Configuration: Define files and the AI model version
INPUT_CSV = "claim_eval_input.csv"
OUTPUT_CSV = "claim_eval_output.csv"
MODEL = "gpt-4.1-mini"

client = OpenAI()

# System Instructions: These set the "rules" for the AI's behavior
SYSTEM_INSTRUCTIONS = (
    "You are reviewing a patent claim limitation against a reference excerpt.\n"
    "Decide whether the excerpt discloses the limitation.\n"
    "Use ONLY the excerpt as evidence.\n\n"
    "Return EXACTLY three lines, and do not omit any line:\n"
    "Assessment: <discloses | partially discloses | does not disclose>\n"
    "Rationale: <1–2 sentences based only on the excerpt>\n"
    "Confidence: <low | medium | high>\n"
)

def norm(s: str) -> str:
    """Removes messy whitespace and non-breaking space characters."""
    return " ".join((s or "").replace("\u00a0", " ").split()).strip()

def parse_three_lines(text: str):
    """
    Extract Assessment/Rationale/Confidence from the model output.
    Returns tuple (assessment, rationale, confidence) where any may be "" if missing.
    """
    text = (text or "").strip()

    def grab(label: str) -> str:
        m = re.search(rf"(?im)^{re.escape(label)}\s*:\s*(.+?)\s*$", text)
        return m.group(1).strip() if m else ""

    assessment = grab("Assessment").lower().strip()
    rationale = grab("Rationale").strip()
    confidence = grab("Confidence").lower().strip()

    # Exact allowed values only
    valid_assessments = {
        "discloses",
        "partially discloses",
        "does not disclose",
    }
    valid_confidence = {"low", "medium", "high"}

    if assessment not in valid_assessments:
        assessment = ""

    if confidence not in valid_confidence:
        confidence = ""

    return assessment, rationale, confidence

def format_three_lines(assessment: str, rationale: str, confidence: str) -> str:
    """Standardizes the final string for the spreadsheet output."""
    return f"Assessment: {assessment}\nRationale: {rationale}\nConfidence: {confidence}"

def call_model(prompt: str) -> str:
    """Executes the API call to OpenAI with temperature 0 for consistency."""
    resp = client.responses.create(
        model=MODEL,
        instructions=SYSTEM_INSTRUCTIONS,
        input=prompt,
        # Use low temperature for more consistent stuctured output
        temperature=0,
    )
    return getattr(resp, "output_text", "").strip()

def main():
    # 1. VALIDATION: Ensure the API key is present
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is not set")
        
    # 2. FILE LOADING: Read the CSV and clean up column names
    with open(INPUT_CSV, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise RuntimeError("CSV has no headers")

        reader.fieldnames = [h.strip() for h in reader.fieldnames]

        rows = []
        for row in reader:
            clean = {}
            for k, v in row.items():
                if k is not None:
                    clean[k.strip()] = v
            rows.append(clean)

    if not rows:
        raise RuntimeError("CSV contains no data rows")

    # 3. DATA CLEANING: Filter out empty rows
    rows = [
        r for r in rows
        if (r.get("row_id") or "").strip()
        or (r.get("claim_limitation") or "").strip()
        or (r.get("prior_art_excerpt") or "").strip()
    ]

    # Check for required column headers
    required_columns = {
        "row_id",
        "claim_limitation",
        "prior_art_excerpt",
        "ai_assessment",
        "human_review",
        "notes",
    }
    missing = required_columns - set(rows[0].keys())
    if missing:
        raise RuntimeError(f"Missing required columns: {sorted(missing)}")

    # Ensure we can store raw output for debugging
    if "ai_raw" not in rows[0]:
        # add ai_raw to output by appending to fieldnames at write-time
        pass

    fieldnames = list(rows[0].keys())
    if "ai_raw" not in fieldnames:
        fieldnames.append("ai_raw")
        
    # 4. MAIN LOOP: Process each row in the spreadsheet
    for row in rows:
        claim = norm(row.get("claim_limitation", ""))
        excerpt = norm(row.get("prior_art_excerpt", ""))

        if not claim or not excerpt:
            row["ai_raw"] = ""
            row["ai_assessment"] = ""
            continue

        base_prompt = f"Claim limitation:\n{claim}\n\nReference excerpt:\n{excerpt}\n"

        # First call
        raw1 = call_model(base_prompt)
        a, r, c = parse_three_lines(raw1)
       
        row["ai_raw"] = raw1

        # 6. FINAL STORAGE: Save results into the row dictionary
        if not a:
            row["ai_assessment"] = "REQUIRES HUMAN REVIEW: missing assessment"
        else:
            row["ai_assessment"] = format_three_lines(
            a, 
            r if r else "[missing rationale]", 
            c if c else "[missing confidence]")

    # 7. EXPORT: Write all processed rows to the new CSV
    with open(OUTPUT_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Done. Wrote {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
