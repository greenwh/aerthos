import google.generativeai as genai
import os

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

model = genai.GenerativeModel("gemini-3-pro-image-preview")
try:
    response = model.generate_content("Draw a cute robot cat.")
    print("Response parts:", response.parts)
    # Check if there are inline data parts (images)
    for part in response.parts:
        if hasattr(part, 'inline_data') and part.inline_data:
            print("Found inline data (image)!")
            print("Mime type:", part.inline_data.mime_type)
        elif hasattr(part, 'text') and part.text:
            print("Text:", part.text)
except Exception as e:
    print("Error:", e)
