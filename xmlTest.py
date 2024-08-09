import re
import os

def get_file_path(prompt):
    return input(prompt).strip()

def detect_encoding(file_path):
    encodings_to_try = ['cp1250', 'utf-8', 'ibm852', 'iso-8859-2']

    for encoding in encodings_to_try:
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                first_line = file.readline()
                if "<?xml" in first_line:
                    match = re.search(r'encoding=["\'](.+?)["\']', first_line)
                    if match:
                        encoding_name = match.group(1)
                        return encoding_name
                return encoding
        except:
            continue

    print("Nepodařilo se detekovat kódování. Použije se Windows-1250.")
    return 'cp1250'

def process_file(input_file_path, output_file_path, encoding):
    print("Začínám zpracování souboru...")
    output = []

    with open(input_file_path, 'r', encoding=encoding) as file:
        lines = file.readlines()

    start_recording = False

    for line in lines:
        if "<titulek>" in line:
            print("Nalezen tag <titulek> - začínám zaznamenávat.")
            start_recording = True

        if start_recording:
            processed_line = process_line(line)
            output.append(processed_line)

    final_output = '\n'.join(output).strip()

    if final_output.endswith("</kniha>"):
        final_output = final_output[:-len("</kniha>")].strip()

    if not final_output:
        print("Varování: Nebyl zpracován žádný obsah. Výstupní soubor bude prázdný.")
    else:
        try:
            with open(output_file_path, 'w', encoding='utf-8') as file:
                file.write(final_output)
            print(f"Výstup byl úspěšně zapsán do: {output_file_path}")
            print(f"Délka výsledného obsahu: {len(final_output)} znaků")
            print("Použité kódování: UTF-8")

            with open(output_file_path, 'r', encoding='utf-8') as file:
                content = file.read(100)
                print(f"Prvních 100 znaků obsahu souboru: {content}")
        except Exception as ex:
            print(f"Chyba při zápisu do souboru: {ex}")
            raise

def process_line(line):
    pattern = r'<odkazo n="(?P<odkazo>.*?)"/>|<odkaz n="(?P<odkaz>.*?)"/>'
    line = re.sub(pattern, lambda m: f"\\fo{m.group('odkazo')}\\fo*" if m.group('odkazo') else f"\\f{m.group('odkaz')}\\f*", line)
    return line

if __name__ == "__main__":
    try:
        input_file_path = get_file_path("Zadejte cestu k vstupnímu XML souboru: ")
        output_file_path = get_file_path("Zadejte cestu k výstupnímu souboru: ")

        if not os.path.exists(input_file_path):
            raise FileNotFoundError(f"Vstupní soubor nebyl nalezen: {input_file_path}")

        encoding = detect_encoding(input_file_path)
        print(f"Detekované kódování: {encoding}")

        process_file(input_file_path, output_file_path, encoding)

        print("Zpracování dokončeno.")
    except Exception as ex:
        print(f"Došlo k chybě: {ex}")
    finally:
        input("Stiskněte libovolnou klávesu pro ukončení...")
