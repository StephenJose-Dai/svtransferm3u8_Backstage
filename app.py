import os
import random
import string
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash, send_from_directory, abort
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import ipaddress
import subprocess
import time
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.urandom(24)
UPLOAD_FOLDER = '/www/qiepian/uploads'
OUTPUT_FOLDER = '/www/qiepian/output'
BASE_URL = 'http://101.42.27.60:9630'

db_config = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '670677773@qq.com*',
    'database': 'm3u8info',
    'port': '6999'
}

# 随机生成字符串用于文件名
def random_string(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# 启动时检查数据库连接
def check_db_connection_on_start():
    try:
        conn = mysql.connector.connect(**db_config)
        if conn.is_connected():
            conn.close()
            print("数据库连接成功，程序启动中...")
            return True
    except Error as e:
        print(f"数据库连接失败，错误详情: {e}")
        sys.exit(1)

# 保存信息到数据库
def save_to_db(client_ip, ip_type, upload_path, filename, user_agent, output_path, m3u8_url):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        query = """INSERT INTO m3u8infos (client_ip, ip_type, upload_time, upload_path, file_name, browser_ua, converted_path, m3u8_url, deleted, active)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        data = (client_ip, ip_type, datetime.now(), upload_path, filename, user_agent, output_path, m3u8_url, 0, 1)
        cursor.execute(query, data)
        conn.commit()
        cursor.close()
        conn.close()
    except Error as e:
        print(f"数据库写入失败，错误详情: {e}")
        raise Exception("数据库插入失败")

# 上传文件处理
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'files' not in request.files:
        return jsonify({'error': '没有文件上传'}), 400

    files = request.files.getlist('files')
    if not files:
        return jsonify({'error': '文件列表为空'}), 400

    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    ip_type = 'IPv6' if ipaddress.ip_address(client_ip).version == 6 else 'IPv4'
    user_agent = request.headers.get('User-Agent')

    results = []
    for file in files:
        if file and file.filename:
            filename = file.filename
            timestamp_formatted = datetime.now().strftime('%Y%m%d_%H%M%S')
            unix_timestamp = str(int(time.time()))
            filename_with_timestamps = f"{os.path.splitext(filename)[0]}_{timestamp_formatted}_{unix_timestamp}{os.path.splitext(filename)[1]}"
            file_path = os.path.join(UPLOAD_FOLDER, filename_with_timestamps)
            file.save(file_path)

            output_name = random_string()
            output_path = os.path.join(OUTPUT_FOLDER, output_name)
            os.makedirs(output_path, exist_ok=True)

            if file.filename.endswith(('.mp4', '.mp3', '.wav', '.avi', '.mov', '.ogg', '.flac')):
                if file.filename.endswith(('.mp4', '.avi', '.mov', '.flv')):
                    ffmpeg_cmd = f"ffmpeg -i '{file_path}' -codec: copy -start_number 0 -hls_time 5 -hls_list_size 0 -f hls '{output_path}/{output_name}.m3u8'"
                elif file.filename.endswith(('.mp3', '.wav', '.ogg', '.flac')):
                    ffmpeg_cmd = f"ffmpeg -i '{file_path}' -c:a aac -b:a 128k -f hls -hls_time 1 -hls_list_size 0 -hls_segment_filename '{output_path}/{output_name}_%03d.ts' '{output_path}/{output_name}.m3u8'"
                else:
                    continue
                
                try:
                    subprocess.run(ffmpeg_cmd, shell=True, check=True)
                except subprocess.CalledProcessError as e:
                    print(f"FFmpeg 处理错误: {e}")
                    continue

                m3u8_url = f"{BASE_URL}/output/{output_name}/{output_name}.m3u8"
                results.append({'filename': filename_with_timestamps, 'url': m3u8_url})

                try:
                    save_to_db(client_ip, ip_type, file_path, filename_with_timestamps, user_agent, output_path, m3u8_url)
                except Exception as db_err:
                    return jsonify({'error': str(db_err)}), 500
            else:
                return jsonify({'error': f'不支持的文件格式: {file.filename}'}), 400

    return jsonify(results)

# 播放m3u8文件
@app.route('/output/<folder>/<filename>', methods=['GET'])
def stream_m3u8(folder, filename):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        query = "SELECT deleted, active FROM m3u8infos WHERE converted_path = %s"
        cursor.execute(query, (os.path.join(OUTPUT_FOLDER, folder),))
        record = cursor.fetchone()
        cursor.close()
        conn.close()

        # 检查文件状态
        if not record or record['deleted'] == 1 or record['active'] == 0:
            # 此文件已被标记为不可用
            abort(403, description="此文件已被删除")

        file_path = os.path.join(OUTPUT_FOLDER, folder, filename)
        return send_from_directory(directory=os.path.join(OUTPUT_FOLDER, folder), path=filename)

    except Error as e:
        print(f"数据库错误: {e}")
        abort(500)

# 用户登录
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
            result = cursor.fetchone()
            cursor.close()
            conn.close()

            if result and check_password_hash(result[0], password):
                session['username'] = username
                return redirect(url_for('dashboard'))
            else:
                flash('用户名或密码错误！')
        except Error as e:
            print(f"数据库错误: {e}")
            flash('登录失败，请重试。')

    return render_template('login.html')

# 仪表盘
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM m3u8infos WHERE deleted = 0")
        records = cursor.fetchall()
        cursor.close()
        conn.close()
    except Error as e:
        print(f"数据库错误: {e}")
        records = []

    return render_template('dashboard.html', records=records)

# 删除文件
@app.route('/delete/<int:file_id>', methods=['POST'])
def delete_file(file_id):
    if 'username' not in session:
        return jsonify({"error": "未授权的请求"}), 403

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        # 更新 deleted 和 active 字段
        cursor.execute("UPDATE m3u8infos SET deleted = 1, active = 0 WHERE id = %s", (file_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": "文件已标记为删除"})
    except Error as e:
        print(f"无法删除文件: {e}")
        return jsonify({"error": "无法删除文件"}), 500

# 注销
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    if check_db_connection_on_start():
        app.run(host='0.0.0.0', port=7788)
