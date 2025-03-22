import discord
from discord.ext import commands
import google.generativeai as genai
import pytesseract
from PIL import Image
import io

# Configurar intents
intents = discord.Intents.default()
intents.message_content = True  # Activar intent para leer mensajes
intents.members = True  # Permite que el bot lea los miembros
intents.message_content = True  # Permitir leer contenido del mensaje

# Crear el bot
bot = commands.Bot(command_prefix="/", intents=intents)

# Configurar Gemini
genai.configure(api_key="AIzaSyAuxhsSwWw2xu9SI1Q0yNkk6ub_fggQas0")  # Reemplaza con tu API key
modelo = genai.GenerativeModel("gemini-2.0-flash")  # O el modelo que uses

# Historial de mensajes para mantener contexto
historial = []
# Instrucción para evitar inventar cosas
instruccion = {
    "role": "system",
    "content": "Por favor, ten en cuenta que solo debes proporcionar información que esté confirmada o documentada en fuentes fiables. No te está permitido inventar hechos, especulaciones o responder con información no verificada. Si no tienes datos verificables sobre un tema o no puedes acceder a la información más reciente, deberías mencionar que no puedes proporcionar una respuesta precisa en lugar de hacer suposiciones."
}

@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")

@bot.command()
async def talk(ctx, *, mensaje: str):
    """Comando para hablar con el bot usando Gemini."""
    global historial
    
    # Agregar mensaje del usuario al historial
    historial.append({"role": "user", "parts": [{"text": mensaje}]})

    # Limitar historial a los últimos 10 mensajes
    if len(historial) > 10:
        historial.pop(0)

    try:
        # Generar respuesta con Gemini
        respuesta = modelo.generate_content(historial)

        # Agregar respuesta al historial
        historial.append({"role": "model", "parts": [{"text": respuesta.text}]})

        # Enviar respuesta a Discord (máximo 2000 caracteres por mensaje)
        for i in range(0, len(respuesta.text), 2000):
            await ctx.send(respuesta.text[i:i+2000])

    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if message.attachments:
        # Comprobamos si hay archivos adjuntos
        for attachment in message.attachments:
            # Descargar la imagen
            image_bytes = await attachment.read()

            # Convertir los bytes de la imagen a una imagen PIL
            image = Image.open(io.BytesIO(image_bytes))

            # Usar OCR para leer el texto
            texto_extraido = pytesseract.image_to_string(image)

            # Enviar el texto extraído
            await message.channel.send(f"Texto extraído de la imagen: {texto_extraido}")
    
    # Procesar comandos después de manejar los mensajes
    await bot.process_commands(message)

# Ejecutar el bot
bot.run("MTM1Mjk3MTc3ODI4MDAwMTU5OA.GIlDW5.F-zirkOeziGm27y41XWlUZBkcJ1BadWXmAF0ps")  # Reemplaza con tu token de Discord