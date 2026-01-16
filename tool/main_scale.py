import xml.etree.ElementTree as ET

def extract_font_sizes(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    font_sizes = {}
    for node in root.iter('node'):
        resource_id = node.attrib.get('resource-id', '')
        text_size = node.attrib.get('textSize')
        if resource_id and text_size:
            font_sizes[resource_id] = float(text_size)
    return font_sizes

before = extract_font_sizes('dump_before.xml')
after = extract_font_sizes('dump_after.xml')

for res_id in before:
    if res_id in after:
        before_size = before[res_id]
        after_size = after[res_id]
        if before_size != after_size:
            print(f"{res_id}: font size changed from {before_size} to {after_size}")
        else:
            print(f"{res_id}: font size unchanged ({before_size})")
    else:
        print(f"{res_id}: not found in after dump")
