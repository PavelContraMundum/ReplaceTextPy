import re
import xml.etree.ElementTree as ET
import time
import os

def process_file(input_file_path, output_file_path):
    start_writing = False
    output = []

    tree = ET.parse(input_file_path)
    root = tree.getroot()

    with open(input_file_path, 'r', encoding='utf-8') as reader:
        for line in reader:
            if not start_writing and "<titulek>" in line:
                start_writing = True

            if start_writing:
                line = process_line(line, root)
                output.append(line)

    final_output = ''.join(output).rstrip()
    last_book_tag_index = final_output.rfind("</kniha>")
    if last_book_tag_index != -1:
        final_output = final_output[:last_book_tag_index]

    if not final_output.strip():
        print("Warning: No content was processed. The output file will be empty.")
    else:
        try:
            with open(output_file_path, 'w', encoding='utf-8') as writer:
                writer.write(final_output)

            print("Waiting for 5 seconds...")
            time.sleep(5)

            if os.path.exists(output_file_path):
                with open(output_file_path, 'r', encoding='utf-8') as f:
                    content_after_wait = f.read()
                print(f"File content after 5 seconds: {content_after_wait[:100]}")

            print(f"Attempting to write {len(final_output)} characters to file.")

            if os.path.exists(output_file_path):
                file_size = os.path.getsize(output_file_path)
                print(f"File created. File size: {file_size} bytes")

                if file_size > 0:
                    print(f"Output successfully written to: {output_file_path}")
                    print(f"Final content length: {len(final_output)} characters")

                    with open(output_file_path, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                    print(f"First 100 characters of file content: {file_content[:100]}")
                else:
                    print("Warning: File was created but is empty.")
            else:
                print("Error: File was not created.")
        except Exception as ex:
            print(f"Error writing to file: {str(ex)}")
            print(f"Stack trace: {traceback.format_exc()}")

def process_line(line, root):
    modified = True
    while modified:
        line, modified = replace_odkaz(line, root)
        if not modified:
            line, modified = replace_odkazo(line, root)
    return line

def replace_odkaz(line, root):
    return replace_tag(line, root, "<odkaz n=\"", "defpozn", "\\f")

def replace_odkazo(line, root):
    return replace_tag(line, root, "<odkazo n=\"", "defpozno", "\\fo")

def replace_tag(line, root, start_tag, xml_tag, replace_tag):
    start_index = line.find(start_tag)
    if start_index != -1:
        end_index = find_end_index(line, start_index)
        if end_index != -1:
            odkaz = extract_odkaz_value(line, start_index)
            if odkaz:
                new_text = get_defpozn_text(root, odkaz, xml_tag)
                if new_text:
                    line = replace_text_with_tags(line, start_index, end_index, new_text, replace_tag)
                    return line, True
    return line, False

def find_end_index(line, start_index):
    match = re.search('"/>', line[start_index:])
    return start_index + match.end() if match else -1

def extract_odkaz_value(line, start_index):
    start_quote = line.index('"', start_index) + 1
    end_quote = line.index('"', start_quote)
    return line[start_quote:end_quote] if end_quote > start_quote else None

def get_defpozn_text(root, odkaz, tag):
    for elem in root.iter(tag):
        if elem.get('n') == odkaz:
            return ''.join(elem.itertext())
    return None

def replace_text_with_tags(line, start_index, end_index, new_text, tag):
    sample = line[start_index:end_index]
    return line.replace(sample, f"{tag}{new_text}{tag}*")

if __name__ == "__main__":
    input_file_path = "D:\\Downloads\\Studijni Bible\\Studijni_Bible\\GenMod.xml"
    output_file_path = "D:\\Downloads\\GenModified.txt"

    try:
        process_file(input_file_path, output_file_path)
    except Exception as ex:
        print(f"An error occurred: {str(ex)}")