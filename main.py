import asyncio
import subprocess
import os
from dotenv import load_dotenv
from pyrogram import Client, filters
from pyrogram.types import Message

# Cargar variables de entorno
load_dotenv()

# Configuración
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Crear el cliente
app = Client(
    "mi_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Función para obtener el ping
async def get_ping():
    try:
        # Ejecutar comando ping (Linux/Windows compatible)
        ping_process = subprocess.Popen(
            ["ping", "-c", "4", "8.8.8.8"],  # Para Windows usa ["ping", "-n", "4", "8.8.8.8"]
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = ping_process.communicate()
        
        if stderr:
            return f"Error: {stderr}"
        
        # Extraer información relevante del ping
        lines = stdout.split('\n')
        stats_line = [line for line in lines if "min/avg/max" in line]
        if stats_line:
            return stats_line[0]
        return "No se pudo obtener información del ping"
    except Exception as e:
        return f"Error al ejecutar ping: {str(e)}"

# Tarea en segundo plano para enviar ping cada minuto
async def ping_task():
    while True:
        ping_result = await get_ping()
        await app.send_message(CHAT_ID, f"📊 **Ping del servidor:**\n`{ping_result}`")
        await asyncio.sleep(60)  # Esperar 60 segundos

# Manejador para el comando /start
@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    await message.reply_text("¡Hola! Soy un bot simple. Escribe /help para ver lo que puedo hacer.")

# Manejador para el comando /help
@app.on_message(filters.command("help"))
async def help_command(client: Client, message: Message):
    help_text = """
**Comandos disponibles:**
/start - Inicia el bot
/help - Muestra este mensaje de ayuda
/echo [texto] - Repite el texto que le envíes
/ping - Obtener el ping actual del servidor
"""
    await message.reply_text(help_text)

# Manejador para el comando /echo
@app.on_message(filters.command("echo"))
async def echo_command(client: Client, message: Message):
    if len(message.command) > 1:
        text = " ".join(message.command[1:])
        await message.reply_text(f"Has dicho: {text}")
    else:
        await message.reply_text("Por favor, escribe algo después de /echo")

# Manejador para el comando /ping
@app.on_message(filters.command("ping"))
async def manual_ping(client: Client, message: Message):
    ping_result = await get_ping()
    await message.reply_text(f"📊 **Ping actual:**\n`{ping_result}`")

# Manejador para mensajes que no son comandos
@app.on_message(filters.text & ~filters.command)
async def echo_text(client: Client, message: Message):
    # Primero verificamos si el mensaje no es un comando
    if not message.text.startswith('/'):
        await message.reply_text(f"Recibí tu mensaje: {message.text}")

# Función para iniciar el bot y la tarea de ping
async def main():
    await app.start()
    print("Bot iniciado...")
    # Iniciar la tarea de ping en segundo plano
    asyncio.create_task(ping_task())
    await asyncio.Event().wait()  # Ejecutar indefinidamente

# Ejecutar el bot
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot detenido")