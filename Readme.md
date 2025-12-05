Driver Drowsiness Detection (Python 3.13 Compatible)

This project detects driver drowsiness using:
- Face detection
- Eye detection
- Eye closure duration logic
- Alarm alert system

Technology Used:
- OpenCV
- NumPy
- PyGame

How to Run:

1. Install dependencies:
   pip install -r requirements.txt

2. Run the project:
   python main.py

3. Press 'q' to quit.

Logic:
If eyes are not detected for continuous frames → DROWSY → Alarm rings.
