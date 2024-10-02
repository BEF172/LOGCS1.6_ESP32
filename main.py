import network  # Importa el módulo para manejar la conexión de red
import socket  # Importa el módulo para crear y manejar sockets
import time  # Importa el módulo para manejar el tiempo
import _thread  # Importa el módulo para manejar hilos (threads)
import config  # Importa el archivo de configuración que contiene credenciales

# Importación de Config.py
ssid = config.ssid  # Obtiene el SSID de la red Wi-Fi desde el archivo de configuración
password = config.password  # Obtiene la contraseña de la red Wi-Fi desde el archivo de configuración
Usuario = config.Usuario  # Obtiene el nombre de usuario desde el archivo de configuración

# Conectar a la red Wi-Fi
wlan = network.WLAN(network.STA_IF)  # Crea una interfaz de red para conectarse como cliente (STA_IF)
wlan.active(True)  # Activa la interfaz de red
wlan.connect(ssid, password)  # Intenta conectarse a la red Wi-Fi usando el SSID y la contraseña

# Mientras no se conecte
while not wlan.isconnected():
    time.sleep(1)  # Pausa por 1 segundo si no está conectado
    print("Conectando a WiFi...")  # Imprime que se está conectando

# Sale del while porque ya se conectó
print("Conectado a WiFi")  # Avisa que se conectó correctamente
print("Dirección IP del ESP32:", wlan.ifconfig()[0])  # Muestra la dirección IP del ESP32

# Configuración del servidor UDP
udp_port = 8888  # Se define el número de puerto que se usará para el servidor UDP. En este caso, se usa el puerto 8888.

# Se crea un socket UDP.
# AF_INET indica que se usará IPv4 (la versión más común de la dirección IP),
# SOCK_DGRAM especifica que se utilizará el protocolo UDP, que es un protocolo de datagramas sin conexión.
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Se enlaza el socket UDP a una dirección y puerto específicos.
# "" significa que se aceptarán conexiones de cualquier dirección IP (todas las interfaces de red disponibles).
# udp_port es el número de puerto definido anteriormente (8888).
udp_socket.bind(("", udp_port))

print("Servidor UDP iniciado en puerto", udp_port)  # Imprime un mensaje indicando que el servidor UDP ha iniciado

# Servidor web - HTML más simple para pruebas
simple_html = """<!DOCTYPE html>
<html>
<head>
    <title>Logs de Counter-Strike</title>
    <style>
        body {{ font-family: Arial, sans-serif; background-color: #222; color: #fff; }}  # Estilo del cuerpo
        h1 {{ color: #4CAF50; }}  # Estilo del encabezado principal
        pre {{ background-color: #333; padding: 10px; border-radius: 5px; }}  # Estilo para el área de logs
    </style>
</head>
<body>
    <h1>Logs de Counter-Strike</h1>
    <h2 id="contador">Muertes: {muerte_count} | Asesinatos: {mate_count}</h2>  # Contadores de muertes y asesinatos
    <pre id="logs">Cargando...</pre>  # Área para mostrar los logs
    <script>
        setInterval(function() {{
            fetch('/logs')  # Solicita los logs cada segundo
                .then(response => response.text())  # Convierte la respuesta a texto
                .then(data => {{
                    const [contador, ...logs] = data.split('\\n');  # Divide los datos en contador y logs
                    document.getElementById('logs').innerText = logs.join('\\n');  # Actualiza el área de logs
                    document.getElementById('contador').innerText = contador;  # Actualiza el contador
                }});
        }}, 1000);  // Actualiza cada segundo
    </script>
</body>
</html>
"""

log_filtered = []  # Lista para almacenar todos los logs filtrados
web_socket = None  # Variable para el socket del servidor web
muerte_count = 0   # Inicializar contador de muertes
mate_count = 0     # Inicializar contador de asesinatos

def start_web_server():  # Función para iniciar el servidor web
    global log_filtered, web_socket, muerte_count, mate_count  # Declarar variables globales

    web_socket = socket.socket()  # Crear un nuevo socket para el servidor web

    try:  # Intenta enlazar el puerto
        web_socket.bind(("", 80))  # Cambia el puerto si es necesario
    except OSError as e:  # Si ocurre un error al enlazar
        print("No se pudo enlazar al puerto 80:", e)  # Imprime el error
        return  # Salir de la función si el puerto ya está en uso

    web_socket.listen(1)  # Escuchar conexiones entrantes

    while True:  # Mientras el servidor esté activo
        try:
            conn, addr = web_socket.accept()  # Acepta una conexión entrante
            request = conn.recv(1024).decode()  # Recibe la solicitud del cliente

            # Limitar la cantidad de logs enviados a los últimos 100
            if len(log_filtered) > 100:  # Si hay más de 100 logs
                log_filtered = log_filtered[-100:]  # Mantener solo los últimos 100 logs

            if "/logs" in request:  # Si la solicitud contiene "/logs"
                # Enviar tanto los logs como los contadores
                response = f"Muertes: {muerte_count} | Asesinatos: {mate_count}\n" + "\n".join(log_filtered)  # Crear la respuesta con contadores y logs
                conn.send("HTTP/1.0 200 OK\r\nContent-Type: text/plain\r\n\r\n".encode())  # Enviar encabezado HTTP
                conn.send(response.encode())  # Enviar la respuesta
            else:  # Si la solicitud no es para "/logs"
                # Usar el template para incluir los contadores
                html = simple_html.format(muerte_count=muerte_count, mate_count=mate_count)  # Formatear el HTML
                conn.send("HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n".encode())  # Enviar encabezado HTTP
                conn.send(html.encode())  # Enviar el HTML

            conn.close()  # Cerrar la conexión
        except Exception as e:  # Capturar cualquier excepción
            print("Error en el servidor web:", e)  # Imprimir el mensaje de error

# Iniciar el servidor web en un hilo separado
_thread.start_new_thread(start_web_server, ())  # Inicia el servidor web en un nuevo hilo

while True:  # Bucle principal para recibir paquetes UDP
    udp_socket.settimeout(1.0)  # Establecer el tiempo de espera para la recepción
    try:
        packet, address = udp_socket.recvfrom(255)  # Recibe un paquete UDP

        # Mostrar el paquete tal cual llega
        log_raw = str(packet)  # Convertir el paquete a formato string

        # Filtrar el log para eliminar todo hasta encontrar 'L'
        position = log_raw.find('L')  # Encontrar la posición de 'L'
        if position != -1:  # Si se encontró 'L'
            filtered_log = log_raw[position:]  # Obtener la subcadena a partir de 'L'

            # Verificar si el log filtrado contiene el nombre de usuario
            if Usuario in filtered_log:  # Si el log filtrado contiene el nombre de usuario
                # Eliminar desde '\' hacia adelante
                backslash_position = filtered_log.find('\\')  # Encontrar la posición de '\'
                if backslash_position != -1:  # Si se encontró '\'
                    filtered_log = filtered_log[:backslash_position]  # Mantener solo la parte antes de '\'

                log_filtered.append(filtered_log)  # Agregar el log filtrado a la lista

                # Contar muertes y asesinatos
                if "killed" in filtered_log:  # Si el log indica que alguien fue asesinado
                    if filtered_log.index("killed") < filtered_log.index(Usuario):  # Muerte de AGUANTE LOS PLANES
                        muerte_count += 1  # Incrementar contador de muertes
                    else:  # AGUANTE LOS PLANES asesina a alguien
                        mate_count += 1  # Incrementar contador de asesinatos
    except OSError:  # Excepción si no se recibe ningún paquete dentro del tiempo de espera
        pass  # Simplemente continuar si no hay paquetes
