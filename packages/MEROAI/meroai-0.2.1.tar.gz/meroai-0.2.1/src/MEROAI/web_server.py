import os
import sys
from flask import Flask, render_template_string, request, jsonify
from werkzeug.utils import secure_filename
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from commands.meroai_cli import (
    process_input, analyze_code, fix_code, detect_language,
    analyze_image, get_device_info, generate_script, generate_cpp_script,
    APP_NAME, __version__, __author__, __contact__
)
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = '/tmp/meroai_uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MEROAI - AI Programming Assistant</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #fff;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            text-align: center;
            padding: 30px 0;
            border-bottom: 1px solid #333;
        }
        .header h1 {
            font-size: 2.5em;
            color: #00d4ff;
            margin-bottom: 10px;
        }
        .header p {
            color: #888;
        }
        .chat-container {
            background: #1e1e2e;
            border-radius: 15px;
            margin: 20px 0;
            padding: 20px;
            min-height: 400px;
            max-height: 500px;
            overflow-y: auto;
        }
        .message {
            margin: 15px 0;
            padding: 15px;
            border-radius: 10px;
        }
        .user-message {
            background: #0066cc;
            margin-left: 50px;
        }
        .ai-message {
            background: #333;
            margin-right: 50px;
        }
        .input-area {
            display: flex;
            gap: 10px;
            margin: 20px 0;
        }
        .input-area input {
            flex: 1;
            padding: 15px;
            border: none;
            border-radius: 10px;
            background: #2a2a3e;
            color: #fff;
            font-size: 16px;
        }
        .input-area button {
            padding: 15px 30px;
            border: none;
            border-radius: 10px;
            background: #00d4ff;
            color: #000;
            font-weight: bold;
            cursor: pointer;
        }
        .input-area button:hover {
            background: #00a8cc;
        }
        .upload-area {
            background: #2a2a3e;
            border: 2px dashed #444;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            margin: 20px 0;
        }
        .upload-area input {
            display: none;
        }
        .upload-area label {
            cursor: pointer;
            color: #00d4ff;
        }
        .commands {
            background: #2a2a3e;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
        }
        .commands h3 {
            color: #00d4ff;
            margin-bottom: 15px;
        }
        .commands ul {
            list-style: none;
        }
        .commands li {
            padding: 5px 0;
            color: #aaa;
        }
        .footer {
            text-align: center;
            padding: 20px;
            color: #666;
        }
        .footer a {
            color: #00d4ff;
            text-decoration: none;
        }
        pre {
            background: #1a1a2e;
            padding: 15px;
            border-radius: 8px;
            overflow-x: auto;
            white-space: pre-wrap;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>MEROAI</h1>
            <p>AI Programming Assistant | Developed by MERO</p>
            <p>GitHub: <a href="https://github.com/6x-u" style="color:#00d4ff">@6x-u</a> | Telegram: <a href="https://t.me/QP4RM" style="color:#00d4ff">@QP4RM</a></p>
        </div>
        <div class="chat-container" id="chat">
            <div class="message ai-message">
                <strong>MEROAI:</strong> Welcome! I am MEROAI, an AI programming assistant developed by MERO. How can I help you?
            </div>
        </div>
        <div class="input-area">
            <input type="text" id="userInput" placeholder="Type your message..." onkeypress="if(event.key==='Enter')sendMessage()">
            <button onclick="sendMessage()">Send</button>
        </div>
        <div class="upload-area">
            <input type="file" id="fileUpload" onchange="uploadFile()">
            <label for="fileUpload">Upload file for analysis (Python, C++, Images...)</label>
        </div>
        <div class="commands">
            <h3>Available Commands:</h3>
            <ul>
                <li>who are you - About MEROAI</li>
                <li>create script - Generate Python script</li>
                <li>c++ script - Generate C++ script</li>
                <li>device - Show device info</li>
                <li>Upload any code file for analysis</li>
            </ul>
        </div>
        <div class="footer">
            <p>MEROAI v1.0.0 | Developer: MERO</p>
            <p><a href="https://github.com/6x-u">GitHub</a> | <a href="https://t.me/QP4RM">Telegram</a></p>
        </div>
    </div>
    <script>
        function addMessage(text, isUser) {
            const chat = document.getElementById('chat');
            const div = document.createElement('div');
            div.className = 'message ' + (isUser ? 'user-message' : 'ai-message');
            div.innerHTML = '<strong>' + (isUser ? 'You' : 'MEROAI') + ':</strong> ' + text.replace(/\\n/g, '<br>');
            chat.appendChild(div);
            chat.scrollTop = chat.scrollHeight;
        }
        async function sendMessage() {
            const input = document.getElementById('userInput');
            const text = input.value.trim();
            if (!text) return;
            addMessage(text, true);
            input.value = '';
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: text})
            });
            const data = await response.json();
            addMessage('<pre>' + data.response + '</pre>', false);
        }
        async function uploadFile() {
            const fileInput = document.getElementById('fileUpload');
            const file = fileInput.files[0];
            if (!file) return;
            addMessage('Uploading: ' + file.name, true);
            const formData = new FormData();
            formData.append('file', file);
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            addMessage('<pre>' + data.response + '</pre>', false);
            fileInput.value = '';
        }
    </script>
</body>
</html>
'''
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)
@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message', '')
    if 'device' in message.lower():
        info = get_device_info()
        response = "Device Information:\\n"
        for key, value in info.items():
            response += f"{key}: {value}\\n"
    else:
        response = process_input(message)
    return jsonify({'response': response})
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'response': 'No file uploaded'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'response': 'No file selected'})
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    ext = os.path.splitext(filename)[1].lower()
    if ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']:
        result = analyze_image(filepath)
        response = f"Image Analysis: {filename}\\n"
        for key, value in result.items():
            response += f"{key}: {value}\\n"
    else:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            language = detect_language(content)
            errors = analyze_code(content, language)
            response = f"File: {filename}\\nLanguage: {language}\\nErrors: {len(errors)}\\n"
            if errors:
                response += "\\nIssues found:\\n"
                for e in errors:
                    response += f"- {e}\\n"
            else:
                response += "\\nNo errors found. Code looks good!"
            response += f"\\n\\nCredits: {APP_NAME} - {__author__} ({__contact__})"
        except Exception as e:
            response = f"Error analyzing file: {str(e)}"
    os.remove(filepath)
    return jsonify({'response': response})
@app.route('/api/info')
def api_info():
    return jsonify(get_device_info())
@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    data = request.get_json()
    code = data.get('code', '')
    language = detect_language(code)
    errors = analyze_code(code, language)
    return jsonify({
        'language': language,
        'errors': errors,
        'credits': f'{APP_NAME} - {__author__} ({__contact__})'
    })
def run_server(host='0.0.0.0', port=5000):
    print(f"""
{'=' * 60}
MEROAI Web Server v{__version__}
{'=' * 60}
Server running at: http://{host}:{port}
Developer: {__author__}
GitHub: https://github.com/6x-u
Telegram: {__contact__}
{'=' * 60}
""")
    app.run(host=host, port=port, debug=False)
if __name__ == '__main__':
    run_server()
