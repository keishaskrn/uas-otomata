(function () {
  const form = document.getElementById("validator-form");
  const input = document.getElementById("nomor_rekening");
  const ledgerStrip = document.getElementById("ledger-strip");
  const stampArea = document.getElementById("stamp-area");
  const resultDetail = document.getElementById("result-detail");

  function clearDiagramHighlight() {
    document.querySelectorAll(".dfa-node").forEach((n) => n.classList.remove("active"));
  }

  function highlightState(state) {
    clearDiagramHighlight();
    const node = document.getElementById(`node-${state}`);
    if (node) node.classList.add("active");
  }

  async function runValidation(nomor) {
    ledgerStrip.innerHTML = "";
    stampArea.innerHTML = "";
    resultDetail.textContent = "Memproses melalui mesin DFA…";
    clearDiagramHighlight();

    let data;
    try {
      const res = await fetch("/validate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nomor_rekening: nomor }),
      });
      data = await res.json();
      if (!res.ok) throw new Error(data.error || "Terjadi kesalahan.");
    } catch (err) {
      resultDetail.textContent = err.message || "Gagal menghubungi server.";
      return;
    }

    // trace[0] is the initial q0 entry with no symbol; render the rest.
    const steps = data.trace.slice(1);

    if (steps.length === 0) {
      ledgerStrip.innerHTML = '<p class="ledger-strip__placeholder">Tidak ada karakter untuk diproses.</p>';
    }

    steps.forEach((step, i) => {
      const cell = document.createElement("div");
      cell.className = "ledger-cell";
      if (step.to_state === "qtrap") cell.classList.add("is-trap");
      if (step.to_state === "q10") cell.classList.add("is-accept");
      cell.style.animationDelay = `${i * 70}ms`;

      const digit = document.createElement("div");
      digit.className = "ledger-cell__digit";
      digit.textContent = step.symbol;

      const stateLabel = document.createElement("div");
      stateLabel.className = "ledger-cell__state";
      stateLabel.textContent = step.to_state;

      cell.appendChild(digit);
      cell.appendChild(stateLabel);
      ledgerStrip.appendChild(cell);
    });

    highlightState(data.final_state);

    const stamp = document.createElement("div");
    stamp.className = "stamp " + (data.accepted ? "valid" : "reject");
    stamp.textContent = data.accepted ? "Sah — Valid" : "Ditolak";
    stampArea.appendChild(stamp);

    resultDetail.textContent =
      `${data.message}  ·  state akhir: ${data.final_state}  ·  panjang input: ${data.input.length} karakter`;
  }

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const nomor = input.value.trim();
    if (!nomor) {
      resultDetail.textContent = "Silakan masukkan nomor rekening terlebih dahulu.";
      return;
    }
    runValidation(nomor);
  });
})();
