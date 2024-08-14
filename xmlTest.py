import re
import os

def get_file_path(prompt):
    return input(prompt).strip()

def store_all_defpozn(content, defpozn_dict):
    pattern = r'<defpozn n="(.+?)">(.*?)</defpozn>'
    matches = re.findall(pattern, content, re.DOTALL)
    for n, pozn_content in matches:
        defpozn_dict[n] = pozn_content

def store_all_defpozno(content, defpozno_dict):
    pattern = r'<defpozno n="(.+?)">(.*?)</defpozno>'
    matches = re.findall(pattern, content, re.DOTALL)
    for n, pozn_content in matches:
        defpozno_dict[n] = pozn_content

def replace_odkaz(content, defpozn_dict):
    pattern = r'<odkaz n="(.+?)"/>'
    modified = False

    def replacer(match):
        nonlocal modified
        n = match.group(1)
        if n in defpozn_dict:
            modified = True
            return f'\\f{defpozn_dict[n]}\\f*'
        return match.group(0)

    result = re.sub(pattern, replacer, content)
    return result, modified

def replace_odkazo(content, defpozno_dict):
    pattern = r'<odkazo n="(.+?)"/>'
    modified = False

    def replacer(match):
        nonlocal modified
        n = match.group(1)
        if n in defpozno_dict:
            modified = True
            return f'\\fo{defpozno_dict[n]}\\fo*'
        return match.group(0)

    result = re.sub(pattern, replacer, content)
    return result, modified

def process_content(content, defpozn_dict, defpozno_dict):
    modified = True
    while modified:
        content, modified = replace_odkaz(content, defpozn_dict)
        if modified:
            continue
        content, modified = replace_odkazo(content, defpozno_dict)
    return content

def process_file(file_content, output_file_path):
    print("Začínám zpracování souboru...")

    defpozn_dict = {}
    defpozno_dict = {}

    store_all_defpozn(file_content, defpozn_dict)
    store_all_defpozno(file_content, defpozno_dict)

    start_index = file_content.find("<titulek>")
    if start_index == -1:
        raise Exception("Tag <titulek> nebyl nalezen.")

    processed_content = process_content(file_content[start_index:], defpozn_dict, defpozno_dict)

    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        output_file.write(processed_content)

    print(f"Výstup byl úspěšně zapsán do: {output_file_path}")

def main():
    try:
        input_file_path = get_file_path("Zadejte cestu k vstupnímu XML souboru: ")
        output_file_path = get_file_path("Zadejte cestu k výstupnímu souboru: ")

        if not os.path.exists(input_file_path):
            raise FileNotFoundError(f"Vstupní soubor nebyl nalezen: {input_file_path}")

        with open(input_file_path, 'r', encoding='cp1250') as input_file:
            file_content = input_file.read()

        print("Převádím obsah souboru na UTF-8...")
        process_file(file_content, output_file_path)

        print("Zpracování dokončeno.")
    except Exception as ex:
        print(f"Došlo k chybě: {ex}")
    finally:
        input("Stiskněte libovolnou klávesu pro ukončení...")

if __name__ == "__main__":
    main()
