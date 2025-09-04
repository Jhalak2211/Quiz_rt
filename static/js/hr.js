const socket = io();

function renderRow(r) {
  const tr = document.createElement("tr");
  tr.innerHTML = `
    <td>${r.name}</td>
    <td>${r.email}</td>
    <td>${r.domain}</td>
    <td>${r.score}</td>
    <td>${new Date(r.submitted_at).toLocaleString()}</td>
    <td>
      <button class="btn btn-sm btn-outline-primary" data-token="${r.token}">View</button>
    </td>
  `;
  // view details
  tr.querySelector("button").addEventListener("click", () => {
    const details = r.details || [];
    let html = `<h5>${r.name} — ${r.domain}</h5><ul>`;
    for (const d of details) {
      html += `<li><strong>Q${d.qno}:</strong> ${d.question}<br>
        Chosen: ${d.chosen || "(none)"}; Correct: ${d.correct} — <em>${d.result}</em></li>`;
    }
    html += "</ul>";
    const modal = document.createElement("div");
    modal.className = "p-3 border rounded bg-light";
    modal.innerHTML = html;
    const container = document.getElementById("genResult");
    container.innerHTML = "";
    container.appendChild(modal);
    modal.scrollIntoView({ behavior: "smooth" });
  });
  return tr;
}

async function loadResults() {
  const r = await fetch("/api/hr/results");
  const data = await r.json();
  const body = document.getElementById("resultsBody");
  body.innerHTML = "";
  for (const row of data.results) {
    body.appendChild(renderRow(row));
  }
}

document.getElementById("genForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const fd = new FormData(e.target);
  const payload = {
    name: fd.get("name"),
    email: fd.get("email"),
    domain: fd.get("domain"),
  };
  const res = await fetch("/api/hr/generate_link", {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify(payload)
  });
  const out = await res.json();
  const box = document.getElementById("genResult");
  if (out.ok) {
    box.innerHTML = `
      <div class="alert alert-success mb-2">Email sent successfully.</div>
      <div class="alert alert-info">Reference Link: <a href="${out.link}" target="_blank">${out.link}</a></div>
    `;
  } else {
    box.innerHTML = `<div class="alert alert-danger">Failed: ${out.error}</div>`;
  }
});

socket.on("connect", () => {
  // initial load
  loadResults();
});

socket.on("result_submitted", (payload) => {
  // prepend the new row
  const body = document.getElementById("resultsBody");
  const tr = renderRow({
    ...payload,
    submitted_at: new Date().toISOString()
  });
  body.prepend(tr);
});
