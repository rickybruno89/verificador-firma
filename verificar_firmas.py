from pypdf import PdfReader
import re

pdf = "0010216255_c6ef39c4-f7d1-4873-8621-f37319a726b4.pdf"
reader = PdfReader(pdf)

fields = reader.trailer["/Root"]["/AcroForm"]["/Fields"]

for i, f in enumerate(fields, start=1):
    obj = f.get_object()
    sig = obj["/V"].get_object()
    contents = str(sig["/Contents"])

    print(f"\n=== Firma {i} ===")
    print("Campo:", obj.get("/T"))
    print("Fecha:", sig.get("/M"))
    print("SubFilter:", sig.get("/SubFilter"))
    print("ByteRange:", sig.get("/ByteRange"))

    cuil_match = re.search(r"CUIL\s+(\d{11})", contents, re.DOTALL)
    if cuil_match:
        print("CUIL visible:", cuil_match.group(1))
    else:
        print("CUIL visible: no encontrado")

    for palabra in ["RODRIGO", "MUKDISE", "CUIL", "MODERNIZACION"]:
        mm = re.search(palabra, contents, re.IGNORECASE)
        if mm:
            ini = max(0, mm.start() - 80)
            fin = min(len(contents), mm.end() + 180)
            print(f"Contexto [{palabra}]:")
            print(contents[ini:fin].replace("\r", " ").replace("\n", " "))