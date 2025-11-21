import dspy
from dotenv import load_dotenv

from config import DEFAULT_MODEL, MAX_TOKENS, TEMPERATURE

load_dotenv()

# Configure DSPy using the central model settings
lm = dspy.LM(DEFAULT_MODEL, max_tokens=MAX_TOKENS, temperature=TEMPERATURE)
dspy.configure(lm=lm)
