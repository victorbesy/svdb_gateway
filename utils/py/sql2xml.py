#!/usr/bin/env python3

import sys
import os
import argparse
import sqlite3
from pathlib import Path
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import json
from typing import Dict

def setup_argument_parser():
    parser = argparse.ArgumentParser(
        description='Convert SQLite database back to IP-XACT XML file'
    )
    parser.add_argument(
        '-i', '--input',
        help='Input SQLite database path',
        required=True,
        type=str
    )
    parser.add_argument(
        '-o', '--output',
        help='Output XML file path (defaults to input filename with .xml extension)',
        type=str,
        default=None
    )
    return parser

def validate_input_file(file_path: str):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input database not found: {file_path}")
    if not file_path.lower().endswith('.db'):
        raise ValueError(f"Input file must be a SQLite database: {file_path}")

def get_output_path(args) -> Path:
    input_file = Path(args.input)
    if args.output:
        return Path(args.output)
    return input_file.with_suffix('.xml')

def fetch_header_info(db_path: str) -> Dict[str, str]:
    """Fetch IP-XACT header information from database."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM ipxact_header ORDER BY id DESC LIMIT 1')
        row = cursor.fetchone()

        if not row:
            raise ValueError("No header information found in database")

        header = {
            'xml_version': row[1],
            'xml_encoding': row[2],
            'schema_version': row[3],
            'vendor': row[4],
            'library': row[5],
            'name': row[6],
            'version': row[7],
            'description': row[8],
            'created_date': row[9]
        }

        conn.close()
        return header
    except sqlite3.Error as e:
        raise Exception(f"Database error: {e}")

def fetch_register_info(db_path: str) -> list:
    """Fetch register information from database."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT memory_map_name, memory_map_description,
                   block_name, block_base_address, block_range, block_width, block_usage,
                   register_name, register_offset, register_size, register_description,
                   register_access, register_reset_value, register_reset_mask,
                   register_fields, hdl_path, register_read_action
            FROM registers
            ORDER BY register_offset
        ''')
        rows = cursor.fetchall()

        if not rows:
            print("Warning: No register information found in database")
            return []

        registers = []
        for row in rows:
            register = {
                'memory_map_name': row[0],
                'memory_map_description': row[1],
                'block_name': row[2],
                'block_base_address': row[3],
                'block_range': row[4],
                'block_width': row[5],
                'block_usage': row[6],
                'register_name': row[7],
                'register_offset': row[8],
                'register_size': row[9],
                'register_description': row[10],
                'register_access': row[11],
                'register_reset_value': row[12],
                'register_reset_mask': row[13],
                'register_fields': row[14],  # JSON string
                'hdl_path': row[15],
                'register_read_action': row[16]
            }
            registers.append(register)

        conn.close()
        return registers
    except sqlite3.Error as e:
        raise Exception(f"Database error: {e}")

def create_xml_tree(header_info: Dict[str, str], registers_info: list) -> ET.Element:
    """Create XML tree from header and register information."""
    # Create root element with namespace
    ns = header_info['schema_version']
    ET.register_namespace('ipxact', ns)
    root = ET.Element(f'{{{ns}}}component')

    # Add header elements
    vendor = ET.SubElement(root, f'{{{ns}}}vendor')
    vendor.text = header_info['vendor']

    library = ET.SubElement(root, f'{{{ns}}}library')
    library.text = header_info['library']

    name = ET.SubElement(root, f'{{{ns}}}name')
    name.text = header_info['name']

    version = ET.SubElement(root, f'{{{ns}}}version')
    version.text = header_info['version']

    if header_info['description']:
        description = ET.SubElement(root, f'{{{ns}}}description')
        description.text = header_info['description']

    # Add memory maps section
    if registers_info:
        memory_maps = ET.SubElement(root, f'{{{ns}}}memoryMaps')
        current_map = None
        current_block = None

        for reg in registers_info:
            # Create memory map if it's new
            if current_map is None or current_map.find(f'{{{ns}}}name').text != reg['memory_map_name']:
                current_map = ET.SubElement(memory_maps, f'{{{ns}}}memoryMap')
                map_name = ET.SubElement(current_map, f'{{{ns}}}name')
                map_name.text = reg['memory_map_name']
                if reg['memory_map_description']:
                    map_desc = ET.SubElement(current_map, f'{{{ns}}}description')
                    map_desc.text = reg['memory_map_description']
                current_block = None

            # Create address block if it's new
            if current_block is None or current_block.find(f'{{{ns}}}name').text != reg['block_name']:
                current_block = ET.SubElement(current_map, f'{{{ns}}}addressBlock')
                block_name = ET.SubElement(current_block, f'{{{ns}}}name')
                block_name.text = reg['block_name']
                base_addr = ET.SubElement(current_block, f'{{{ns}}}baseAddress')
                base_addr.text = reg['block_base_address']
                range_elem = ET.SubElement(current_block, f'{{{ns}}}range')
                range_elem.text = reg['block_range']
                width = ET.SubElement(current_block, f'{{{ns}}}width')
                width.text = str(reg['block_width'])
                usage = ET.SubElement(current_block, f'{{{ns}}}usage')
                usage.text = reg['block_usage']

            # Create register
            register = ET.SubElement(current_block, f'{{{ns}}}register')
            reg_name = ET.SubElement(register, f'{{{ns}}}name')
            reg_name.text = reg['register_name']

            if reg['register_description']:
                reg_desc = ET.SubElement(register, f'{{{ns}}}description')
                reg_desc.text = reg['register_description']

            reg_offset = ET.SubElement(register, f'{{{ns}}}addressOffset')
            reg_offset.text = reg['register_offset']

            reg_size = ET.SubElement(register, f'{{{ns}}}size')
            reg_size.text = str(reg['register_size'])

            if reg['register_access']:
                reg_access = ET.SubElement(register, f'{{{ns}}}access')
                reg_access.text = reg['register_access']

            # Add readAction before reset block if present
            if reg.get('register_read_action') and reg['register_read_action'] != 'N/A':
                read_action = ET.SubElement(register, f'{{{ns}}}readAction')
                read_action.text = reg['register_read_action']

            # Add reset value and mask if present
            if reg['register_reset_value'] or reg['register_reset_mask']:
                reset = ET.SubElement(register, f'{{{ns}}}reset')
                if reg['register_reset_value']:
                    reset_val = ET.SubElement(reset, f'{{{ns}}}value')
                    reset_val.text = reg['register_reset_value']
                if reg['register_reset_mask']:
                    reset_mask = ET.SubElement(reset, f'{{{ns}}}mask')
                    reset_mask.text = reg['register_reset_mask']

            # Add fields section if present
            if reg['register_fields'] and reg['register_fields'] != 'null':
                try:
                    fields_data = json.loads(reg['register_fields'])
                    if fields_data:
                        fields_elem = ET.SubElement(register, f'{{{ns}}}fields')
                        for field_info in fields_data:
                            field = ET.SubElement(fields_elem, f'{{{ns}}}field')

                            # Add field name
                            field_name = ET.SubElement(field, f'{{{ns}}}name')
                            field_name.text = field_info.get('name', 'unnamed_field')

                            # Add field description if present
                            if field_info.get('description'):
                                field_desc = ET.SubElement(field, f'{{{ns}}}description')
                                field_desc.text = field_info['description']

                            # Add bit offset
                            bit_offset = ET.SubElement(field, f'{{{ns}}}bitOffset')
                            bit_offset.text = field_info.get('bit_offset', '0')

                            # Add bit width
                            bit_width = ET.SubElement(field, f'{{{ns}}}bitWidth')
                            bit_width.text = field_info.get('bit_width', '1')

                            # Add access if present
                            if field_info.get('access'):
                                access = ET.SubElement(field, f'{{{ns}}}access')
                                access.text = field_info['access']

                            # Add all child elements in the same order as stored in the database
                            for element in field_info.get('elements', []):
                                # Skip elements that have already been added explicitly
                                if element['type'] in ['name', 'description', 'bitOffset', 'bitWidth', 'access']:
                                    continue
                                if element['type'] == 'writeValueConstraint':
                                    write_value_constraint = ET.SubElement(field, f'{{{ns}}}writeValueConstraint')
                                    min_val = ET.SubElement(write_value_constraint, f'{{{ns}}}minimum')
                                    min_val.text = element['minimum']
                                    max_val = ET.SubElement(write_value_constraint, f'{{{ns}}}maximum')
                                    max_val.text = element['maximum']
                                elif element['type'] == 'modifiedWriteValue':
                                    modified_write_value = ET.SubElement(field, f'{{{ns}}}modifiedWriteValue')
                                    modified_write_value.text = element['value']
                                elif element['type'] == 'reset':
                                    reset = ET.SubElement(field, f'{{{ns}}}reset')
                                    reset_val = ET.SubElement(reset, f'{{{ns}}}value')
                                    reset_val.text = element['value']
                                elif element['type'] == 'readAction':  # Add readAction for fields
                                    read_action = ET.SubElement(field, f'{{{ns}}}readAction')
                                    read_action.text = element['value']
                                else:
                                    custom_elem = ET.SubElement(field, f'{{{ns}}}{element["type"]}')
                                    custom_elem.text = element['value']
                except json.JSONDecodeError as e:
                    print(f"Warning: Failed to parse fields JSON for register {reg['register_name']}: {e}")
                except Exception as e:
                    print(f"Warning: Error processing fields for register {reg['register_name']}: {e}")

            # Add HDL path if present (moved to end of register definition)
            if reg['hdl_path'] and reg['hdl_path'] != 'N/A':
                vendor_extensions = ET.SubElement(register, f'{{{ns}}}vendorExtensions')
                hdl_path = ET.SubElement(vendor_extensions, f'{{{ns}}}hdlPath')
                hdl_path.text = reg['hdl_path']

    return root

def write_xml_file(root: ET.Element, header_info: Dict[str, str], output_path: Path):
    """Write XML tree to file with proper formatting."""
    # Register namespace
    ET.register_namespace('ipxact', header_info['schema_version'])

    # Convert to string with initial formatting
    xml_str = ET.tostring(root, encoding='unicode')

    # Use minidom for pretty printing
    dom = minidom.parseString(xml_str)
    pretty_xml = dom.toprettyxml(indent='    ')

    # Remove the XML declaration that minidom adds
    pretty_xml = '\n'.join(line for line in pretty_xml.split('\n') if not line.startswith('<?xml'))

    # Add our own XML declaration with proper encoding
    xml_declaration = f'<?xml version="{header_info["xml_version"]}" encoding="{header_info["xml_encoding"]}"?>\n'

    # Add extra newlines after specific sections
    pretty_xml = pretty_xml.replace('</ipxact:version>\n', '</ipxact:version>\n\n')
    pretty_xml = pretty_xml.replace('</ipxact:description>\n', '</ipxact:description>\n\n')
    pretty_xml = pretty_xml.replace('</ipxact:register>\n', '</ipxact:register>\n\n')
    pretty_xml = pretty_xml.replace('</ipxact:addressBlock>\n', '</ipxact:addressBlock>\n\n')
    pretty_xml = pretty_xml.replace('</ipxact:memoryMap>\n', '</ipxact:memoryMap>\n\n')

    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(xml_declaration)
        f.write(pretty_xml)

def main():
    try:
        parser = setup_argument_parser()
        args = parser.parse_args()

        # Validate input database
        validate_input_file(args.input)

        # Get output path
        output_path = get_output_path(args)

        print(f"Input database: {args.input}")
        print(f"Output XML: {output_path}")

        # Fetch header information from database
        header_info = fetch_header_info(args.input)

        # Fetch register information from database
        registers_info = fetch_register_info(args.input)

        # Create XML tree
        root = create_xml_tree(header_info, registers_info)

        # Write formatted XML to file with proper XML declaration
        write_xml_file(root, header_info, output_path)

        print(f"Successfully created XML file with {len(registers_info)} registers: {output_path}")

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
