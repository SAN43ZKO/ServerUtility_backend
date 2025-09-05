from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import io
import paramiko
import os
import re
import a2s

load_dotenv()

app=Flask(__name__)
app.debug = True
CORS(app)

SSH_HOST = os.getenv('HOST_IP', "linfed.ru")
SSH_USER = 'cs'
SSH_PRIVATE_KEY = os.getenv("SSH_KEY")
if SSH_PRIVATE_KEY is not None:
    key = SSH_PRIVATE_KEY.encode().decode("unicode_escape")
    with open("ssh_key", "w") as file:
        file.write(key)
else:
    print("No ssh_key")



@app.route('/api/server-start', methods=['POST'])
def start_server():
    try:
        data = request.get_json()

        if not data or "id" not in data:
            return jsonify({"error": "No id"}), 400

        server_id = data["id"]

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SSH_HOST, username=SSH_USER, key_filename="ssh_key")

        stdin, stdout, stderr = ssh.exec_command(f'cs2-server @prac{server_id} start')
        output = stdout.read().decode()
        error = stderr.read().decode()

        ssh.close()
        app.logger.info(output)
        app.logger.warning(error)
        return jsonify({"output": output, "error": error})
    except Exception as e:
        app.logger.error(e)
        return jsonify({"error": str(e)}), 500

@app.route('/api/server-stop', methods=['POST'])
def stop_server():
    try:
        data = request.get_json()

        if not data or "id" not in data:
            return jsonify({"error": "No id"}), 400

        server_id = data["id"]

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SSH_HOST, username=SSH_USER, key_filename="ssh_key")

        stdin, stdout, stderr = ssh.exec_command(f"cs2-server @prac{server_id} stop")
        output = stdout.read().decode()
        error = stderr.read().decode()

        clean_output = re.sub(r'\x1b\[[0-9;]*m', '', output)
        clean_output = re.sub(r'\*+\s*|\n\s*', ' ', clean_output).strip()

        ssh.close()
        app.logger.info(output)
        app.logger.warning(error)
        return jsonify({"output": clean_output, "error": error})
    except Exception as e:
        app.logger.error(e)
        return jsonify({"error": str(e)}), 500

@app.route('/api/say', methods=['POST'])
def say_mod():
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SSH_HOST, username=SSH_USER, key_filename="ssh_key")

        stdin, stdout, stderr = ssh.exec_command('cs2-server @prac3 exec say WORK!!!')
        output = stdout.read().decode()
        error = stderr.read().decode()

        ssh.close()
        return jsonify({"output": output, "error": error})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/status', methods=['POST'])
async def check_status():
    try:
        data = request.get_json()
        app.logger.info(f"Received data: {data}")

        if not data or "serverIp" not in data or "serverPort" not in data:
            app.logger.warning("Missing serverIp or serverPort in request")
            return jsonify({"error": "No server ip or port"}), 400

        server_ip = data['serverIp']
        server_port = data['serverPort']
        server_addres = (server_ip, server_port)

        info = await a2s.ainfo(server_addres)
        return jsonify({
            "status": "online",
            "players": str(info.player_count),
            "map": info.map_name,
            "port": info.port
        })

    except Exception as e:
        return jsonify({
            "status": "offline",
            "error": str(e)
        }), 200

if __name__ == "__main__":
    app.run(host="localhost", port=5000)
