# -*- coding: utf-8 -*-
"""
app.py
Implementasi Deterministic Finite Automata (DFA) untuk Validasi
Nomor Rekening Sederhana Berbasis Website.

Definisi Formal DFA (5-tuple): M = (Q, Sigma, delta, q0, F)

Q      = {q0, q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, qtrap}
Sigma  = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9}   (karakter di luar himpunan ini
                                            otomatis dianggap invalid -> qtrap)
q0     = state awal
F      = {q10}   (satu-satunya accepting state)

Aturan bisnis yang dimodelkan:
    Nomor rekening dinyatakan VALID jika dan hanya jika:
    1. Terdiri dari TEPAT 10 digit angka.
    2. Digit pertama TIDAK BOLEH '0' (merepresentasikan kode bank/cabang
       yang harus dimulai dari 1-9).
    3. Digit ke-2 sampai ke-10 bebas berupa angka 0-9.
    4. Tidak boleh mengandung karakter selain digit (spasi, huruf, simbol, dll).

Fungsi transisi delta:
    q0  --[1-9]--> q1        q0  --[0, non-digit]--> qtrap
    qi  --[0-9]--> q(i+1)    untuk i = 1..9
    q10 --[0-9]--> qtrap     (kepanjangan, lebih dari 10 digit)
    qtrap --[apa pun]--> qtrap   (dead state / trap state)
"""

from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# ---------------------------------------------------------------------------
# DEFINISI FORMAL DFA
# ---------------------------------------------------------------------------
STATES = ["q0", "q1", "q2", "q3", "q4", "q5", "q6", "q7", "q8", "q9", "q10", "qtrap"]
ALPHABET = list("0123456789")
START_STATE = "q0"
ACCEPT_STATES = {"q10"}
TRAP_STATE = "qtrap"


def build_transition_table():
    """Membangun tabel transisi delta: delta[state][simbol] = state_tujuan."""
    delta = {state: {} for state in STATES}

    # q0: hanya digit 1-9 yang boleh maju ke q1, digit '0' -> trap
    for d in ALPHABET:
        delta["q0"][d] = "q1" if d != "0" else TRAP_STATE

    # q1..q9: digit 0-9 apa pun maju ke state berikutnya
    for i in range(1, 10):
        current = f"q{i}"
        nxt = f"q{i + 1}"
        for d in ALPHABET:
            delta[current][d] = nxt

    # q10 (accepting): digit tambahan berarti kepanjangan -> trap
    for d in ALPHABET:
        delta["q10"][d] = TRAP_STATE

    # qtrap: sekali masuk trap, selamanya trap
    for d in ALPHABET:
        delta[TRAP_STATE][d] = TRAP_STATE

    return delta


DELTA = build_transition_table()

STATE_LABELS = {
    "q0": "Mulai (belum ada digit)",
    "q1": "1 digit terbaca",
    "q2": "2 digit terbaca",
    "q3": "3 digit terbaca",
    "q4": "4 digit terbaca",
    "q5": "5 digit terbaca",
    "q6": "6 digit terbaca",
    "q7": "7 digit terbaca",
    "q8": "8 digit terbaca",
    "q9": "9 digit terbaca",
    "q10": "10 digit terbaca (ACCEPT)",
    "qtrap": "Ditolak / tidak valid (TRAP)",
}


def run_dfa(input_string: str):
    """
    Menjalankan DFA terhadap sebuah string input, karakter demi karakter.
    Mengembalikan dict berisi jejak (trace) transisi, state akhir,
    dan status diterima/ditolak, mengikuti definisi delta di atas.
    """
    state = START_STATE
    trace = [{
        "step": 0,
        "symbol": None,
        "from_state": None,
        "to_state": state,
        "label": STATE_LABELS[state],
    }]

    for idx, ch in enumerate(input_string, start=1):
        prev = state
        if ch in ALPHABET:
            state = DELTA[state][ch]
        else:
            state = TRAP_STATE
        trace.append({
            "step": idx,
            "symbol": ch,
            "from_state": prev,
            "to_state": state,
            "label": STATE_LABELS[state],
        })

    accepted = state in ACCEPT_STATES
    return {
        "input": input_string,
        "trace": trace,
        "final_state": state,
        "accepted": accepted,
        "message": (
            "Nomor rekening VALID: 10 digit, diawali digit 1-9."
            if accepted else
            "Nomor rekening TIDAK VALID sesuai aturan DFA."
        ),
    }


# ---------------------------------------------------------------------------
# ROUTES
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    return render_template(
        "index.html",
        states=STATES,
        alphabet=ALPHABET,
        accept_states=list(ACCEPT_STATES),
        start_state=START_STATE,
    )


@app.route("/validate", methods=["POST"])
def validate():
    data = request.get_json(silent=True) or {}
    nomor_rekening = str(data.get("nomor_rekening", "")).strip()

    if not nomor_rekening:
        return jsonify({"error": "Nomor rekening tidak boleh kosong."}), 400
    if len(nomor_rekening) > 20:
        return jsonify({"error": "Input terlalu panjang."}), 400

    result = run_dfa(nomor_rekening)
    return jsonify(result)


@app.route("/api/dfa-definition")
def dfa_definition():
    """Mengembalikan definisi formal DFA (Q, Sigma, delta, q0, F) sebagai JSON,
    berguna untuk ditampilkan di diagram transisi pada halaman utama."""
    return jsonify({
        "Q": STATES,
        "Sigma": ALPHABET,
        "q0": START_STATE,
        "F": list(ACCEPT_STATES),
        "delta": DELTA,
    })


import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
