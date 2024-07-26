import os
import re
import xml.etree.ElementTree as ET


def get_file_path(prompt):
    return input(prompt).strip()

def detect_encoding_robust(file_path):
    encodings_to_try = ['windows-1250', 'utf-8', 'ibm852', 'iso-8859-2']
    
    for encoding in encodings_to_try:
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                first_line = file.readline()
                if first_line and '<?xml' in first_line:
                    match = re.search(r'encoding=["\'](.+?)["\']', first_line)
                    if match:
                        encoding_name = match.group(1)
                        try:
                            return encoding_name
                        except LookupError:
                            pass
                    return encoding
        except UnicodeDecodeError:
            continue
    
    print("Nepodařilo se detekovat kódování. Použije se Windows-1250.")
    return 'windows-1250'

def process_defpozn(line, tag_name, replace_tag):
    pattern = f'<{tag_name} n="(.+?)">(.*?)</{tag_name}>'
    return re.sub(pattern, lambda m: f"{replace_tag}{m.group(2)}{replace_tag}*", line)

def replace_odkaz(line, root, modified):
    start_index = line.find('<odkaz n="')
    if start_index != -1:
        end_index = line.find('"/>', start_index)
        if end_index != -1:
            odkaz = line[start_index + 10:end_index].strip('"')
            if odkaz:
                new_text = get_defpozn_text(root, odkaz)
                if new_text:
                    line = line[:start_index] + f"\\f{new_text}\\f*" + line[end_index + 3:]
                    modified[0] = True
    return line

def replace_odkazo(line, root, modified):
    start_index = line.find('<odkazo n="')
    if start_index != -1:
        end_index = line.find('"/>', start_index)
        if end_index != -1:
            odkaz = line[start_index + 11:end_index].strip('"')
            if odkaz:
                new_text = get_defpozno_text(root, odkaz)
                if new_text:
                    line = line[:start_index] + f"\\fo{new_text}\\fo*" + line[end_index + 3:]
                    modified[0] = True
    return line

def get_defpozn_text(root, odkaz):
    defpozn = root.find(f".//defpozn[@n='{odkaz}']")
    return defpozn.text if defpozn is not None else None

def get_defpozno_text(root, odkaz):
    defpozno = root.find(f".//defpozno[@n='{odkaz}']")
    return defpozno.text if defpozno is not None else None

def process_line(line, root):
    if '<defpozno' in line or '<defpozn' in line:
        line = process_defpozn(line, 'defpozno', '\\fo')
        line = process_defpozn(line, 'defpozn', '\\f')
    else:
        modified = [False]
        while True:
            line = replace_odkaz(line, root, modified)
            line = replace_odkazo(line, root, modified)
            if not modified[0]:
                break
            modified[0] = False
    return line

def process_file(input_file_path, output_file_path, input_encoding):
    print("Začínám zpracování souboru...")
    output = []

    tree = ET.parse(input_file_path)
    root = tree.getroot()

    with open(input_file_path, 'r', encoding=input_encoding) as file:
        start_recording = False
        for line in file:
            if line.startswith('<?xml') or line.startswith('<!DOCTYPE'):
                continue

            if '<titulek>' in line:
                print("Nalezen tag <titulek> - začínám zaznamenávat.")
                start_recording = True

            if start_recording:
                line = process_line(line.strip(), root)
                output.append(line)

    final_output = '\n'.join(output).rstrip()

    if final_output.endswith('</kniha>'):
        final_output = final_output[:-8].rstrip()

    if not final_output.strip():
        print("Varování: Nebyl zpracován žádný obsah. Výstupní soubor bude prázdný.")
    else:
        try:
            with open(output_file_path, 'w', encoding='utf-8') as file:
                file.write(final_output)

            print(f"Výstup byl úspěšně zapsán do: {output_file_path}")
            print(f"Délka výsledného obsahu: {len(final_output)} znaků")
            print("Použité kódování: UTF-8")

            with open(output_file_path, 'r', encoding='utf-8') as file:
                file_content = file.read(100)
                print(f"Prvních 100 znaků obsahu souboru: {file_content}")
        except Exception as ex:
            print(f"Chyba při zápisu do souboru: {str(ex)}")
            raise

def main():
    try:
        input_file_path = get_file_path("Zadejte cestu k vstupnímu XML souboru: ")
        output_file_path = get_file_path("Zadejte cestu k výstupnímu souboru: ")

        if not os.path.exists(input_file_path):
            raise FileNotFoundError(f"Vstupní soubor nebyl nalezen: {input_file_path}")

        input_encoding = detect_encoding_robust(input_file_path)
        print(f"Detekované kódování: {input_encoding}")

        if input_encoding != 'windows-1250':
            print("Přepínám na Windows-1250 kódování...")
            input_encoding = 'windows-1250'

        process_file(input_file_path, output_file_path, input_encoding)

        print("Zpracování dokončeno.")
    except Exception as ex:
        print(f"Došlo k chybě: {str(ex)}")
        print(f"Stack trace: {ex.__traceback__}")
    finally:
        input("Stiskněte Enter pro ukončení...")

if __name__ == "__main__":
    main()