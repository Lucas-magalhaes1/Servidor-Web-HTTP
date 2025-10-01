import java.io.*;
import java.net.*;
import java.nio.charset.StandardCharsets;

public class HttpClientSimple {

    private static void send(String method, URL url, String body, String contentType) throws IOException {
        String host = url.getHost();
        int port = (url.getPort() == -1) ? (url.getProtocol().equals("https") ? 443 : 80) : url.getPort();
        if (!url.getProtocol().equals("http")) {
            throw new IOException("Somente http:// neste cliente simples");
        }

        try (Socket sock = new Socket(host, port)) {
            sock.setSoTimeout(5000);
            OutputStream out = sock.getOutputStream();
            InputStream in = sock.getInputStream();

            String path = url.getFile().isEmpty() ? "/" : url.getFile();
            byte[] bodyBytes = (body == null) ? new byte[0] : body.getBytes(StandardCharsets.UTF_8);
            boolean hasBody = method.equals("POST") && bodyBytes.length > 0;

            // Montando a requisição HTTP manualmente
            StringBuilder req = new StringBuilder();
            req.append(method).append(" ").append(path).append(" HTTP/1.1\r\n");
            req.append("Host: ").append(host).append(":").append(port).append("\r\n");
            req.append("User-Agent: JavaClientSimple/0.1\r\n");
            req.append("Accept: */*\r\n");
            req.append("Connection: close\r\n");
            if (hasBody) {
                req.append("Content-Type: ").append(contentType == null ? "text/plain; charset=utf-8" : contentType).append("\r\n");
                req.append("Content-Length: ").append(bodyBytes.length).append("\r\n");
            }
            req.append("\r\n");

            out.write(req.toString().getBytes(StandardCharsets.UTF_8));
            if (hasBody) out.write(bodyBytes);
            out.flush();

            // Lendo a resposta e imprimindo no console
            BufferedReader reader = new BufferedReader(new InputStreamReader(in, StandardCharsets.ISO_8859_1));
            String line;
            while ((line = reader.readLine()) != null) {
                System.out.println(line);
            }
        }
    }

    private static void usage() {
        System.out.println("Uso:");
        System.out.println("  GET:  java HttpClientSimple GET http://localhost:8080/");
        System.out.println("  POST: java HttpClientSimple POST http://localhost:8080/echo \"mensagem\" \"text/plain; charset=utf-8\"");
    }

    public static void main(String[] args) {
        if (args.length < 2) { usage(); return; }
        String method = args[0].toUpperCase();
        try {
            URL url = new URL(args[1]);
            String body = (args.length >= 3) ? args[2] : null;
            String ctype = (args.length >= 4) ? args[3] : null;
            send(method, url, body, ctype);
        } catch (Exception e) {
            System.err.println("Erro: " + e.getMessage());
        }
    }
}
