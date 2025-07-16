#!/bin/bash
# Este script actualizará tu repositorio en Git desde tu VPS

# Verifica si hay cambios locales
git add .
git commit -m "Actualización"

# Empuja los cambios al repositorio remoto
git push origin main  # Asegúrate de usar la rama correcta
