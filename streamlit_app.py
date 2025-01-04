import streamlit as st
import subprocess
from ansi2html import Ansi2HTMLConverter
import requests

# Store your secrets in Streamlit's secrets management
BOT_TOKEN = st.secrets["BOT_TOKEN"]
CHAT_ID = st.secrets["CHAT_ID"]

conv = Ansi2HTMLConverter(inline=True)

def send_telegram_message(message):
    """Sends a message to the Telegram bot."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, data=data)
    except Exception as e:
        st.error(f"Failed to send Telegram message: {e}")

st.title("Remote Command Executor")

# Improved Text Input with Command History
if "command_history" not in st.session_state:
    st.session_state.command_history = []

command = st.text_input("Enter command", placeholder="e.g., ls -l /tmp", key="command_input")

if st.button("Execute"):
    if command:
        try:
            command = command.replace("_", " ")

            # Add command to history
            st.session_state.command_history.insert(0, command)  # Add to the beginning

            send_telegram_message(f"<b>Executing command:</b>\n<code>{command}</code>")

            process = subprocess.Popen(
                command,
                shell=True, # Be VERY careful with this!
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate()

            send_telegram_message(f"<b>Output:</b>\n<pre>{stdout}</pre>")
            if stderr:
                send_telegram_message(f"<b>Error:</b>\n<pre>{stderr}</pre>")

            html_output = conv.convert(stdout, full=False)
            st.markdown(html_output, unsafe_allow_html=True) # CAREFUL!

            if stderr:
                st.error(stderr)

        except Exception as e:
            send_telegram_message(f"<b>Error:</b> {e}")
            st.error(f"Error: {e}")
    else:
        st.warning("Please enter a command")


# Display Command History (optional)
st.subheader("Command History")
for cmd in st.session_state.command_history:
    st.code(cmd) # Display history as code
