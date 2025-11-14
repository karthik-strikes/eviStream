import dspy
from dotenv import load_dotenv
load_dotenv()

# Set your API key (uncomment and add your key)
# os.environ["OPENAI_API_KEY"] = "your-api-key-here"

# Configure DSPy with OpenAI GPT-4o-mini for cost efficiency
lm = dspy.LM('gemini/gemini-2.5-pro', max_tokens=20000, temperature=1.0)
# lm = dspy.LM('openai/gpt-5-mini-2025-08-07', max_tokens=20000, temperature=1.0)
# lm = dspy.LM("anthropic/claude-sonnet-4-5-20250929" , max_tokens=20000, temperature=1.0)
dspy.configure(lm=lm)

print("Language model configured successfully")
