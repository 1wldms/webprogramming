from openai import OpenAI

client = OpenAI(api_key="")

try:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Hello!"}],
        max_tokens=10,
    )
    print(response.choices[0].message.content)
except Exception as e:
    print("Error:", e)