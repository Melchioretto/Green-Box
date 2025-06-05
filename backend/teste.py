from dotenv import load_dotenv
import os

load_dotenv()

print("USUARIO =", os.getenv("USUARIO"))
print("SENHA =", os.getenv("SENHA"))
