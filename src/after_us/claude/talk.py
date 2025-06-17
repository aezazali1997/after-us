
from google import genai

client = genai.Client(api_key="AIzaSyCKGa99UxZNmW-WTVN2U3IIYJCPBU5C1I8")

def get_response(prompt: str) -> str:
    response = client.models.generate_content(
    model="gemini-2.0-flash", contents=prompt
)
    return response.text