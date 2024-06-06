# Ejecutable que crea un proyecto Premier con los ficheros traducidos 


## Instrucciones de uso 

1. Inicia un nuevo proyecto vacío en Premiere.
2. Descarga de drive todos los archivos generados después de la síntesis y colócalos en una carpeta.
3. Haz clic en el botón 'Seleccionar archivo de video' y selecciona el video de esa carpeta.

## Lista de mejoras 
    - 

##  Para crear el ejecutable:

###  Win (ejecutar en la consola)
    PyInstaller InterfazPymiere.py --onefile --noconsole


###  Mac (desde un mac)
    python3 -m PyInstaller InterfazPymiere.py --onefile --noconsole
    cd dist
    tar -czvf …..tar.gz …..