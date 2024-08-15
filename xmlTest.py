import os
import re
import codecs
import sys
import traceback

def get_file_path(prompt):
    return input(prompt).strip()

def store_all_defpozn(content, defpozn_dictionary):
    pattern = r'<defpozn n="(.+?)">(.*?)</defpozn>'
    for match in re.finditer(pattern, content, re.DOTALL):
        n = match.group(1)
        pozn_content = match.group(2)
        defpozn_dictionary[n] = pozn_content

def store_all_defpozno(content, defpozno_dictionary):
    pattern = r'<defpozno n="(.+?)">(.*?)</defpozno>'
    for match in re.finditer(pattern, content, re.DOTALL):
        n = match.group(1)
        pozn_content = match.group(2)
        defpozno_dictionary[n] = pozn_content

def replace_odkaz(content, defpozn_dictionary):
    def replace_func(match):
        letter = match.group(1)
        n = match.group(2)
        full_key = letter + n
        if full_key in defpozn_dictionary:
            return f"\\sup {letter}\\sup*\\f{defpozn_dictionary[full_key]}\\f*"
        return match.group(0)
    
    pattern = r'<odkaz n="(.)(\d+)"/>'
    new_content = re.sub(pattern, replace_func, content)
    return new_content, new_content != content

def replace_odkazo(content, defpozno_dictionary):
    def replace_func(match):
        letter = match.group(1)
        n = match.group(2)
        full_key = letter + n
        if full_key in defpozno_dictionary:
            return f"\\sup {letter}\\sup*\\fo{defpozno_dictionary[full_key]}\\fo*"
        return match.group(0)
    
    pattern = r'<odkazo n="(.)(\d+)"/>'
    new_content = re.sub(pattern, replace_func, content)
    return new_content, new_content != content

def process_content(content, defpozn_dictionary, defpozno_dictionary):
    while True:
        content, modified1 = replace_odkaz(content, defpozn_dictionary)
        content, modified2 = replace_odkazo(content, defpozno_dictionary)
        if not (modified1 or modified2):
            break
    return content

def process_file(file_content, output_file_path):
    print("Začínám zpracování souboru...")

    defpozn_dictionary = {}
    defpozno_dictionary = {}

    store_all_defpozn(file_content, defpozn_dictionary)
    store_all_defpozno(file_content, defpozno_dictionary)

    start_index = file_content.find("<titulek>")
    if start_index == -1:
        raise Exception("Tag <titulek> nebyl nalezen.")

    processed_content = process_content(file_content[start_index:], defpozn_dictionary, defpozno_dictionary)

    with open(output_file_path, 'w', encoding='utf-8') as f:
        f.write(processed_content)

    print(f"Výstup byl úspěšně zapsán do: {output_file_path}")

def main():
    try:
        input_file_path = get_file_path("Zadejte cestu k vstupnímu XML souboru: ")
        output_file_path = get_file_path("Zadejte cestu k výstupnímu souboru: ")

        if not os.path.exists(input_file_path):
            raise FileNotFoundError(f"Vstupní soubor nebyl nalezen: {input_file_path}")

        print("Převádím obsah souboru na UTF-8...")
        with codecs.open(input_file_path, 'r', encoding='cp1250') as f:
            file_content = f.read()

        process_file(file_content, output_file_path)

        print("Zpracování dokončeno.")
    except Exception as ex:
        print(f"Došlo k chybě: {str(ex)}")
        print(f"Stack trace: {traceback.format_exc()}")
    finally:
        input("Stiskněte Enter pro ukončení...")

if __name__ == "__main__":
    main()