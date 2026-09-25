import os, time
from openai import OpenAI

token = os.environ.get("HF_TOKEN")
if not token:
    print("NO TOKEN")
    exit(1)

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=token,
)

start = time.time()
try:
    response = client.chat.completions.create(
        model="meta-llama/Llama-3.1-8B-Instruct",
        messages=[{"role": "user", "content": "Explain OIML R76 repeatability testing."}],
        max_tokens=350,
        temperature=0.3,
    )
    print(response.choices[0].message.content)
except Exception as e:
    print("Error:", e)
print(f"Time: {time.time() - start:.2f}s")
