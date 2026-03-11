from pypdf import PdfReader
import re

# IMPORTANTE: Cambiar este nombre por el archivo PDF a analizar
pdf = "0010216255_c6ef39c4-f7d1-4873-8621-f37319a726b4.pdf"
reader = PdfReader(pdf)

# Acceder a los campos de formulario del PDF
fields = reader.trailer["/Root"]["/AcroForm"]["/Fields"]

# Iterar sobre cada campo buscando firmas
for i, f in enumerate(fields, start=1):
    obj = f.get_object()
    sig = obj["/V"].get_object()
    contents = str(sig["/Contents"])

    print(f"\n=== Firma {i} ===")
    print("Campo:", obj.get("/T"))
    print("Fecha:", sig.get("/M"))
    print("SubFilter:", sig.get("/SubFilter"))
    print("ByteRange:", sig.get("/ByteRange"))

    # Buscar CUIL en el contenido de la firma
    cuil_match = re.search(r"CUIL\s+(\d{11})", contents, re.DOTALL)
    if cuil_match:
        print("CUIL visible:", cuil_match.group(1))
    else:
        print("CUIL visible: no encontrado")

    # NOTA TÉCNICA:
    # El siguiente bloque de código realiza únicamente una búsqueda de palabras clave
    # dentro del contenido ya existente del archivo PDF previamente extraído.
    #
    # Es importante aclarar que este procedimiento NO modifica el documento,
    # NO agrega texto, NO altera el contenido del PDF y NO "fuerza" la aparición
    # de palabras dentro del archivo.
    #
    # La función re.search simplemente localiza si una cadena de texto ya está
    # presente dentro del contenido del documento. En caso de encontrarla,
    # se imprime un fragmento del contexto circundante únicamente con fines
    # de inspección y verificación.
    #
    # Por lo tanto, si aparecen palabras como "RODRIGO", "MUKDISE", "CUIL" o
    # "MODERNIZACION", ello significa que dichas palabras ya estaban contenidas
    # originalmente dentro del PDF analizado, y el script únicamente las detecta
    # y muestra parte del texto donde se encuentran.
    #
    # Este procedimiento es equivalente a utilizar la función "buscar" dentro
    # de un lector de PDF, pero automatizado mediante código.

    # Buscar palabras clave y mostrar contexto.
    for palabra in ["RODRIGO", "MUKDISE", "CUIL", "MODERNIZACION"]:
        mm = re.search(palabra, contents, re.IGNORECASE)
        if mm:
            ini = max(0, mm.start() - 80)
            fin = min(len(contents), mm.end() + 180)
            print(f"Contexto [{palabra}]:")
            print(contents[ini:fin].replace("\r", " ").replace("\n", " "))
