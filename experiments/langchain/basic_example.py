from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain.chat_models import init_chat_model


# ---------------------------
# 1. Define the state
# ---------------------------
class MyState(TypedDict):
    question: str
    answer: str


# ---------------------------
# 2. Build the graph
# ---------------------------
class UniversalLangGraph:
    def __init__(self, model_name="gemini-3-pro-preview"):
        """
        model_name can be:
        - "gpt-4.1", "gpt-4.1-mini"
        - "claude-3.5-sonnet"
        - "google_genai:gemini-2.0-flash"
        - "microsoft/Phi-3-mini-4k-instruct"
        - "ollama:llama3"
        - ANY supported model
        """
        self.llm = init_chat_model(model_name, temperature=0)
        self.graph = self._build_graph()

    # Node 1: Query LLM
    def generate(self, state: MyState) -> MyState:
        response = self.llm.invoke(state["question"])
        state["answer"] = response.content
        return state

    # Node 2: Simple post-processing
    def finalize(self, state: MyState) -> MyState:
        state["answer"] = state["answer"].strip()
        return state

    # Build LangGraph
    def _build_graph(self):
        workflow = StateGraph(MyState)

        workflow.add_node("generate", self.generate)
        workflow.add_node("finalize", self.finalize)

        workflow.set_entry_point("generate")
        workflow.add_edge("generate", "finalize")
        workflow.add_edge("finalize", END)

        return workflow.compile()

    # Run it
    def run(self, question: str):
        return self.graph.invoke({"question": question})


# ---------------------------
# 3. Run Example
# ---------------------------
if __name__ == "__main__":
    g = UniversalLangGraph(model_name="gemini-3-pro-preview")
    out = g.run("Explain LangGraph in one sentence.")
    print(out)
