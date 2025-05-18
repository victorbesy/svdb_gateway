import argparse
import os
import sqlite3
import xml.etree.ElementTree as ET
from pathlib import Path

SCHEMA_FILE = os.path.join(os.path.dirname(__file__), 'schema.txt')

# Helper functions to parse XML files

def parse_design(root):
    return {
        'vendor': root.findtext('.//{*}vendor'),
        'library': root.findtext('.//{*}library'),
        'name': root.findtext('.//{*}name'),
        'version': root.findtext('.//{*}version'),
    }

def parse_component(root):
    return {
        'vendor': root.findtext('.//{*}vendor'),
        'library': root.findtext('.//{*}library'),
        'name': root.findtext('.//{*}name'),
        'version': root.findtext('.//{*}version'),
    }

def parse_memory_maps(root):
    return root.findall('.//{*}memoryMap')

def parse_address_blocks(memory_map):
    return memory_map.findall('.//{*}addressBlock')

def parse_registers(address_block):
    return address_block.findall('.//{*}register')

def parse_fields(register):
    return register.findall('.//{*}field')

def parse_component_instances(root):
    return root.findall('.//{*}componentInstance')

def parse_interconnections(root):
    return root.findall('.//{*}interconnection')

def parse_active_interfaces(interconnection):
    return interconnection.findall('.//{*}activeInterface')

def parse_system_memory_map(root):
    return root.findall('.//{*}memoryMap')

def parse_system_address_blocks(memory_map):
    return memory_map.findall('.//{*}addressBlock')

# Main function to process XML and populate DB
def process_xml_files(xml_files, db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    # Load schema, but use CREATE TABLE IF NOT EXISTS
    with open(SCHEMA_FILE, 'r') as f:
        schema = f.read().replace('CREATE TABLE ', 'CREATE TABLE IF NOT EXISTS ')
        cur.executescript(schema)
    conn.commit()

    # ID counters for tables
    ids = {k: 1 for k in [
        'design', 'component', 'memory_map', 'address_block', 'register', 'field',
        'component_instance', 'interconnection', 'active_interface',
        'system_memory_map', 'system_address_block']}

    for xml_file in xml_files:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        tag = root.tag.lower()
        if 'design' in tag:
            # Insert into design
            d = parse_design(root)
            cur.execute('INSERT INTO design (design_id, vendor, library, name, version) VALUES (?, ?, ?, ?, ?)',
                        (ids['design'], d['vendor'], d['library'], d['name'], d['version']))
            design_id = ids['design']
            ids['design'] += 1
            # Component instances
            for ci in parse_component_instances(root):
                cref = ci.find('.//{*}componentRef')
                cur.execute('INSERT INTO component_instance (instance_id, design_id, instance_name, ref_vendor, ref_library, ref_name, ref_version) VALUES (?, ?, ?, ?, ?, ?, ?)',
                    (ids['component_instance'], design_id, ci.findtext('.//{*}instanceName'),
                     cref.get('vendor'), cref.get('library'), cref.get('name'), cref.get('version')))
                ids['component_instance'] += 1
            # Interconnections
            for iconn in parse_interconnections(root):
                cur.execute('INSERT INTO interconnection (interconnection_id, design_id, name) VALUES (?, ?, ?)',
                    (ids['interconnection'], design_id, iconn.findtext('.//{*}name')))
                interconnection_id = ids['interconnection']
                ids['interconnection'] += 1
                for ai in parse_active_interfaces(iconn):
                    cur.execute('INSERT INTO active_interface (active_interface_id, interconnection_id, component_ref, bus_ref) VALUES (?, ?, ?, ?)',
                        (ids['active_interface'], interconnection_id, ai.get('componentRef'), ai.get('busRef')))
                    ids['active_interface'] += 1
        elif 'component' in tag:
            # Insert into component
            c = parse_component(root)
            cur.execute('INSERT INTO component (component_id, vendor, library, name, version) VALUES (?, ?, ?, ?, ?)',
                        (ids['component'], c['vendor'], c['library'], c['name'], c['version']))
            component_id = ids['component']
            ids['component'] += 1
            # Memory maps
            for mm in parse_memory_maps(root):
                cur.execute('INSERT INTO memory_map (memory_map_id, component_id, name) VALUES (?, ?, ?)',
                            (ids['memory_map'], component_id, mm.findtext('.//{*}name')))
                memory_map_id = ids['memory_map']
                ids['memory_map'] += 1
                for ab in parse_address_blocks(mm):
                    cur.execute('INSERT INTO address_block (address_block_id, memory_map_id, name, base_address, range, width) VALUES (?, ?, ?, ?, ?, ?)',
                        (ids['address_block'], memory_map_id, ab.findtext('.//{*}name'), ab.findtext('.//{*}baseAddress'), ab.findtext('.//{*}range'), ab.findtext('.//{*}width')))
                    address_block_id = ids['address_block']
                    ids['address_block'] += 1
                    for reg in parse_registers(ab):
                        cur.execute('INSERT INTO register (register_id, address_block_id, name, address_offset, size, access) VALUES (?, ?, ?, ?, ?, ?)',
                            (ids['register'], address_block_id, reg.findtext('.//{*}name'), reg.findtext('.//{*}addressOffset'), reg.findtext('.//{*}size'), reg.findtext('.//{*}access')))
                        register_id = ids['register']
                        ids['register'] += 1
                        for field in parse_fields(reg):
                            cur.execute('INSERT INTO field (field_id, register_id, name, bit_offset, bit_width, access) VALUES (?, ?, ?, ?, ?, ?)',
                                (ids['field'], register_id, field.findtext('.//{*}name'), field.findtext('.//{*}bitOffset'), field.findtext('.//{*}bitWidth'), field.findtext('.//{*}access')))
                            ids['field'] += 1
        elif 'memorymaps' in tag:
            # System memory map
            for mm in parse_system_memory_map(root):
                cur.execute('INSERT INTO system_memory_map (system_memory_map_id, name) VALUES (?, ?)',
                            (ids['system_memory_map'], mm.findtext('.//{*}name')))
                system_memory_map_id = ids['system_memory_map']
                ids['system_memory_map'] += 1
                for ab in parse_system_address_blocks(mm):
                    cur.execute('INSERT INTO system_address_block (system_address_block_id, system_memory_map_id, name, base_address, range, width) VALUES (?, ?, ?, ?, ?, ?)',
                        (ids['system_address_block'], system_memory_map_id, ab.findtext('.//{*}name'), ab.findtext('.//{*}baseAddress'), ab.findtext('.//{*}range'), ab.findtext('.//{*}width')))
                    ids['system_address_block'] += 1
        # else: skip unknown root
        conn.commit()
    conn.close()


def main():
    parser = argparse.ArgumentParser(description='Parse IP-XACT XML files and generate an SQLite database.')
    parser.add_argument('xml_files', nargs='+', help='List of XML files to process, or a .txt file containing the list')
    parser.add_argument('-o', '--output_dir', default='.', help='Output directory for the SQLite database')
    args = parser.parse_args()

    # Support file list if first argument ends with .txt
    if len(args.xml_files) == 1 and args.xml_files[0].endswith('.txt'):
        with open(args.xml_files[0], 'r') as f:
            xml_files = [line.strip() for line in f if line.strip()]
    else:
        xml_files = args.xml_files

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    db_path = output_dir / 'ipxact.db'
    process_xml_files(xml_files, str(db_path))
    print(f"Database created at {db_path}")

if __name__ == '__main__':
    main()