from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import re
import ast

app = Flask(__name__)

# Set up Gemini API
genai.configure(api_key="AIzaSyBmeuxEnAhSCT1LQ68DBYwF0wAKgpGgVik")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/load')
def load():
    # This route can be used to load data or perform other actions
    return render_template('main.html')

@app.route('/receive_letters', methods=['POST'])
def receive_letters():
    data = request.json
    letters = data.get('letters', [])
    
    if not letters:
        return jsonify({"status": "error", "message": "No letters provided"})
    
    # Convert list of letters to a string for AI processing
    letter_str = ''.join(letters)
    print(letter_str)
    # Get possible words using the AI
    possible_words = get_possible_words(letter_str)
    
    return jsonify({
        "status": "success", 
        "message": f"Received {len(letters)} letters",
        "possible_words": possible_words
    })

@app.route('/process_word', methods=['POST'])
def process_word():
    data = request.json
    word = data.get('word', '')
    
    if not word:
        return jsonify({"status": "error", "message": "No word provided"})
    
    # Get possible words using the AI based on the letters in the word
    possible_words = get_possible_words(word)
    
    return jsonify({
        "status": "success", 
        "message": f"Processed word: {word}",
        "possible_words": possible_words
    })

def get_possible_words(letter_str):
    # Remove any non-letter characters
    clean_letters = ''.join(filter(str.isalpha, letter_str)).lower()
    
    # Strict prompt to force exact list format
    prompt = f"""
You are a word solver. Using only the given letters: {list(clean_letters)}, find all possible valid English words.
Rules:
1. You can use each letter only as many times as it appears in the list.
2. Return ONLY 5-10 of the most interesting words (not obvious ones).
3. Return the words as a valid Python list, e.g., ["word1", "word2", "word3"].
4. Do NOT add explanations or extra text, just return the list.
5. Prefer words that are 3-6 letters long.
"""
    
    try:
        # Query Gemini
        model = genai.GenerativeModel("gemini-1.5-pro")
        response = model.generate_content(prompt)
        
        # Log raw response for debugging
        response_text = response.text.strip()
        print("Raw Response:", response_text)
        
        words = []
        # Extract the first valid Python list using regex
        match = re.search(r"\[\s*\".*?\"\s*(?:,\s*\".*?\"\s*)*\]", response_text, re.DOTALL)
        if match:
            try:
                clean_text = match.group(0)  # Extract the list from the response
                words = ast.literal_eval(clean_text)  # Safely parse the list
            except:
                # If literal_eval fails, try another approach
                matches = re.findall(r'"([^"]+)"', clean_text)
                if matches:
                    words = matches
        else:
            # Try another pattern in case AI formatted it differently
            matches = re.findall(r'"([^"]+)"', response_text)
            if matches:
                words = matches[:10]  # Limit to 10 words
        
        # Fallback in case no words were found
        if not words:
            words = ["Try another word!"]
            
        return words[:10]  # Return maximum 10 words
        
    except Exception as e:
        print(f"Error generating words: {e}")
        return ["Error", "Try again"]
if __name__ == '__main__':
    # Import the send_from_directory function here to avoid circular imports
    from flask import send_from_directory
    # Run the app in debug mode for development
    app.run(debug=True, host='0.0.0.0')