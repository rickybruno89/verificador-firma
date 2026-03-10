#!/usr/bin/env python3
"""
Verificador de Firmas Digitales en PDF
Extrae información de firmantes y genera archivo de reporte
Uso: python3 verificar_firmas.py [archivo.pdf]
"""

import re
from datetime import datetime
from pypdf import PdfReader

def parsear_fecha_pdf(fecha_raw):
    """Convierte fecha PDF (D:YYYYMMDDHHmmSS-TZ) a formato legible"""
    if not fecha_raw:
        return None
    try:
        # Extraer: D:20260211091919-03'00'
        match = re.match(r"D:(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})([+-]\d{2})'(\d{2})'", str(fecha_raw))
        if match:
            año, mes, dia, hora, min, seg, tz_h, tz_m = match.groups()
            return f"{dia}/{mes}/{año} {hora}:{min}:{seg} (UTC{tz_h}:{tz_m})"
    except:
        pass
    return None



pdf = "0010216255_c6ef39c4-f7d1-4873-8621-f37319a726b4.pdf"
reader = PdfReader(pdf)
fields = reader.trailer["/Root"]["/AcroForm"]["/Fields"]

reporte_raw = []
reporte_raw.append(f"REPORTE DE FIRMAS DIGITALES (RAW)")
reporte_raw.append(f"Fecha análisis: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
reporte_raw.append("=" * 70)

reporte_limpio = []
reporte_limpio.append(f"REPORTE DE FIRMAS DIGITALES (INTERPRETADO)")
reporte_limpio.append(f"Fecha análisis: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
reporte_limpio.append("=" * 70)

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
    
    # Buscar nombre del firmante (patrón antes de CUIL)
    nombre_match = re.search(r'U\s+([A-Za-zÀ-ÿÃ\s]+?[A-Z]+)1[ˇ˛˙˚˝]', texto)
    nombre = nombre_match.group(1).strip() if nombre_match else "No encontrado"

    # Extraer organización emisora
    org_match = re.search(r'(MINISTERIO[^1]+)', texto)
    organizacion = org_match.group(1).strip() if org_match else None

    # Extraer autoridad certificante
    ac_match = re.search(r'(AC\s+[A-Z\-]+)', texto)
    autoridad_cert = ac_match.group(1).strip() if ac_match else None

    # Extraer URLs relevantes y limpiarlas
    urls = re.findall(r'(https?://[a-zA-Z0-9./_-]+\.(?:crt|pdf|crl|ocsp))', texto)
    urls = list(set(urls))  # Eliminar duplicados


    print(f"Nombre: {nombre}")

    # === REPORTE RAW (con contenido completo) ===
    reporte_raw.append(f"\n{'='*70}")
    reporte_raw.append(f"FIRMA #{i}")
    reporte_raw.append(f"{'='*70}")
    reporte_raw.append(f"Campo: {obj.get('/T')}")
    reporte_raw.append(f"Fecha: {sig.get('/M')}")
    reporte_raw.append(f"Tipo: {sig.get('/SubFilter')}")
    reporte_raw.append(f"ByteRange: {sig.get('/ByteRange')}")
    if cuil:
        reporte_raw.append(f"CUIL: {cuil.group(1)}")
    if cuit:
        reporte_raw.append(f"CUIT Org: {cuit.group(1)}")
    if email:
        reporte_raw.append(f"Email: {email.group(1)}")
    reporte_raw.append(f"\n--- CONTENIDO RAW DE LA FIRMA (primeros 3000 chars) ---")
    reporte_raw.append(texto[:3000])
    reporte_raw.append(f"\n--- FIN CONTENIDO FIRMA #{i} ---")

    # === REPORTE LIMPIO (interpretado) ===
    reporte_limpio.append(f"\n{'='*70}")
    reporte_limpio.append(f"FIRMA #{i}")
    reporte_limpio.append(f"{'='*70}")
    reporte_limpio.append(f"Campo: {obj.get('/T')}")
    fecha_raw = sig.get('/M')
    fecha_legible = parsear_fecha_pdf(fecha_raw)
    reporte_limpio.append(f"Fecha firma: {fecha_raw}")
    if fecha_legible:
        reporte_limpio.append(f"Fecha legible: {fecha_legible}")
    reporte_limpio.append(f"Tipo: {sig.get('/SubFilter')}")
    if cuil:
        reporte_limpio.append(f"CUIL: {cuil.group(1)}")
    if nombre:
        reporte_limpio.append(f"Nombre: {nombre}")
    if cuit:
        reporte_limpio.append(f"CUIT Org: {cuit.group(1)}")
    if email:
        reporte_limpio.append(f"Email: {email.group(1)}")

    reporte_limpio.append(f"\n--- CERTIFICADO ---")
    if organizacion:
        reporte_limpio.append(f"Emisor: {organizacion}")
    if autoridad_cert:
        reporte_limpio.append(f"Autoridad: {autoridad_cert}")
    if urls:
        reporte_limpio.append(f"URLs validación:")
        for url in urls:
            reporte_limpio.append(f"  - {url}")

# Guardar reporte RAW
output_raw = "output_firmas.txt"
with open(output_raw, 'w', encoding='utf-8') as f:
    f.write('\n'.join(reporte_raw))

# Guardar reporte LIMPIO
output_limpio = "interpretacion_output.txt"
with open(output_limpio, 'w', encoding='utf-8') as f:
    f.write('\n'.join(reporte_limpio))

print(f"\n{'='*50}")
print(f"Reporte RAW guardado en: {output_raw}")
print(f"Reporte interpretado guardado en: {output_limpio}")
print(f"{'='*50}\n")



