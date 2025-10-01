import socket
import threading
import os
from datetime import datetime
from email.utils import formatdate
from urllib.parse import unquote

# Definindo o host e a porta do servidor
HOST = "0.0.0.0"  # Aceita conexões de qualquer IP
PORT = 8080        # Porta 8080 para o servidor HTTP

# Caminho para os arquivos do servidor
WWW_ROOT = os.path.join(os.path.dirname(__file__), "www")  # Diretório para os arquivos HTML servidos
ALLOWED_METHODS = {"GET", "POST"}  # Métodos HTTP suportados (GET e POST)

# Função para retornar data no formato RFC 7231
def http_date():
    return formatdate(timeval=None, localtime=False, usegmt=True)

# Função para construir a resposta HTTP
def build_response(status_code, reason, body=b"", content_type="text/plain; charset=utf-8", extra_headers=None):
    headers = {
        "Date": http_date(),
        "Server": "MiniPy/0.1",  # Identificação do servidor
        "Content-Length": str(len(body)),  # Tamanho do corpo da resposta
        "Content-Type": content_type,  # Tipo do conteúdo (HTML, JSON, etc.)
        "Connection": "close",  # Fechar a conexão após a resposta
    }
    if extra_headers:
        headers.update(extra_headers)  # Adiciona cabeçalhos extras se fornecidos
    status_line = f"HTTP/1.1 {status_code} {reason}\r\n"
    header_block = "".join(f"{k}: {v}\r\n" for k, v in headers.items())
    return (status_line + header_block + "\r\n").encode("utf-8") + body  # Retorna a resposta em bytes

# Função para processar a requisição recebida
def parse_request(conn):
    conn.settimeout(5)  # Define um tempo limite de 5 segundos
    data = b""
    while b"\r\n\r\n" not in data:
        chunk = conn.recv(4096)  # Recebe a requisição em partes
        if not chunk:
            break
        data += chunk
        if len(data) > 65536:  # Limita os cabeçalhos a 64KB
            raise ValueError("Headers too large")

    head, _, rest = data.partition(b"\r\n\r\n")  # Divide cabeçalho e corpo
    if not head:
        raise ValueError("Empty request")

    head_txt = head.decode("iso-8859-1")  # Decodifica cabeçalhos no padrão ISO-8859-1
    lines = head_txt.split("\r\n")
    request_line = lines[0]
    parts = request_line.split(" ")
    if len(parts) != 3:
        raise ValueError("Malformed request line")
    method, target, version = parts
    if version != "HTTP/1.1":
        raise ValueError("Only HTTP/1.1 supported")  # Verifica se a versão é HTTP/1.1

    headers = {}
    for line in lines[1:]:
        if not line:
            continue
        if ":" not in line:
            raise ValueError("Malformed header")
        k, v = line.split(":", 1)
        headers[k.strip().title()] = v.strip()

    if "Host" not in headers:  # Verifica a presença do cabeçalho 'Host' (necessário em HTTP/1.1)
        raise ValueError("Missing Host header")

    body = b""  # Inicializa o corpo da requisição
    content_length = int(headers.get("Content-Length", "0") or "0")
    if content_length > 0:
        body = rest
        to_read = content_length - len(body)
        while to_read > 0:
            chunk = conn.recv(min(4096, to_read))
            if not chunk:
                break
            body += chunk
            to_read -= len(chunk)
        if len(body) != content_length:
            raise ValueError("Body shorter than Content-Length")
    return method, target, version, headers, body

# Função para tratar o caminho do arquivo, evitando vulnerabilidades
def safe_path(url_path):
    path = unquote(url_path.split("?", 1)[0])
    path = path.split("#", 1)[0]
    if path == "/":
        path = "/index.html"  # Se o caminho for '/', serve o arquivo index.html
    path = os.path.normpath(path.lstrip("/"))  # Normaliza o caminho
    full = os.path.join(WWW_ROOT, path)
    if not full.startswith(os.path.abspath(WWW_ROOT)):  # Impede acesso a arquivos fora do diretório 'www'
        return None
    return full

# Função para tratar requisições GET
def handle_get(target):
    file_path = safe_path(target)
    if not file_path or not os.path.exists(file_path) or not os.path.isfile(file_path):
        return build_response(404, "Not Found", b"Not Found\n")

    # Determina o tipo de conteúdo do arquivo
    if file_path.endswith(".html"):
        ctype = "text/html; charset=utf-8"
    elif file_path.endswith(".txt"):
        ctype = "text/plain; charset=utf-8"
    elif file_path.endswith(".json"):
        ctype = "application/json; charset=utf-8"
    else:
        ctype = "application/octet-stream"

    with open(file_path, "rb") as f:
        body = f.read()
    return build_response(200, "OK", body, ctype)

# Função para tratar requisições POST
def handle_post(target, headers, body):
    if target.startswith("/echo"):
        ctype = headers.get("Content-Type", "application/octet-stream")
        return build_response(200, "OK", body, ctype)
    if target.startswith("/form"):
        resp = f"Recebido {len(body)} bytes.\nContent-Type: {headers.get('Content-Type','-')}\nBody: {body.decode('utf-8', errors='replace')}\n"
        return build_response(200, "OK", resp.encode("utf-8"), "text/plain; charset=utf-8")

    return build_response(404, "Not Found", b"Not Found\n")

# Função para lidar com cada conexão cliente em uma thread separada
def client_thread(conn, addr):
    try:
        method, target, version, headers, body = parse_request(conn)

        if method not in ALLOWED_METHODS:
            return conn.sendall(
                build_response(405, "Method Not Allowed", b"Method Not Allowed\n", extra_headers={"Allow": ", ".join(sorted(ALLOWED_METHODS))})
            )

        if method == "GET":
            resp = handle_get(target)
        elif method == "POST":
            if body and "Content-Length" not in headers:
                resp = build_response(400, "Bad Request", b"Missing Content-Length\n")
            else:
                resp = handle_post(target, headers, body)

        conn.sendall(resp)
    except ValueError as e:
        msg = f"Bad Request: {str(e)}\n".encode("utf-8", errors="replace")
        conn.sendall(build_response(400, "Bad Request", msg))
    except Exception as e:
        err = f"Internal Server Error\n".encode("utf-8")
        conn.sendall(build_response(500, "Internal Server Error", err))
    finally:
        conn.close()

# Função principal do servidor, que inicializa a escuta e lida com novas conexões
def main():
    os.makedirs(WWW_ROOT, exist_ok=True)
    index_html = os.path.join(WWW_ROOT, "index.html")
    if not os.path.exists(index_html):
        with open(index_html, "w", encoding="utf-8") as f:
            f.write("<!doctype html><meta charset='utf-8'><h1>Servidor MiniPy</h1><p>OK!</p>")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(50)
        print(f"[*] Servidor ouvindo em http://{HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            t = threading.Thread(target=client_thread, args=(conn, addr), daemon=True)
            t.start()

if __name__ == "__main__":
    main()
