from flask import Flask, render_template
import google.generativeai as genai
import re
import ast

app = Flask(__name__)

# Set up Gemini API
genai.configure(api_key="AIzaSyAvunNq7e7nsASv4eY75KrZKaFpBeHkue0")

@app.route('/')
def home():
    letters = ['n','u','r']  # Change this for different test cases

    # Strict prompt to force exact list format
    prompt = f"""
You are a word solver. Using only the given letters: {letters}, find all possible valid English words with same letter count. 
Rules:
1. You can use each letter only as many times as it appears in {letters}.
2. Return the words as a valid Python list, e.g., ["word1", "word2", "word3"].
3. Do NOT add explanations or extra text, just return the list.
"""
    # Query Gemini
    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(prompt)

    # Log raw response for debugging
    response_text = response.text.strip()
    print("Raw Response:", response_text)

    words = []
    try:
        # Extract the first valid Python list using regex
        match = re.search(r"\[\s*\".*?\"\s*\]", response_text, re.DOTALL)
        if match:
            clean_text = match.group(0)  # Extract the list from the response
            words = ast.literal_eval(clean_text)  # Safely parse the list
        else:
            words = ["Error: No valid list found in response"]
    except Exception as e:
        words = [f"Error in response parsing: {str(e)}"]

    print("Parsed Words:", words)  # Debugging output
    
    return render_template('load.html')

if __name__ == '__main__':
    app.run(debug=True)
