import os
import subprocess
import json
import requests
import sys
from datetime import datetime

print("oops")
# FUCK AM I DOING

# Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
MODEL = "llama-3.3-70b-versatile"

if not GROQ_API_KEY:
    print("Error: GROQ_API_KEY is missing.")
    # In a real app we might exit, but for a demo script we'll just warn
    # sys.exit(1)

def get_git_diff():
    """
    Retrieves the code changes between the main branch and the current commit.
    'origin/main...HEAD' gives us the changes in this PR.
    """
    try:
        # Execute git diff command
        result = subprocess.run(
            ["git", "diff", "origin/main...HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error getting git diff: {e}")
        # Handle error if not a git directory
        return "print('Hello World')\n# No docstring here"

def review_code(diff_content):
    """
    Sends the git diff to the Groq API (Llama 3) and asks for a structured review.
    """
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    # System prompt definition
    system_prompt = """
    You are a strict and humorous Senior Software Engineer code reviewer.
    Review the provided python code changes (git diff).
    
    Rules:
    1. Reject code with 'print()' statements (debugging leftovers).
    2. Reject code with missing docstrings/comments.
    3. Reject code with hardcoded secrets/passwords.
    
    Output strictly in JSON format with these keys:
    - "status": "APPROVE" or "REJECT"
    - "issues": [list of string explanations]
    - "humorous_roast": A short, witty, sarcastic roast of the code.
    """

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Code Diff:\n{diff_content}"}
        ],
        "response_format": {"type": "json_object"}
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f"Error calling Groq API: {e}")
        # Return a fallback JSON if API fails
        return json.dumps({
            "status": "REJECT", 
            "issues": ["API Error: Could not reach the brain."], 
            "humorous_roast": "My brain is disconnected, but your code is probably bad anyway."
        })

def main():
    print("Starting AI Code Review...")
    
    # Retrieve git diff
    diff = get_git_diff()
    if not diff.strip():
        print("No changes found.")
        sys.exit(0)

    # Step 2: Ask the AI Judge
    result_json_str = review_code(diff)
   
    # Clean up potential markdown backticks if the AI added them
    clean_json_str = result_json_str.strip().replace("```json", "").replace("```", "")
    
    try:
        result_data = json.loads(clean_json_str)
    except json.JSONDecodeError:
        print("Error: Could not parse JSON from AI response.")
        # Fallback
        result_data = {"status": "REJECT", "issues": ["AI Output Error"], "humorous_roast": "I'm speechless."}
    
    status = result_data.get("status", "REJECT")
    issues = result_data.get("issues", [])
    roast = result_data.get("humorous_roast", "No roast generated.")
    
    print(f"Verdict: {status}")
    print(f"Roast: {roast}")

    # Save results to log file
    # Append structured log entry
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "status": status,
        "roast": roast,
        "issues_count": len(issues)
    }
    
    # 'a' mode means append (add to the end) instead of overwriting
    with open("review_logs.jsonl", "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    # Generate Markdown report for CML
    report_content = f"""
# AI Code Review Report

**Verdict**: {status}

> "{roast}"

## Issues Found
"""
    for issue in issues:
        report_content += f"- {issue}\n"
        
    with open("review_report.md", "w") as f:
        f.write(report_content)

    # Exit with status code based on verdict
    if status == "REJECT":
        print("Build failed due to bad code.")
        sys.exit(1)
    else:
        print("Code approved!")
        sys.exit(0)

if __name__ == "__main__":
    main()
