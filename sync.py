#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sync.py — Script interactivo para la gestión de prospectos de Nexora.

Funcionalidades:
  1. Agregar nuevos prospectos a clientes.json.
  2. Cambiar el estado de un cliente existente.
  3. Ejecutar automáticamente git add, git commit y git push
     al repositorio privado de GitHub para actualizar Vercel.

Uso:
    python sync.py
"""

import json
import os
import subprocess
import sys
from datetime import datetime

# Ruta al archivo de prospectos
ARCHIVO_CLIENTES = "clientes.json"

# Estados válidos
ESTADOS_VALIDOS = ["Pendiente", "Correo Enviado", "Respondió", "Rechazado"]

# Codificación UTF-8 para Windows
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def cargar_clientes():
    """Carga la lista de clientes desde clientes.json."""
    if not os.path.exists(ARCHIVO_CLIENTES):
        print("⚠️  No existe " + ARCHIVO_CLIENTES + ". Se creará uno nuevo.")
        return []
    try:
        with open(ARCHIVO_CLIENTES, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("❌ Error: " + ARCHIVO_CLIENTES + " contiene JSON inválido.")
        return []
    except Exception as e:
        print("❌ Error al leer " + ARCHIVO_CLIENTES + ": " + str(e))
        return []


def guardar_clientes(clientes):
    """Guarda la lista de clientes en clientes.json con indentación."""
    try:
        with open(ARCHIVO_CLIENTES, "w", encoding="utf-8") as f:
            json.dump(clientes, f, indent=2, ensure_ascii=False)
        print("✅ Cambios guardados en " + ARCHIVO_CLIENTES)
    except Exception as e:
        print("❌ Error al guardar: " + str(e))


def obtener_siguiente_id(clientes):
    """Devuelve el siguiente ID disponible."""
    if not clientes:
        return 1
    return max(c.get("id", 0) for c in clientes) + 1


def agregar_prospecto():
    """Agrega un nuevo prospecto a clientes.json."""
    print("\n--- Agregar nuevo prospecto ---")
    clientes = cargar_clientes()

    empresa = input("Nombre de la empresa: ").strip()
    if not empresa:
        print("❌ El nombre de la empresa es obligatorio.")
        return

    nicho = input("Nicho (mecanica / clinica / ingenieria): ").strip().lower()
    if nicho not in ("mecanica", "clinica", "ingenieria"):
        print("❌ Nicho inválido. Usa: mecanica, clinica o ingenieria.")
        return

    email = input("Email: ").strip()
    telefono = input("Teléfono: ").strip()
    contacto = input("Persona de contacto: ").strip()

    nueva_fecha = datetime.now().strftime("%Y-%m-%d")
    nuevo_id = obtener_siguiente_id(clientes)

    nuevo = {
        "id": nuevo_id,
        "empresa": empresa,
        "nicho": nicho,
        "contacto": contacto,
        "email": email,
        "telefono": telefono,
        "estado": "Pendiente",
        "fecha": nueva_fecha
    }

    clientes.append(nuevo)
    guardar_clientes(clientes)
    print("✅ Prospecto agregado: " + empresa + " (ID: " + str(nuevo_id) + ")")


def cambiar_estado():
    """Cambia el estado de un cliente existente."""
    print("\n--- Cambiar estado de un cliente ---")
    clientes = cargar_clientes()
    if not clientes:
        print("❌ No hay prospectos registrados.")
        return

    # Listar clientes
    print("\nProspectos disponibles:")
    for c in clientes:
        print("  ID " + str(c["id"]) + " - " + c["empresa"] + " | Estado: " + c.get("estado", "Pendiente"))

    try:
        id_str = input("\nIntroduce el ID del prospecto: ").strip()
        id_cliente = int(id_str)
    except ValueError:
        print("❌ ID inválido. Usa un número.")
        return

    cliente = next((c for c in clientes if c.get("id") == id_cliente), None)
    if not cliente:
        print("❌ No se encontró ningún prospecto con ID " + str(id_cliente))
        return

    print("\nEstado actual: " + cliente.get("estado", "Pendiente"))
    print("Estados disponibles:")
    for i, e in enumerate(ESTADOS_VALIDOS, 1):
        print("  " + str(i) + ") " + e)

    try:
        opcion = int(input("Selecciona el nuevo estado (1-" + str(len(ESTADOS_VALIDOS)) + "): ").strip())
        if opcion < 1 or opcion > len(ESTADOS_VALIDOS):
            print("❌ Opción fuera de rango.")
            return
        nuevo_estado = ESTADOS_VALIDOS[opcion - 1]
    except ValueError:
        print("❌ Opción inválida.")
        return

    cliente["estado"] = nuevo_estado
    cliente["fecha"] = datetime.now().strftime("%Y-%m-%d")
    guardar_clientes(clientes)
    print("✅ Estado actualizado a '" + nuevo_estado + "' para " + cliente["empresa"])


def git_push():
    """Ejecuta git add, git commit y git push."""
    print("\n--- Despliegue a GitHub/Vercel ---")

    # Verificar si git está inicializado
    if not os.path.exists(".git"):
        print("❌ No es un repositorio git. Ejecuta 'git init' primero.")
        return

    try:
        # git add
        print("\n🔄 Ejecutando: git add .")
        subprocess.run(["git", "add", "."], check=True)

        # git status para ver cambios
        print("📋 Cambios detectados:")
        subprocess.run(["git", "status", "--short"], check=True)

        # Confirmar el commit
        respuesta = input("\n¿Quieres hacer commit y push ahora? (s/n): ").strip().lower()
        if respuesta != "s":
            print("Operación cancelada.")
            return

        mensaje = input("Mensaje de commit (presiona Enter para usar el predeterminado): ").strip()
        if not mensaje:
            mensaje = "Actualiza prospectos Nexora — " + datetime.now().strftime("%Y-%m-%d %H:%M")

        # git commit
        print("\n🔄 Ejecutando: git commit -m \"" + mensaje + "\"")
        subprocess.run(["git", "commit", "-m", mensaje], check=True)

        # git push
        print("\n🔄 Ejecutando: git push")
        result = subprocess.run(["git", "push"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Push completado. Vercel desplegará los cambios automáticamente.")
        else:
            print("⚠️  git push devolvió: " + result.stderr.strip())
            print("Asegúrate de que el remoto esté configurado: git remote add origin <url>")

    except subprocess.CalledProcessError as e:
        print("❌ Error en git: " + str(e))
    except FileNotFoundError:
        print("❌ Git no está instalado o no está en el PATH.")


def menu():
    """Menú principal interactivo."""
    while True:
        print("\n" + "=" * 50)
        print("     Nexora · Sync de Prospectos")
        print("=" * 50)
        print("1. Agregar nuevo prospecto")
        print("2. Cambiar estado de un prospecto")
        print("3. Git add + commit + push (despliegue Vercel)")
        print("4. Salir")
        print("=" * 50)

        try:
            opcion = input("Selecciona una opción (1-4): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 ¡Hasta luego!")
            break

        if opcion == "1":
            agregar_prospecto()
        elif opcion == "2":
            cambiar_estado()
        elif opcion == "3":
            git_push()
        elif opcion == "4":
            print("👋 ¡Hasta luego!")
            break
        else:
            print("❌ Opción no válida. Usa 1, 2, 3 o 4.")


if __name__ == "__main__":
    menu()
