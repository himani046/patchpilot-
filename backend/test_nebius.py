"""Manual Token Factory smoke test; requires configured .env."""
from app.llm.nebius_client import ask_nemotron
if __name__=="__main__": print(ask_nemotron("You are a concise software engineering assistant.","In one sentence, explain why a unit test might fail."))
