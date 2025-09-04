# import random
# import os
# import google.generativeai as genai
# from dotenv import load_dotenv
# load_dotenv()


# # Configure Gemini if API key available
# API_KEY = os.getenv("GEMINI_API_KEY")
# print("Loaded GEMINI_API_KEY:", API_KEY[:5] + "*****" if API_KEY else None)

# if API_KEY:
#     genai.configure(api_key=API_KEY)
# else:
#     print("⚠️ Warning: GEMINI_API_KEY not set. Falling back to dummy questions.")

# # ---------- Generate Quiz ----------
# def generate_quiz(domain):
#     if API_KEY:
#         try:
#             prompt = f"Generate 5 multiple-choice questions for {domain}. Each question should have 4 options (A, B, C, D). Return in JSON format."
#             model = genai.GenerativeModel("gemini-pro")
#             response = model.generate_content(prompt)
#             import json
#             questions = json.loads(response.text)
#             return questions
#         except Exception as e:
#             print("Gemini error:", e)

#     # --- Fallback dummy questions if Gemini not working ---
#     dummy = [
#         {"question": f"What is {domain} Question {i+1}?", 
#          "options": [f"Option A{i+1}", f"Option B{i+1}", f"Option C{i+1}", f"Option D{i+1}"], 
#          "answer": random.choice(["Option A1","Option B1","Option C1","Option D1"])}
#         for i in range(5)
#     ]
#     return dummy

# # ---------- Evaluate Quiz ----------
# def evaluate_quiz(quiz, answers):
#     score = 0
#     details = []
#     for i, q in enumerate(quiz):
#         correct = q.get("answer", "")
#         # ✅ use string key since answers dict comes from form
#         user_ans = answers.get(str(i), "")
#         if user_ans == correct:
#             score += 1
#         details.append({
#             "question": q["question"],
#             "your_answer": user_ans,
#             "correct": correct
#         })
#     return score, details



















import random
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini if API key available
API_KEY = os.getenv("GEMINI_API_KEY")
print("Loaded GEMINI_API_KEY:", API_KEY[:5] + "*****" if API_KEY else None)

if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    print("⚠️ Warning: GEMINI_API_KEY not set. Falling back to dummy questions.")

# ---------- Generate Quiz ----------
def generate_quiz(domain: str):
    """
    Generate a 5-question multiple-choice quiz for the given domain using Gemini.
    Falls back to dummy questions if Gemini fails.
    """
    if API_KEY:
        try:
            prompt = (
                f"Generate 5 multiple-choice questions for {domain}. "
                f"Each question should have 4 options (A, B, C, D). "
                f"Provide the correct answer for each question. "
                f"Return ONLY a valid JSON array in the format:\n"
                f'[{{"question": "...", "options": ["A", "B", "C", "D"], "answer": "correct option"}}, ...]'
            )

            # ✅ use a supported Gemini model
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)

            raw_text = response.text.strip()
            print("Gemini raw response:", raw_text[:200], "..." if len(raw_text) > 200 else "")

            # Clean response in case Gemini wraps with ```json fences
            if raw_text.startswith("```"):
                raw_text = raw_text.strip("`").replace("json", "", 1).strip()

            questions = json.loads(raw_text)
            # add ids if missing
            for i, q in enumerate(questions, start=1):
                q["id"] = i
            return questions

        except Exception as e:
            print("Gemini error:", e)

    # --- Fallback dummy questions if Gemini not working ---
    dummy = [
        {
            "id": i + 1,
            "question": f"What is {domain} Question {i+1}?",
            "options": [
                f"Option A{i+1}",
                f"Option B{i+1}",
                f"Option C{i+1}",
                f"Option D{i+1}",
            ],
            "answer": f"Option A{i+1}",
        }
        for i in range(5)
    ]
    return dummy

# ---------- Evaluate Quiz ----------
# def evaluate_quiz(quiz, answers):
#     """
#     Compare submitted answers with correct answers and calculate score.
#     Handles both full option text and A/B/C/D/OptionX style answers.
#     """
#     score = 0
#     details = []

#     for i, q in enumerate(quiz):
#         # Candidate's submitted answer
#         user_ans = answers.get(str(i), "").strip()
#         user_ans_norm = user_ans.lower()

#         # Correct answer from Gemini
#         correct_raw = str(q.get("answer", "")).strip()
#         correct_norm = correct_raw.lower()

#         # Case 1: Gemini returned just a letter (A/B/C/D)
#         if correct_norm in ["a", "b", "c", "d"]:
#             idx = ord(correct_norm) - ord("a")
#             if 0 <= idx < len(q["options"]):
#                 correct_norm = q["options"][idx].strip().lower()

#         # Case 2: Gemini returned "Option A/B/C/D"
#         elif correct_norm.startswith("option "):
#             letter = correct_norm.split()[-1].lower()
#             if letter in ["a", "b", "c", "d"]:
#                 idx = ord(letter) - ord("a")
#                 if 0 <= idx < len(q["options"]):
#                     correct_norm = q["options"][idx].strip().lower()

#         # Case 3: Already full text → nothing to change

#         # Compare
#         is_correct = user_ans_norm == correct_norm
#         if is_correct:
#             score += 1

#         details.append({
#             "qno": i + 1,
#             "question": q["question"],
#             "your_answer": user_ans,
#             "correct_answer": correct_raw,
#             "result": "Correct" if is_correct else "Wrong"
#         })

#     return score, details


def evaluate_quiz(quiz, answers):
    score = 0
    details = []

    for q in quiz:
        qid = str(q.get("id"))  # ✅ match how form names inputs
        user_ans = answers.get(qid, "").strip().lower()

        correct_raw = str(q.get("answer", "")).strip()
        correct_norm = correct_raw.lower()

        # Case 1: Gemini returned just a letter (A/B/C/D)
        if correct_norm in ["a", "b", "c", "d"]:
            idx = ord(correct_norm) - ord("a")
            if 0 <= idx < len(q["options"]):
                correct_norm = q["options"][idx].strip().lower()

        # Case 2: Gemini returned "Option A/B/C/D"
        elif correct_norm.startswith("option "):
            letter = correct_norm.split()[-1].lower()
            if letter in ["a", "b", "c", "d"]:
                idx = ord(letter) - ord("a")
                if 0 <= idx < len(q["options"]):
                    correct_norm = q["options"][idx].strip().lower()

        # Compare
        is_correct = user_ans == correct_norm
        if is_correct:
            score += 1

        details.append({
            "qno": qid,
            "question": q["question"],
            "your_answer": user_ans,
            "correct_answer": correct_raw,
            "result": "Correct" if is_correct else "Wrong"
        })

    print("Form answers:", answers)
    print("Evaluation details:", details)

    return score, details
