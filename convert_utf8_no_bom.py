# convert_utf16_to_utf8_no_bom.py
import chardet

# Lire le fichier en binaire
with open("dump.json", "rb") as f:
    raw_data = f.read()

# Détecter l'encodage
result = chardet.detect(raw_data)
encoding = result['encoding']
print(f"Encodage détecté : {encoding}")

# Décoder correctement
text = raw_data.decode(encoding)

# Supprimer un éventuel BOM résiduel
if text.startswith('\ufeff'):
    text = text[1:]

# Réécrire en UTF-8 sans BOM
with open("dump_clean.json", "w", encoding="utf-8") as f:
    f.write(text)

print("Fichier converti en UTF-8 sans BOM : dump_clean.json")