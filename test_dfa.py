# -*- coding: utf-8 -*-
"""
test_dfa.py
Pengujian sederhana terhadap fungsi run_dfa() pada app.py.
Jalankan dengan: python test_dfa.py
"""

from app import run_dfa

CASES = [
    # (input, seharusnya_diterima)
    ("1234567890", True),    # 10 digit, diawali bukan 0 -> valid
    ("9876543210", True),    # 10 digit, diawali bukan 0 -> valid
    ("0123456789", False),   # diawali 0 -> invalid
    ("12345", False),        # kurang dari 10 digit -> invalid
    ("123456789012", False), # lebih dari 10 digit -> invalid
    ("12345abcde", False),   # mengandung huruf -> invalid
    ("", False),             # kosong -> invalid
    ("1 234567890", False),  # mengandung spasi -> invalid
]


def main():
    passed = 0
    for text, expected in CASES:
        result = run_dfa(text)
        ok = result["accepted"] == expected
        status = "PASS" if ok else "FAIL"
        if ok:
            passed += 1
        print(f"[{status}] input={text!r:16} final_state={result['final_state']:6} "
              f"accepted={result['accepted']} (expected {expected})")

    print(f"\n{passed}/{len(CASES)} test case lulus.")


if __name__ == "__main__":
    main()
