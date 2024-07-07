import re
import xml.etree.ElementTree as ET


def main():
    input_file_path = "D:\\Downloads\\Studijni Bible\\Studijni_Bible\\GenMod.xml"
    output_file_path = "D:\\Downloads\\GenModifiedPython.txt"

    try:
        process_file(input_file_path, output_file_path)
    except Exception as ex:
        print(f"An error occurred: {ex}")


def process_file(input_file_path, output_file_path):
    with open(input_file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    xml_doc = ET.parse(input_file_path)
    modified_lines = [process_line(line, xml_doc) for line in lines]

    with open(output_file_path, 'w', encoding='utf-8') as file:
        file.writelines(modified_lines)


def process_line(line, xml_doc):
    modified = True
    while modified:
        modified = False
        line, mod = replace_odkaz(line, xml_doc)
        modified = modified or mod
        line, mod = replace_odkazo(line, xml_doc)
        modified = modified or mod

    return line


def replace_odkaz(line, xml_doc):
    return replace_tag(line, xml_doc, 'odkaz', 'defpozn', 'f')


def replace_odkazo(line, xml_doc):
    return replace_tag(line, xml_doc, 'odkazo', 'defpozno', 'fo')


def replace_tag(line, xml_doc, tag, def_tag, tag_suffix):
    pattern = f'<{tag} n="([^"]+)"/>'
    match = re.search(pattern, line)

    if match:
        odkaz = match.group(1)
        new_text = get_def_text(xml_doc, def_tag, odkaz)
        if new_text:
            start_index = match.start()
            end_index = match.end()
            line = replace_text_with_tags(line, start_index, end_index, new_text, tag_suffix)
            return line, True

    return line, False


def get_def_text(xml_doc, def_tag, odkaz):
    node = xml_doc.find(f".//{def_tag}[@n='{odkaz}']")
    return ET.tostring(node, encoding='unicode', method='xml') if node is not None else None


def replace_text_with_tags(line, start_index, end_index, new_text, tag):
    sample = line[start_index:end_index]
    modified = line.replace(sample, new_text)
    modified = modified[:start_index] + f'/{tag}' + new_text + f'/{tag}*' + modified[start_index + len(new_text) + 2:]
    return modified


if __name__ == "__main__":
    main()







