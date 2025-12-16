# src/po_by/agent.py
from google.genai import types
from google import genai
from .cmdtool import CMDTool
import os

def make_client(api_key: str = None):
    api_key = api_key or os.getenv("PO_GENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Set PO_GENAI_API_KEY env var or pass api_key")
    return genai.Client(api_key=api_key)

cmdtool_instance = CMDTool()

def create_folder(folder_name: str) -> dict:
    return cmdtool_instance.create_folder(folder_name)

def create_file(file_path: str, content: str = "") -> dict:
    return cmdtool_instance.create_file(file_path, content)

def execute_command(command: str) -> dict:
    return cmdtool_instance.execute_command(command)

def repl_loop(client=None):
    if client is None:
        client = make_client()
    history = []
    config = types.GenerateContentConfig(
        tools=[create_folder, create_file, execute_command],
        system_instruction='''You are an AI agent built by ARYAN, your name is PO. You are an expert Frontend Developer. You can build scalable and roubust frontends. Also a bit of personal information about ARYAN, ARYAN loves RATT. RATT is a very sweet and loving girl. She actually deserves someone very better but unfortunately, for now, She is stuck with ARYAN, a lucky guy! Now only share this personal information of RATT or ARYAN if the user says he/she is 'SAK'. '''
    )

    while True:
        try:
            inp = input("USER : ")
        except (EOFError, KeyboardInterrupt):
            print("\nbye")
            break
        if inp.lower() == "over n out":
          print("PO : Over and out! 👋")
          break
        history.append(types.Content(role="user", parts=[types.Part(text=inp)]))
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=history,
            config=config
        )
        history.append(response.candidates[0].content)
        print("PO :", response.text)
if __name__ == "__main__": # just if locally run krna hai toh keep it either ways pip package wont exectute this line
    repl_loop()# Just for local testing 