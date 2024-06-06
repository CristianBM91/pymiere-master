import pymiere
from pymiere.wrappers import get_system_sequence_presets
from pymiere import wrappers
from pymiere.wrappers import time_from_seconds
import tkinter as tk
from tkinter import messagebox
import re

def cargar_todo_en_premiere(archivo_video, archivo_audio, archivos_imagenes, archivo_guia_diapositivas, archivo_fondo):
    try:
        colocar_medios_en_la_secuencia(archivo_video, archivo_audio, archivos_imagenes, archivo_fondo)
        guia_diapositivas, guia_speaker = leer_guia_diapositivas(archivo_guia_diapositivas)
        ajustar_tiempo_aparicion_persona(guia_speaker)
        ajustar_diapositivas(guia_diapositivas)
        ajustar_persona(recorte_izquierda=25, recorte_derecha=25, recorte_arriba=0, recorte_abajo=0)
        alargar_fondo()

    except Exception as e:
        # Mostrar el mensaje de error en una ventana emergente
        messagebox.showerror("Error", str(e))

def tiempo_a_segundos(tiempo):
    partes_tiempo = tiempo.split(':')
    horas = int(partes_tiempo[0])
    minutos = int(partes_tiempo[1])
    segundos = int(partes_tiempo[2].split('.')[0])
    milisegundos = int(partes_tiempo[2].split('.')[1])
    tiempo_total_segundos = horas * 3600 + minutos * 60 + segundos + milisegundos / 1000
    return tiempo_total_segundos

def ordenar_por_numero(s):
    # Función auxiliar para ordenar las imágenes numéricamente
    return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', s)]

def colocar_medios_en_la_secuencia(archivo_video, archivo_audio, archivos_imagenes, archivo_fondo):
    # Verificar si hay un proyecto abierto
    project_opened, sequence_active = wrappers.check_active_sequence(crash=False)
    if not project_opened:
        raise ValueError("Por favor, abre un proyecto en Premiere.")

    # Crear una nueva secuencia y abrirla en el proyecto
    sequence_preset_path = get_system_sequence_presets(category="", resolution=None, preset_name="a")
    sequence_name = "My new sequence"
    pymiere.objects.qe.project.newSequence(sequence_name, sequence_preset_path)
    
    # Verificar si la nueva secuencia se creó correctamente
    sequences = pymiere.objects.app.project.sequences
    if not sequences:
        raise ValueError("No se pudo crear la nueva secuencia.")
    
    sequence = [s for s in sequences if s.name == sequence_name][0]
    pymiere.objects.app.project.openSequence(sequenceID=sequence.sequenceID)
    
    # Añadir archivos a la secuencia
    project = pymiere.objects.app.project
    archivo_video = archivo_video.replace("/", "\\")
    archivo_audio = archivo_audio.replace("/", "\\")
    archivos_imagenes = [archivo.replace("/", "\\") for archivo in archivos_imagenes]
    archivo_fondo = archivo_fondo.replace("/", "\\")

    success = project.importFiles(
        [archivo_video, archivo_audio, archivo_fondo] + archivos_imagenes,
        suppressUI=True,
        targetBin=project.getInsertionBin(),
        importAsNumberedStills=False
    )
    if not success:
        raise ValueError("Error al importar archivos en Premiere.")
    
    video_item = project.rootItem.findItemsMatchingMediaPath(archivo_video, ignoreSubclips=False)[0]
    audio_item = project.rootItem.findItemsMatchingMediaPath(archivo_audio, ignoreSubclips=False)[0]
    fondo_item = project.rootItem.findItemsMatchingMediaPath(archivo_fondo, ignoreSubclips=False)[0]
    
    transparencias_items_lista = []
    for imagen_path in archivos_imagenes:
        imagen_item = project.rootItem.findItemsMatchingMediaPath(imagen_path, ignoreSubclips=False)[0]
        transparencias_items_lista.append(imagen_item)
    
    # Ordenar las imágenes por nombre de archivo de manera natural
    transparencias_items_lista.sort(key=lambda item: ordenar_por_numero(item.name))
    
    project.activeSequence.videoTracks[2].insertClip(video_item, time_from_seconds(0))
    project.activeSequence.audioTracks[2].overwriteClip(audio_item, time_from_seconds(0))
    
    for imagen_item in reversed(transparencias_items_lista):
        project.activeSequence.videoTracks[1].insertClip(imagen_item, time_from_seconds(0))

    project.activeSequence.videoTracks[0].insertClip(fondo_item, time_from_seconds(0))
    
def leer_guia_diapositivas(archivo_guia_diapositivas):
    with open(archivo_guia_diapositivas, 'r') as file:
        content = file.read()
    lines = content.strip().replace('\r', '').split('\n')
    diapositivas = []
    speaker = []
    tiempo_speaker = lines[1]
    tiempo_inicio_speaker, tiempo_fin_speaker = tiempo_speaker.split(' --> ')
    speaker.append({
        'tiempo_inicio': tiempo_inicio_speaker,
        'tiempo_fin': tiempo_fin_speaker
    })

    for i in range(3, len(lines), 3):
        numero = int(lines[i])
        tiempo_inicio, tiempo_fin = lines[i + 1].split(' --> ')
        diapositivas.append({
            'numero': numero,
            'tiempo_inicio': tiempo_inicio,
            'tiempo_fin': tiempo_fin
        })
    print(speaker)
    print(diapositivas)
    return diapositivas, speaker

def ajustar_tiempo_aparicion_persona(guia_speaker):
    sequence = pymiere.objects.app.project.activeSequence
    video_track = sequence.videoTracks[2]
    tiempo_inicio_speaker = guia_speaker[0]['tiempo_inicio']
    tiempo_fin_speaker = guia_speaker[0]['tiempo_fin']
    clip = video_track.clips[0]
    clip.start = time_from_seconds(tiempo_a_segundos(tiempo_inicio_speaker))
    clip.end = time_from_seconds(tiempo_a_segundos(tiempo_fin_speaker))
    

def ajustar_diapositivas(guia_diapositivas):
    sequence = pymiere.objects.app.project.activeSequence
    video_track = sequence.videoTracks[1]
    for diapositiva in guia_diapositivas:
        numero = diapositiva['numero']
        tiempo_inicio = diapositiva['tiempo_inicio']
        tiempo_fin = diapositiva['tiempo_fin']
        clip = video_track.clips[numero - 1]
        clip.start = time_from_seconds(tiempo_a_segundos(tiempo_inicio))
        clip.end = time_from_seconds(tiempo_a_segundos(tiempo_fin))
        for component in clip.components:
            if component.displayName == "Movimiento":
                for property in component.properties:
                    if property.displayName == "Escala":
                        property.setValue(110, True)
                    if property.displayName == "Posición":
                        property.setValue([0.4, 0.5], True)
                    
        # Añadir y configurar el efecto "Sombra Paralela"
        qe_project = pymiere.objects.qe.project  
        qe_clip = qe_project.getActiveSequence().getVideoTrackAt(1).getItemAt(numero - 1)
        qe_clip.addVideoEffect(qe_project.getVideoEffectByName("Sombra paralela"))
        
        for component in clip.components:
            if component.displayName == "Sombra paralela":
                for property in component.properties:
                    print(property.displayName)
                    if property.displayName == "Distancia":
                        property.setValue(25, True)  # Ajusta la distancia de la sombra
                    if property.displayName == "Dirección":
                        property.setValue(225, True)  # Ajusta el ángulo de la sombra
                    if property.displayName == "Opacidad":
                        property.setValue(60, True)  # Ajusta la opacidad de la sombra
                    if property.displayName == "Suavizado":
                        property.setValue(30, True)

def ajustar_persona(recorte_izquierda, recorte_derecha, recorte_arriba, recorte_abajo):
    try:
        sequence = pymiere.objects.app.project.activeSequence
        clip = sequence.videoTracks[2].clips[0]  # Ajusta según la pista y clip que necesites
        qe_project = pymiere.objects.qe.project

        # Obtener la secuencia activa
        active_sequence = qe_project.getActiveSequence()
        if not active_sequence:
            raise ValueError("No hay una secuencia activa")
        print("Secuencia activa obtenida.")

        # Obtener la pista de video V3 (índice 2)
        try:
            video_track = active_sequence.getVideoTrackAt(2)  # V3
        except Exception as e:
            raise ValueError(f"Error al obtener la pista de video V3: {e}")

        if not video_track:
            raise ValueError("No se encontró la pista de video V3")
        print("Pista de video V3 obtenida.")

        # Verificar la cantidad de clips en la pista de video V3
        clip_count = video_track.numItems
        print(f"Cantidad de clips encontrados en V3: {clip_count}")

        # Obtener el único clip en la pista de video V3
        if clip_count > 0:
            for i in range(clip_count-1):
                qe_clip = video_track.getItemAt(i)
                # Obtener el efecto de recorte
                recortar_effect = qe_project.getVideoEffectByName("Recortar")
                if not recortar_effect:
                    raise ValueError("El efecto 'Recortar' no se encontró")
                print("Efecto 'Recortar' encontrado.")

                # Añadir el efecto al clip
                qe_clip.addVideoEffect(recortar_effect)
                print("Intentando añadir el efecto 'Recortar' al clip.")

            


                # Aplicar el recorte
                for component in clip.components:
                    if component.displayName == "Recortar":
                        for property in component.properties:
                            if property.displayName == "Izquierda":
                                property.setValue(recorte_izquierda, True)
                            if property.displayName == "Derecha":
                                property.setValue(recorte_derecha, True)
                            if property.displayName == "Arriba":
                                property.setValue(recorte_arriba, True)
                            if property.displayName == "Abajo":
                                property.setValue(recorte_abajo, True)

                # Añadir el efecto 'Ultra Key'
                qe_clip.addVideoEffect(qe_project.getVideoEffectByName("Incrustación ultra"))

                # Aplicar el efecto Ultra Key para eliminar el fondo verde
                for component in clip.components:
                    if component.displayName == "Incrustación ultra":
                        for property in component.properties:
                            if property.displayName == "Incrustación por croma":
                                property.setColorValue(0,209,255,133, True)
                            if property.displayName == "Contraste":
                                property.setValue(80, True)  # Ajusta según sea necesario
                            if property.displayName == "Punto medio":
                                property.setValue(80, True)  # Ajusta según sea necesario

    except Exception as e:
        print(f"Error: {e}")

    # mover la persona a la mitad derecha de la pantalla
    try:
        sequence = pymiere.objects.app.project.activeSequence
        clip = sequence.videoTracks[2].clips[0]  # Ajusta según la pista y clip que necesites
        # Aplicar el movimiento
        for component in clip.components:
            if component.displayName == "Movimiento":
                for property in component.properties:
                    if property.displayName == "Escala":  
                        property.setValue(90, True)
                    if property.displayName == "Posición":
                        property.setValue([0.8, 0.6], True)  # Ajusta según sea necesario

    except Exception as e:
        print(f"Error: {e}")


def alargar_fondo():
    try:
        sequence = pymiere.objects.app.project.activeSequence
        clip = sequence.videoTracks[0].clips[0]  # Ajusta según la pista y clip que necesites
        # Acaba cuando acaba el video
        clip.end = sequence.videoTracks[2].clips[0].end

    except Exception as e:
        print(f"Error: {e}")