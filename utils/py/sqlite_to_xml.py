import argparse
import os
import sqlite3
from pathlib import Path
import xml.etree.ElementTree as ET
import xml.dom.minidom
import re

IPXACT_NS = "http://www.accellera.org/XMLSchema/IPXACT/1685-2014"
XSI_NS = "http://www.w3.org/2001/XMLSchema-instance"
SCHEMA_LOC = "http://www.accellera.org/XMLSchema/IPXACT/1685-2014 http://www.accellera.org/XMLSchema/IPXACT/1685-2014/index.xsd"

# Helper functions to reconstruct XML from DB rows

def fetchall_dict(cur, query, params=()):
    cur.execute(query, params)
    columns = [desc[0] for desc in cur.description]
    return [dict(zip(columns, row)) for row in cur.fetchall()]

# Helper to create root with all required namespaces and schemaLocation

def make_root(tag):
    attrib = {
        'xmlns:ipxact': IPXACT_NS,
        'xmlns:xsi': XSI_NS,
        'xsi:schemaLocation': SCHEMA_LOC
    }
    return ET.Element(tag, attrib)

# Pretty-print helper

def indent(elem, level=0):
    i = "\n" + level * "    "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "    "
        for e in elem:
            indent(e, level + 1)
        if not e.tail or not e.tail.strip():
            e.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

def build_design_xml(cur, design_id):
    d = fetchall_dict(cur, 'SELECT * FROM design WHERE design_id=?', (design_id,))[0]
    design = make_root('ipxact:design')
    for tag in ['vendor', 'library', 'name', 'version']:
        ET.SubElement(design, f'ipxact:{tag}').text = d[tag]
    # Component Instances
    cis = fetchall_dict(cur, 'SELECT * FROM component_instance WHERE design_id=?', (design_id,))
    if cis:
        ci_parent = ET.SubElement(design, 'ipxact:componentInstances')
        for ci in cis:
            ci_elem = ET.SubElement(ci_parent, 'ipxact:componentInstance')
            ET.SubElement(ci_elem, 'ipxact:instanceName').text = ci['instance_name']
            cref = ET.SubElement(ci_elem, 'ipxact:componentRef')
            cref.set('vendor', ci['ref_vendor'])
            cref.set('library', ci['ref_library'])
            cref.set('name', ci['ref_name'])
            cref.set('version', ci['ref_version'])
    # Interconnections
    icons = fetchall_dict(cur, 'SELECT * FROM interconnection WHERE design_id=?', (design_id,))
    if icons:
        icon_parent = ET.SubElement(design, 'ipxact:interconnections')
        for icon in icons:
            icon_elem = ET.SubElement(icon_parent, 'ipxact:interconnection')
            ET.SubElement(icon_elem, 'ipxact:name').text = icon['name']
            ais = fetchall_dict(cur, 'SELECT * FROM active_interface WHERE interconnection_id=?', (icon['interconnection_id'],))
            for ai in ais:
                ai_elem = ET.SubElement(icon_elem, 'ipxact:activeInterface')
                ai_elem.set('componentRef', ai['component_ref'])
                ai_elem.set('busRef', ai['bus_ref'])
    return design

def build_component_xml(cur, component_id):
    c = fetchall_dict(cur, 'SELECT * FROM component WHERE component_id=?', (component_id,))[0]
    comp = make_root('ipxact:component')
    for tag in ['vendor', 'library', 'name', 'version']:
        ET.SubElement(comp, f'ipxact:{tag}').text = c[tag]
    # Memory Maps
    mms = fetchall_dict(cur, 'SELECT * FROM memory_map WHERE component_id=?', (component_id,))
    if mms:
        mm_parent = ET.SubElement(comp, 'ipxact:memoryMaps')
        for mm in mms:
            mm_elem = ET.SubElement(mm_parent, 'ipxact:memoryMap')
            ET.SubElement(mm_elem, 'ipxact:name').text = mm['name']
            abs = fetchall_dict(cur, 'SELECT * FROM address_block WHERE memory_map_id=?', (mm['memory_map_id'],))
            for ab in abs:
                ab_elem = ET.SubElement(mm_elem, 'ipxact:addressBlock')
                ET.SubElement(ab_elem, 'ipxact:name').text = ab['name']
                ET.SubElement(ab_elem, 'ipxact:baseAddress').text = ab['base_address']
                ET.SubElement(ab_elem, 'ipxact:range').text = ab['range']
                ET.SubElement(ab_elem, 'ipxact:width').text = str(ab['width'])
                regs = fetchall_dict(cur, 'SELECT * FROM register WHERE address_block_id=?', (ab['address_block_id'],))
                for reg in regs:
                    reg_elem = ET.SubElement(ab_elem, 'ipxact:register')
                    ET.SubElement(reg_elem, 'ipxact:name').text = reg['name']
                    ET.SubElement(reg_elem, 'ipxact:addressOffset').text = reg['address_offset']
                    ET.SubElement(reg_elem, 'ipxact:size').text = str(reg['size'])
                    ET.SubElement(reg_elem, 'ipxact:access').text = reg['access']
                    fields = fetchall_dict(cur, 'SELECT * FROM field WHERE register_id=?', (reg['register_id'],))
                    for field in fields:
                        field_elem = ET.SubElement(reg_elem, 'ipxact:field')
                        ET.SubElement(field_elem, 'ipxact:name').text = field['name']
                        ET.SubElement(field_elem, 'ipxact:bitOffset').text = str(field['bit_offset'])
                        ET.SubElement(field_elem, 'ipxact:bitWidth').text = str(field['bit_width'])
                        ET.SubElement(field_elem, 'ipxact:access').text = field['access']
    return comp

def build_system_memory_map_xml(cur, system_memory_map_id):
    mm = fetchall_dict(cur, 'SELECT * FROM system_memory_map WHERE system_memory_map_id=?', (system_memory_map_id,))[0]
    root = make_root('ipxact:memoryMaps')
    mm_elem = ET.SubElement(root, 'ipxact:memoryMap')
    ET.SubElement(mm_elem, 'ipxact:name').text = mm['name']
    abs = fetchall_dict(cur, 'SELECT * FROM system_address_block WHERE system_memory_map_id=?', (system_memory_map_id,))
    for ab in abs:
        ab_elem = ET.SubElement(mm_elem, 'ipxact:addressBlock')
        ET.SubElement(ab_elem, 'ipxact:name').text = ab['name']
        ET.SubElement(ab_elem, 'ipxact:baseAddress').text = ab['base_address']
        ET.SubElement(ab_elem, 'ipxact:range').text = ab['range']
        ET.SubElement(ab_elem, 'ipxact:width').text = str(ab['width'])
    return root

# Main function
def main():
    parser = argparse.ArgumentParser(description='Convert SQLite DB to XML files.')
    parser.add_argument('input_db', help='Input SQLite database file')
    parser.add_argument('output_dir', help='Output directory for XML files')
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(args.input_db)
    cur = conn.cursor()

    # Design files
    for d in fetchall_dict(cur, 'SELECT * FROM design'):
        xml_elem = build_design_xml(cur, d['design_id'])
        xml_str = ET.tostring(xml_elem, encoding='utf-8')
        pretty_xml = xml.dom.minidom.parseString(xml_str.decode('utf-8')).toprettyxml(indent='    ')
        lines = pretty_xml.splitlines()
        if lines and lines[1].startswith('<ipxact:'):
            lines[1] = re.sub(r' (xmlns:xsi=)', r'\n    \1', lines[1])
            lines[1] = re.sub(r' (xsi:schemaLocation=)', r'\n    \1', lines[1])
            pretty_xml = '\n'.join(lines)
        pretty_xml = re.sub(r'\n+', '\n', pretty_xml)
        if pretty_xml.startswith('<?xml version="1.0" ?>'):
            pretty_xml = pretty_xml.replace('<?xml version="1.0" ?>', '<?xml version="1.0" encoding="UTF-8"?>', 1)
        out_path = output_dir / f"{d['name']}.xml"
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(pretty_xml)

    # Component files
    for c in fetchall_dict(cur, 'SELECT * FROM component'):
        xml_elem = build_component_xml(cur, c['component_id'])
        xml_str = ET.tostring(xml_elem, encoding='utf-8')
        pretty_xml = xml.dom.minidom.parseString(xml_str.decode('utf-8')).toprettyxml(indent='    ')
        lines = pretty_xml.splitlines()
        if lines and lines[1].startswith('<ipxact:'):
            lines[1] = re.sub(r' (xmlns:xsi=)', r'\n    \1', lines[1])
            lines[1] = re.sub(r' (xsi:schemaLocation=)', r'\n    \1', lines[1])
            pretty_xml = '\n'.join(lines)
        pretty_xml = re.sub(r'\n+', '\n', pretty_xml)
        if pretty_xml.startswith('<?xml version="1.0" ?>'):
            pretty_xml = pretty_xml.replace('<?xml version="1.0" ?>', '<?xml version="1.0" encoding="UTF-8"?>', 1)
        out_path = output_dir / f"{c['name']}.xml"
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(pretty_xml)

    # System memory map files
    for mm in fetchall_dict(cur, 'SELECT * FROM system_memory_map'):
        xml_elem = build_system_memory_map_xml(cur, mm['system_memory_map_id'])
        xml_str = ET.tostring(xml_elem, encoding='utf-8')
        pretty_xml = xml.dom.minidom.parseString(xml_str.decode('utf-8')).toprettyxml(indent='    ')
        lines = pretty_xml.splitlines()
        if lines and lines[1].startswith('<ipxact:'):
            lines[1] = re.sub(r' (xmlns:xsi=)', r'\n    \1', lines[1])
            lines[1] = re.sub(r' (xsi:schemaLocation=)', r'\n    \1', lines[1])
            pretty_xml = '\n'.join(lines)
        pretty_xml = re.sub(r'\n+', '\n', pretty_xml)
        if pretty_xml.startswith('<?xml version="1.0" ?>'):
            pretty_xml = pretty_xml.replace('<?xml version="1.0" ?>', '<?xml version="1.0" encoding="UTF-8"?>', 1)
        out_path = output_dir / f"{mm['name']}.xml"
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(pretty_xml)

    print(f"XML files written to {output_dir}")

if __name__ == '__main__':
    main()