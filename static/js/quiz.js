if (typeof TOKEN !== "undefined" && TOKEN) {
  // 5 minutes
  let timeLeft = 300;
  const timeEl = document.getElementById("timeLeft");

  const intId = setInterval(() => {
    timeLeft -= 1;
    const m = String(Math.floor(timeLeft / 60)).padStart(2, "0");
    const s = String(timeLeft % 60).padStart(2, "0");
    timeEl.textContent = `${m}:${s}`;
    if (timeLeft <= 0) {
      clearInterval(intId);
      autoSubmit();
    }
  }, 1000);

  async function doSubmit(answers) {
    const r = await fetch(`/api/quiz/submit/${TOKEN}`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ answers })
    });
    const out = await r.json();
    const msg = document.getElementById("submitMsg");
    if (out.ok) {
      msg.innerHTML = `<div class="alert alert-success">Submitted! Score: ${out.score}/5</div>`;
      document.getElementById("quizForm").querySelector("button").disabled = true;
    } else {
      msg.innerHTML = `<div class="alert alert-danger">Error: ${out.error}</div>`;
    }
  }

  function collectAnswers() {
    const form = document.getElementById("quizForm");
    const answers = [];
    const qCount = form.querySelectorAll('[name^="q"]').length / 4; // 4 options per Q
    for (let i = 0; i < qCount; i++) {
      const chosen = form.querySelector(`input[name="q${i}"]:checked`);
      answers.push(chosen ? chosen.value : "-1");
    }
    return answers;
  }

  function autoSubmit() {
    const answers = collectAnswers();
    doSubmit(answers);
  }

  document.getElementById("quizForm").addEventListener("submit", (e) => {
    e.preventDefault();
    const answers = collectAnswers();
    doSubmit(answers);
  });
}
