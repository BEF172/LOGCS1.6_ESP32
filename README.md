# LOGCS1.6_ESP32

Hola, esto conecta el servidor UDP del juego "Counter-Strike 1.6" utilizando MicroPython (Firmware Python para ESP32). Para poder usarlo, es necesario activar los comandos `logaddress_add` y `log on` en el juego.

### Parte ESP32:
Necesitas tener VS Code con la extensión **Pymakr** para poder enviar los archivos al ESP32.

1. Abre VS Code
2. Descarga la extension **Pymakr** y **Node.js** para que funcione bien.
3. Descarga el ZIP desde esta página y descomprímelo.
4. Cambia SSID y PASSWORD por las credenciales de tu internet y el nombre del usuario en config.py.
5. Conecta el dispositivo con VS Code usando la extensión.
6. Abre la consola del ESP32 usando la extensión.

#### Comandos útiles de la extensión:
- **Ctrl + C** interrumpe al ESP32 apagándolo.
- **Ctrl + D** reinicia el ESP32. *(Cada vez que subes un archivo tienes que hacer este reinicio. Asegúrate de que el ESP32 esté apagado con **Ctrl + C** antes de enviar el archivo).*

5. Envía el archivo: en la parte donde está la carpeta del proyecto, en la parte inferior de VS Code aparece el ESP32 con una nube que dice "Sync project to device". Haz clic en la nube.
6. Una vez hecho esto, carga el proyecto y usa **Ctrl + D** para que se ejecute y muestre su IP y puerto, los cuales usarás en CS 1.6.

### Parte CS 1.6:
1. Entra a **CS 1.6**.
2. Abre la consola de comandos.
3. Ejecuta el comando `logaddress_add IP PUERTO`.

   **Nota**: La IP y el puerto deben ser del ESP32.

4. Activa el logging con el comando `log on`.

### FINAL:
Ahora solamente utiliza el navegador para ver si esta funcionando.  
deberias poder entrar usando su ip como si fuera un router.
