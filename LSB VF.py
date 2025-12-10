from PIL import Image
import sys

def bytes_a_bits(data: bytes):
    
    """Convierte bytes a una secuencia de bits (0/1)"""
    
    for byte in data:
        for i in range(8):
            yield (byte >> (7 - i)) & 1


def bits_a_bytes(bits):
    
    """Convierte una secuencia de bits (0/1) a bytes"""
    
    b = 0
    out = bytearray()
    count = 0
    for bit in bits:
        b = (b << 1) | bit
        count += 1
        if count == 8:
            out.append(b)
            b = 0
            count = 0
    return bytes(out)

# ===============================
#   OCULTAR MENSAJE (El llmado ENCODE)
# ===============================

def ocultar_mensaje_en_imagen(ruta_entrada, ruta_salida, mensaje):
    img = Image.open(ruta_entrada)

    if img.mode != "RGB":
        img = img.convert("RGB")

    pixels = img.load()
    ancho, alto = img.size

    datos_mensaje = mensaje.encode("utf-8")
    longitud = len(datos_mensaje)

    header = longitud.to_bytes(4, byteorder="big")

    bits = list(bytes_a_bits(header + datos_mensaje))

    capacidad = ancho * alto * 3

    if len(bits) > capacidad:
        raise ValueError(
            f"Mensaje demasiado grande Capacidad: {capacidad} bits, Mensaje: {len(bits)} bits"
        )

    # Se insertan los bits en los LSB
    idx = 0
    for y in range(alto):
        for x in range(ancho):
            r, g, b = pixels[x, y]
            nuevos = [r, g, b]

            for canal in range(3):
                if idx < len(bits):
                    nuevos[canal] = (nuevos[canal] & ~1) | bits[idx]
                    idx += 1

            pixels[x, y] = tuple(nuevos)

            if idx >= len(bits):
                break
        if idx >= len(bits):
            break

    img.save(ruta_salida)
    print(f"\n✅ Mensaje ocultado exitosamente en '{ruta_salida}' ({longitud} bytes).")


# ===============================
#   EXTRAER MENSAJE (El llamado DECODE)
# ===============================

def extraer_mensaje_de_imagen(ruta_imagen):
    img = Image.open(ruta_imagen)

    if img.mode != "RGB":
        img = img.convert("RGB")

    pixels = img.load()
    ancho, alto = img.size

    bits = []
    for y in range(alto):
        for x in range(ancho):
            r, g, b = pixels[x, y]
            bits.append(r & 1)
            bits.append(g & 1)
            bits.append(b & 1)

    header_bits = bits[:32]
    header_bytes = bits_a_bytes(header_bits)
    longitud = int.from_bytes(header_bytes, byteorder="big")

    # Bits del mensaje
    total_bits_mensaje = longitud * 8
    mensaje_bits = bits[32 : 32 + total_bits_mensaje]

    mensaje_bytes = bits_a_bytes(mensaje_bits)

    try:
        return mensaje_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return None


# ===============================
#   MENÚ PRINCIPAL (LOOP)
# ===============================

def main():
    while True:
        print("\n==============================")
        print(" Esteganografía LSB en imágenes")
        print(" (solo uso educativo)")
        print("==============================")
        print("1) Ocultar mensaje")
        print("2) Extraer mensaje")
        print("3) Salir")
        opcion = input("Elige una opción (1/2/3): ").strip()

        # ---- Opción 1: ocultar ----
        if opcion == "1":
            ruta_entrada = input("Ruta de la imagen original: ").strip()
            ruta_salida = input("Ruta para guardar la imagen con mensaje: ").strip()
            mensaje = input("Escribe el mensaje a ocultar: ")

            try:
                ocultar_mensaje_en_imagen(ruta_entrada, ruta_salida, mensaje)
            except FileNotFoundError:
                print("❌ No se encontró la imagen. Revisa la ruta.")
            except ValueError as e:
                print(f"❌ Error: {e}")

        # ---- Opción 2: extraer ----
        elif opcion == "2":
            ruta_imagen = input("Ruta de la imagen con mensaje oculto: ").strip()

            try:
                mensaje = extraer_mensaje_de_imagen(ruta_imagen)
                if mensaje is None:
                    print("⚠ No se pudo decodificar el mensaje (imagen no válida o mensaje corrupto).")
                else:
                    print("\n✅ Mensaje extraído:")
                    print(mensaje)
            except FileNotFoundError:
                print("❌ No se encontró la imagen. Revisa la ruta.")

        # ---- Opción 3: salir ----
        elif opcion == "3":
            print("\nSaliendo...")
            sys.exit()

        else:
            print("❌ Opción no válida. Intenta de nuevo.")


if __name__ == "__main__":
    main()
