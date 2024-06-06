import tkinter as tk
from tkinter import filedialog, messagebox
import os
from Script import cargar_todo_en_premiere

def seleccionar_archivos():
    try:
        # Abrir un cuadro de diálogo para que el usuario seleccione el archivo de video
        archivo_video = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4")])
        # Si el usuario cancela la selección, video_ruta será una cadena vacía
        if not archivo_video:
            raise ValueError("No se ha seleccionado ningún archivo de video.")
        # busca el archivo de video _pre
        archivo_video_pre = archivo_video.replace(".mp4", "_pre.mp4")
        if not os.path.exists(archivo_video_pre):
            raise ValueError("No se ha encontrado el archivo de video preprocesado.")
        
        # Obtener la carpeta que contiene el archivo de video seleccionado
        carpeta = os.path.dirname(archivo_video)
        # obtener el nombre_base
        nombre_base = os.path.splitext(os.path.basename(archivo_video))[0]
        print(nombre_base)
        # Encontrar el archivo de audio en la misma carpeta que el archivo de video
        archivo_audio = next((os.path.join(carpeta, f) for f in os.listdir(carpeta) if f.endswith((".mp3", ".wav"))), None)
        if not archivo_audio:
            raise ValueError("No se ha encontrado ningún archivo de audio en la carpeta.")
        
        # Encontrar los archivos de imágenes en la misma carpeta que el archivo de video
        # por nombre, tiene que empezar por "diapositiva" y terminar en ".png", ".jpg" o ".jpeg"

        archivos_imagenes = [os.path.join(carpeta, f) for f in os.listdir(carpeta) if f.endswith((".png", ".jpg", ".jpeg", ".PNG")) and f.startswith(nombre_base)]
        if not archivos_imagenes:
            raise ValueError("No se han encontrado archivos de imágenes en la carpeta.")
        
        # Encontrar el archivo de guía de diapositivas en la misma carpeta que el archivo de video
        archivo_guia_diapositivas = next((os.path.join(carpeta, f) for f in os.listdir(carpeta) if f.endswith((".txt"))), None)
        if not archivo_guia_diapositivas:
            raise ValueError("No se ha encontrado el archivo de guía de diapositivas en la carpeta.")
        
        # Encontrar el fondo
        archivo_fondo = next((os.path.join(carpeta, f) for f in os.listdir(carpeta) if f.endswith((".png", ".jpg", ".jpeg", ".PNG")) and f.startswith("fondo")), None)
        if not archivo_fondo:
            raise ValueError("No se ha encontrado el archivo de fondo en la carpeta.")
        # Llamar al script
        cargar_todo_en_premiere(archivo_video_pre, archivo_audio, archivos_imagenes, archivo_guia_diapositivas, archivo_fondo)
    
    except ValueError as e:
        # Mostrar el mensaje de error en una ventana emergente
        messagebox.showerror("Error", str(e))

# Crear una ventana de tkinter
root = tk.Tk()
root.title("Generación de proyecto Premier Pro a partir de ficheros obtenidos")

# Etiqueta para mostrar las instrucciones
instrucciones = tk.Label(root, text="Instrucciones:\n1. Inicia un nuevo proyecto vacío en Premiere.\n2. Descarga de drive todos los archivos generados después de la síntesis y colócalos en una carpeta.\n3. Haz clic en el botón 'Seleccionar archivo de video' y selecciona el video.", font=("Helvetica", 16))
instrucciones.pack(pady=10)

# Agregar un botón para que el usuario seleccione el archivo de video
boton = tk.Button(root, text="Seleccionar archivo de video", command=seleccionar_archivos)
boton.pack(pady=10)

# Ejecutar el bucle principal de tkinter
root.mainloop()
