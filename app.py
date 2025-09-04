# from flask import Flask, render_template, request, jsonify, redirect, url_for
# from flask_socketio import SocketIO, emit
# from config import Config
# from database import init_db, save_candidate, get_candidate, save_quiz, get_quiz, save_result, get_results_joined
# from quiz_generator import generate_quiz
# from email_utils import send_quiz_link
# import uuid
# import json
# import os

# app = Flask(__name__)
# app.config.from_object(Config)

# # Real-time
# socketio = SocketIO(app, cors_allowed_origins="*")

# # Init DB
# init_db()

# def make_token():
#     return str(uuid.uuid4())[:8]

# @app.route("/")
# def root():
#     return redirect(url_for("hr_dashboard"))

# # ------------------ HR Dashboard ------------------

# @app.route("/hr")
# def hr_dashboard():
#     return render_template("hr_dashboard.html")

# @app.route("/api/hr/results")
# def api_hr_results():
#     rows = get_results_joined()
#     data = []
#     for (token, name, email, domain, score, details_json, submitted_at) in rows:
#         data.append({
#             "token": token, "name": name, "email": email, "domain": domain,
#             "score": score, "submitted_at": submitted_at,
#             "details": json.loads(details_json) if details_json else {}
#         })
#     return jsonify({"results": data})

# @app.route("/api/hr/generate_link", methods=["POST"])
# def api_generate_link():
#     payload = request.get_json(force=True)
#     name = payload.get("name", "").strip()
#     email = payload.get("email", "").strip()
#     domain = payload.get("domain", "").strip()

#     if not (name and email and domain):
#         return jsonify({"ok": False, "error": "Missing name/email/domain"}), 400

#     token = make_token()
#     link = f"{Config.APP_BASE_URL}/quiz/{token}"

#     # Save candidate
#     save_candidate(token, name, email, domain)

#     # Pre-generate quiz (so refresh won't change questions)
#     quiz = generate_quiz(domain)
#     save_quiz(token, quiz)

#     ok, err = send_quiz_link(email, name, link)
#     return jsonify({"ok": ok, "error": err if not ok else "", "token": token, "link": link})

# # ------------------ Candidate Quiz ------------------

# @app.route("/quiz/<token>")
# def quiz_page(token):
#     cand = get_candidate(token)
#     if not cand:
#         return render_template("quiz.html", invalid=True)
#     _, name, email, domain, _ = cand
#     quiz = get_quiz(token)
#     if not quiz:
#         # fallback if quiz missing
#         quiz = generate_quiz(domain)
#         save_quiz(token, quiz)
#     return render_template("quiz.html", invalid=False, token=token, name=name, domain=domain, quiz=quiz)

# @app.route("/api/quiz/submit/<token>", methods=["POST"])
# def api_quiz_submit(token):
#     cand = get_candidate(token)
#     if not cand:
#         return jsonify({"ok": False, "error": "Invalid token"}), 400
#     _, name, email, domain, _ = cand

#     payload = request.get_json(force=True)
#     answers = payload.get("answers", [])
#     quiz = get_quiz(token)
#     if not quiz or len(answers) != len(quiz):
#         return jsonify({"ok": False, "error": "Malformed submission"}), 400

#     # Evaluate
#     details = []
#     score = 0
#     for i, q in enumerate(quiz):
#         correct = q["answer"]
#         chosen_idx = int(answers[i]) if str(answers[i]).isdigit() else -1
#         chosen_text = q["options"][chosen_idx] if 0 <= chosen_idx < 4 else ""
#         is_correct = (chosen_text == correct)
#         if is_correct:
#             score += 1
#         details.append({
#             "qno": i + 1,
#             "question": q["question"],
#             "options": q["options"],
#             "chosen": chosen_text,
#             "correct": correct,
#             "result": "Correct" if is_correct else "Wrong"
#         })

#     # Save result
#     save_result(token, name, email, domain, score, details)

#     # Push real-time to HR
#     socketio.emit("result_submitted", {
#         "token": token, "name": name, "email": email, "domain": domain,
#         "score": score, "details": details
#     }, broadcast=True)

#     return jsonify({"ok": True, "score": score})
    
# if __name__ == "__main__":
#     # eventlet for websockets
#     socketio.run(app, host="0.0.0.0", port=5000)

































from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO
from database import save_candidate, get_candidate, save_result, get_results
from quiz_generator import generate_quiz, evaluate_quiz
from datetime import datetime
import uuid
from dotenv import load_dotenv
import os
from email_utils import send_quiz_link
from flask import Flask, jsonify, request, render_template



load_dotenv()  # ✅ Explicit path
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

app = Flask(__name__)
app.secret_key = "supersecretkey"
socketio = SocketIO(app)

# ---------------- HOME / HR DASHBOARD ----------------
@app.route("/", methods=["GET", "POST"])
def hr_dashboard():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        domain = request.form["domain"]
        token = str(uuid.uuid4())[:8]

        # Save candidate
        save_candidate(token, name, email, domain)

        # Generate link
        link = request.url_root + "quiz/" + token

        # Normally send email here (stub)
        ok, err = send_quiz_link(email, name, link)
        if not ok:
            print("❌ Email error:", err)
        else:
            print("✅ Email sent")

        return render_template(
        "hr_dashboard.html",
        link=link,
        name=name,
        email=email,
        domain=domain,
        results=get_results()
    )

    return render_template("hr_dashboard.html", results=get_results(), name="", email="", domain="")


# ---------------- CANDIDATE QUIZ PAGE ----------------
@app.route("/quiz/<token>")
def quiz_page(token):
    candidate = get_candidate(token)
    if not candidate:
        return render_template("quiz.html", invalid=True)

    name, email, domain = candidate[1], candidate[2], candidate[3]

    # # Generate and save quiz in session
    # quiz = generate_quiz(domain)
    # session[f"quiz_{token}"] = quiz

    # return render_template(
    #     "quiz.html",
    #     invalid=False,
    #     token=token,
    #     name=name,
    #     domain=domain,
    #     quiz=quiz,
    #     answers={}
    # )

    # Load quiz
    quiz = session.get(f"quiz_{token}")
    if not quiz:
        quiz = generate_quiz(domain)
        session[f"quiz_{token}"] = quiz

    # ✅ Load answers if already in session
    answers = session.get(f"answers_{token}", {})

    return render_template(
        "quiz.html",
        invalid=False,
        token=token,
        name=name,
        domain=domain,
        questions=quiz,
        answers=answers
    )


# ---------------- QUIZ SUBMISSION ----------------
# ---------------- SAVE ANSWER (AJAX) ----------------
@app.route("/save_answer/<token>", methods=["POST"])
def save_answer(token):
    data = request.form.to_dict()
    answers = session.get(f"answers_{token}", {})
    answers.update(data)   # merge with existing answers
    session[f"answers_{token}"] = answers
    return ("", 204)  # no content


@app.route("/submit/<token>", methods=["POST"])
def submit_quiz(token):
    answers = request.form.to_dict()

    # ✅ Get candidate info from DB
    candidate = get_candidate(token)
    if not candidate:
        return "❌ Invalid candidate token", 400

    name = candidate[1]
    email = candidate[2]
    domain = candidate[3]

    # ✅ Generate and evaluate quiz
    # quiz = generate_quiz(domain)
    quiz = session.get(f"quiz_{token}")   # ✅ use same quiz
    score, details = evaluate_quiz(quiz, answers)

    # ✅ Save result in DB
    save_result(token, name, email, score, str(details))


    # ✅ Emit result to HR dashboard in real-time
    socketio.emit("new_result", {
        "token": token,
        "name": name,
        "email": email,
        "domain": domain,
        "score": score
    })

    print("➡️ Raw form answers:", answers)
    return render_template("submitted.html", name=name, score=score)



if __name__ == "__main__":
    socketio.run(app, debug=True)













