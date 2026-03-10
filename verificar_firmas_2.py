#!/usr/bin/env python3
"""
Verificador de Firmas Digitales en PDF
Extrae información de firmantes y genera archivo de reporte
Uso: python3 verificar_firmas.py [archivo.pdf]
"""

import sys
import re
from datetime import datetime
from pypdf import PdfReader



pdf = "0010216255_c6ef39c4-f7d1-4873-8621-f37319a726b4.pdf"
reader = PdfReader(pdf)
fields = reader.trailer["/Root"]["/AcroForm"]["/Fields"]

reporte = []
reporte.append(f"REPORTE DE FIRMAS DIGITALES")
reporte.append(f"Fecha análisis: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
reporte.append("=" * 70)

for i, f in enumerate(fields, start=1):
    obj = f.get_object()
    if "/V" not in obj:
        continue
        
    sig = obj["/V"].get_object()
    contents = sig["/Contents"]
    
    # Obtener bytes originales y decodificar
    data = contents.original_bytes
    texto = data.decode('utf-16-be', errors='ignore')
    
    print(f"\n{'─'*50}")
    print(f"FIRMA #{i}")
    print(f"{'─'*50}")
    print(f"Campo: {obj.get('/T')}")
    print(f"Fecha: {sig.get('/M')}")
    print(f"Tipo: {sig.get('/SubFilter')}")
    
    # Extraer CUIL
    cuil = re.search(r'CUIL\s*(\d{11})', texto)
    if cuil:
        print(f"CUIL: {cuil.group(1)}")
    
    # Extraer CUIT organización
    cuit = re.search(r'CUIT\s*(\d{11})', texto)
    if cuit:
        print(f"CUIT Org: {cuit.group(1)}")
    
    # Extraer email
    email = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,})', texto)
    if email:
        print(f"Email: {email.group(1)}")
    
    # Contexto alrededor del CUIL (donde está el nombre)
    cuil_ctx = re.search(r'.{0,200}CUIL.{0,50}', texto)
    if cuil_ctx:
        ctx = cuil_ctx.group(0)
        print(f"\nContexto firmante:")
        print(f"  {ctx}")
    
    # Guardar en reporte
    reporte.append(f"\n{'='*70}")
    reporte.append(f"FIRMA #{i}")
    reporte.append(f"{'='*70}")
    reporte.append(f"Campo: {obj.get('/T')}")
    reporte.append(f"Fecha: {sig.get('/M')}")
    reporte.append(f"Tipo: {sig.get('/SubFilter')}")
    reporte.append(f"ByteRange: {sig.get('/ByteRange')}")
    if cuil:
        reporte.append(f"CUIL: {cuil.group(1)}")
    if cuit:
        reporte.append(f"CUIT Org: {cuit.group(1)}")
    if email:
        reporte.append(f"Email: {email.group(1)}")
    
    reporte.append(f"\n--- CONTENIDO RAW DE LA FIRMA (primeros 3000 chars) ---")
    reporte.append(texto[:3000])
    reporte.append(f"\n--- FIN CONTENIDO FIRMA #{i} ---")

# Guardar reporte
output_file = "output_firmas.txt"
with open(output_file, 'w', encoding='utf-8') as f:
    f.write('\n'.join(reporte))

print(f"\n{'='*50}")
print(f"Reporte guardado en: {output_file}")
print(f"{'='*50}\n")



