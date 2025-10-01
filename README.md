# Guia de Execução — Servidor Python + Cliente Java

---

## 1. Verificar se o **Python** está instalado

### Linux

```bash
python3 --version
```

Se não estiver instalado:

```bash
sudo apt update
sudo apt install -y python3
```

### Windows

No **Prompt de Comando** ou **PowerShell**:

```powershell
python --version
```

Se não estiver instalado:

* Baixar em: [https://www.python.org/downloads/](https://www.python.org/downloads/)
* Durante a instalação, marcar **"Add Python to PATH"**.

---

## 2. Verificar se o **Java** está instalado

### Linux

```bash
java -version
javac -version
```

Se não estiver instalado:

```bash
sudo apt update
sudo apt install -y default-jdk
```

### Windows

No **Prompt de Comando**:

```powershell
java -version
javac -version
```

Se não estiver instalado:

* Baixar o JDK (Java Development Kit) em:

  * [https://adoptium.net/](https://adoptium.net/)
  * ou [https://www.oracle.com/java/technologies/javase-downloads.html](https://www.oracle.com/java/technologies/javase-downloads.html)

* Instalar e garantir que o **JAVA_HOME** está configurado e que o diretório **bin/** do JDK está no **PATH**.

---

## 3. Rodar o **servidor (Python)**

No terminal (**Linux**) ou no **Prompt/PowerShell (Windows)**, vá até a pasta onde está o arquivo `server.py`:

```bash
python server.py
```

ou (Linux):

```bash
python3 server.py
```

O servidor inicia em:

```
http://0.0.0.0:8080/
```

Ele cria automaticamente uma pasta **`www/`** com um **`index.html`**.

---

## 4. Rodar o **cliente (Java)**

Abra outro terminal/janela, vá até a pasta onde está o arquivo `HttpClientSimple.java` e compile:

```bash
javac HttpClientSimple.java
```

Depois execute:

### GET

```bash
java HttpClientSimple GET http://localhost:8080/
```

### POST

```bash
java HttpClientSimple POST http://localhost:8080/echo "olá prof" "text/plain; charset=utf-8"
```

---

## 5. Testes extras com **curl** (opcional)

### Linux (já vem com curl)

```bash
curl -v http://localhost:8080/
```

### Windows

No **PowerShell moderno** pode usar:

```powershell
curl.exe -v http://localhost:8080/
```

Se não tiver o `curl.exe`, pode baixar em: [https://curl.se/windows/](https://curl.se/windows/)

### Exemplos de testes:

* **GET default (serve index.html)**

```bash
curl -v http://localhost:8080/
```

* **GET arquivo inexistente → 404**

```bash
curl -v http://localhost:8080/nao-tem.txt
```

* **POST /echo com JSON → 200 OK**

```bash
curl -v -H "Content-Type: application/json" --data '{"msg":"oi"}' http://localhost:8080/echo
```

* **Método não permitido → 405**

```bash
curl -v -X PUT http://localhost:8080/
```

---

## 6. Testando em **duas máquinas diferentes**

### Máquina A (Servidor — você)

```bash
# Descobrir IP (Windows)
ipconfig

# Iniciar servidor
python server.py
```

### Máquina B (Cliente)

```bash
# Descobrir IP
i p a   # Linux
ipconfig # Windows

# Testar acesso ao servidor da máquina A
curl -v http://192.168.1.42:8080/

# Compilar cliente Java
javac HttpClientSimple.java

# Executar cliente apontando para máquina A
java HttpClientSimple GET http://192.168.1.42:8080/
```

---

##  Resumo

1. Instalar/verificar **Python** e **Java**.
2. Rodar servidor em **Python**.
3. Rodar cliente em **Java** (mesma máquina ou diferente).
4. Testar com **curl** ou navegador.
5. Para duas máquinas: usar o **IP da máquina do servidor** no cliente.
