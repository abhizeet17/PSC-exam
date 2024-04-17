import socket
import mimetypes
import psycopg2
import json

conn = psycopg2.connect(
    database="dummy",
    user="postgres",
    password="newpassword",
    host="localhost"
)

cur = conn.cursor()

# Check if the student table exists
cur.execute("""
    SELECT EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_name = 'students'
    )
""")
student_table_exists = cur.fetchone()[0]

# Check if the teacher table exists
cur.execute("""
    SELECT EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_name = 'teachers'
    )
""")
teacher_table_exists = cur.fetchone()[0]

# If the student table doesn't exist, create it
if not student_table_exists:
    cur.execute("""
        CREATE TABLE students (
            username varchar PRIMARY KEY,
            password varchar
        )
    """)
    conn.commit()

# If the teacher table doesn't exist, create it
if not teacher_table_exists:
    cur.execute("""
        CREATE TABLE teachers (
            username varchar PRIMARY KEY,
            password varchar
        )
    """)
    conn.commit()


def run_server(host='127.0.0.1', port=1712):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen()
        print(f"Server is running on {host}:{port}")
        print("Press Ctrl+C to stop the server.")

        while True:
            client_socket, addr = server_socket.accept()
            print(f"Connected by {addr}")

            request = client_socket.recv(2048).decode('utf-8')
            print(f"Request received:\n{request}")

            response = handleRequest(request)
            client_socket.sendall(response)
            client_socket.close()


def serverFile(file_path):
    try:
        with open(file_path, 'rb') as file:
            return file.read()
    except:
        return f"HTTP/1.1 404 NOT FOUND\n\n file not found".encode()


def userInput(request):
    body = request.split('\r\n\r\n')[1]
    postData = body
    formData = {}
    for pair in postData.split('&'):
        key, value = pair.split('=')
        formData[key] = value
    return formData


def handleRequest(request):
    global conn

    parseRequest = request.split('\n')[0].split()
    method = parseRequest[0]
    uri = parseRequest[1]

    if '/favicon.ico' in request:
        return ''.encode()

    if method == 'GET':
        if uri == '/':
            response = f'HTTP/1.1 200 OK\r\nContent-Type:text/html\r\n\r\n'.encode() + serverFile('default.html')
        elif uri == '/studentlogin':
            response = f'HTTP/1.1 200 OK\r\nContent-Type:text/html\r\n\r\n'.encode() + serverFile('studentlogin.html')
        elif uri == '/studentregister':
            response = f'HTTP/1.1 200 OK\r\nContent-Type:text/html\r\n\r\n'.encode() + serverFile('studentregister.html')
        elif uri == '/teacherlogin':
            response = f'HTTP/1.1 200 OK\r\nContent-Type:text/html\r\n\r\n'.encode() + serverFile('teacherlogin.html')
        elif uri == '/teacherregister':
            response = f'HTTP/1.1 200 OK\r\nContent-Type:text/html\r\n\r\n'.encode() + serverFile('teacherregister.html')
        elif uri == '/studenthp':
            response = f'HTTP/1.1 200 OK\r\nContent-Type:text/html\r\n\r\n'.encode() + serverFile('studenthp.html')
        elif uri == '/teacherhp':
            response = f'HTTP/1.1 200 OK\r\nContent-Type:text/html\r\n\r\n'.encode() + serverFile('teacherhp.html')

        return response

    elif method == 'POST':
        if uri == '/studentregister':
            data = userInput(request)
            username = data.get('username').replace('+', ' ')
            password = data.get('password')
            cur.execute(f"INSERT INTO students VALUES ('{username}', '{password}')")
            conn.commit()

            response = f'HTTP/1.1 302 FOUND\r\nLocation: /studentlogin\r\n\r\n'.encode()

        elif uri == '/teacherregister':
            data = userInput(request)
            username = data.get('username').replace('+', ' ')
            password = data.get('password')
            cur.execute(f"INSERT INTO teachers VALUES ('{username}', '{password}')")
            conn.commit()

            response = f'HTTP/1.1 302 FOUND\r\nLocation: /teacherlogin\r\n\r\n'.encode()

        elif uri == '/studentlogin':
            data = userInput(request)
            username = data.get('username').replace('+', ' ')
            password = data.get('password')
            cur.execute(f"SELECT EXISTS (SELECT 1 FROM students WHERE username = '{username}' AND password = '{password}') AS password_exists;")
            password_exists = cur.fetchone()[0]

            if password_exists:
                response = f'HTTP/1.1 302 FOUND\r\nLocation: /studenthp\r\n\r\n'.encode()
            else:
                response = f'HTTP/1.1 302 FOUND\r\nLocation: /studentlogin\r\n\r\n'.encode()

        elif uri == '/teacherlogin':
            data = userInput(request)
            username = data.get('username').replace('+', ' ')
            password = data.get('password')
            cur.execute(f"SELECT EXISTS (SELECT 1 FROM teachers WHERE username = '{username}' AND password = '{password}') AS password_exists;")
            password_exists = cur.fetchone()[0]

            if password_exists:
                response = f'HTTP/1.1 302 FOUND\r\nLocation: /teacherhp\r\n\r\n'.encode()
            else:
                response = f'HTTP/1.1 302 FOUND\r\nLocation: /teacherlogin\r\n\r\n'.encode()

        return response


if __name__ == '__main__':
    run_server()
