import pytest
import sqlite3
import os
from pathlib import Path
from xml2sql import (
    setup_argument_parser, 
    validate_input_file, 
    get_database_path,
    get_xml_version,
    parse_ipxact_header,
    create_database,
    parse_register_info,
    create_register_table
)
import unittest
import json
from datetime import datetime

@pytest.fixture
def temp_xml_file(tmp_path):
    """Create a temporary XML file for testing."""
    xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<ipxact:component xmlns:ipxact="http://www.accellera.org/XMLSchema/IPXACT/1685-2014">
    <ipxact:vendor>example.com</ipxact:vendor>
    <ipxact:library>test_lib</ipxact:library>
    <ipxact:name>test_component</ipxact:name>
    <ipxact:version>1.0</ipxact:version>
    <ipxact:description>Test description</ipxact:description>
</ipxact:component>'''
    xml_file = tmp_path / "test_registers.xml"
    xml_file.write_text(xml_content)
    return xml_file

def test_parser_required_input():
    """Test that parser requires input argument."""
    parser = setup_argument_parser()
    with pytest.raises(SystemExit):
        parser.parse_args([])

def test_parser_with_input(temp_xml_file):
    """Test parser with only input file."""
    parser = setup_argument_parser()
    args = parser.parse_args(['-i', str(temp_xml_file)])
    assert args.input == str(temp_xml_file)
    assert args.database == os.getcwd()

def test_parser_with_input_and_database(temp_xml_file, tmp_path):
    """Test parser with both input and database arguments."""
    parser = setup_argument_parser()
    args = parser.parse_args(['-i', str(temp_xml_file), '-d', str(tmp_path)])
    assert args.input == str(temp_xml_file)
    assert args.database == str(tmp_path)

def test_validate_input_file_exists(temp_xml_file):
    """Test validation of existing XML file."""
    validate_input_file(str(temp_xml_file))

def test_validate_input_file_not_exists():
    """Test validation of non-existing file."""
    with pytest.raises(FileNotFoundError):
        validate_input_file('nonexistent.xml')

def test_validate_input_file_wrong_extension(tmp_path):
    """Test validation of file with wrong extension."""
    wrong_file = tmp_path / "test.txt"
    wrong_file.write_text("content")
    with pytest.raises(ValueError):
        validate_input_file(str(wrong_file))

def test_get_database_path_directory(temp_xml_file, tmp_path):
    """Test database path generation when directory is provided."""
    class Args:
        def __init__(self, input_path, db_path):
            self.input = input_path
            self.database = db_path

    args = Args(str(temp_xml_file), str(tmp_path))
    db_path = get_database_path(args)
    expected_path = tmp_path / "test_registers.db"
    assert db_path == expected_path

def test_get_database_path_full_path(temp_xml_file, tmp_path):
    """Test database path when full path is provided."""
    db_file = tmp_path / "custom.db"
    class Args:
        def __init__(self, input_path, db_path):
            self.input = input_path
            self.database = db_path

    args = Args(str(temp_xml_file), str(db_file))
    db_path = get_database_path(args)
    assert db_path == db_file

def test_get_xml_version(temp_xml_file):
    """Test XML version extraction."""
    version_info = get_xml_version(str(temp_xml_file))
    assert version_info['version'] == '1.0'
    assert version_info['encoding'] == 'UTF-8'

def test_parse_ipxact_header(temp_xml_file):
    """Test IP-XACT header parsing."""
    header = parse_ipxact_header(str(temp_xml_file))
    assert header['xml_version'] == '1.0'
    assert header['xml_encoding'] == 'UTF-8'
    assert header['vendor'] == 'example.com'
    assert header['library'] == 'test_lib'
    assert header['name'] == 'test_component'
    assert header['version'] == '1.0'
    assert header['description'] == 'Test description'

def test_create_database(temp_xml_file, tmp_path):
    """Test database creation with header information."""
    db_path = tmp_path / "test.db"
    header = parse_ipxact_header(str(temp_xml_file))
    # Add schema_version to header dictionary
    header['schema_version'] = 'http://www.accellera.org/XMLSchema/IPXACT/1685-2014'
    
    # Create empty registers_info list since this test only checks header information
    registers_info = []
    
    conn = create_database(db_path, header, registers_info)
    
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM ipxact_header')
    row = cursor.fetchone()
    
    # Verify all header fields
    assert row[1] == '1.0'  # xml_version
    assert row[2] == 'UTF-8'  # xml_encoding
    assert row[3] == 'http://www.accellera.org/XMLSchema/IPXACT/1685-2014'  # schema_version
    assert row[4] == 'example.com'  # vendor
    assert row[5] == 'test_lib'  # library
    assert row[6] == 'test_component'  # name
    assert row[7] == '1.0'  # version
    assert row[8] == 'Test description'  # description
    
    cursor.execute('PRAGMA table_info(ipxact_header)')
    columns = cursor.fetchall()
    expected_columns = ['id', 'xml_version', 'xml_encoding', 'schema_version', 
                       'vendor', 'library', 'name', 'version', 'description']
    actual_columns = [col[1] for col in columns]
    assert all(col in actual_columns for col in expected_columns)
    
    conn.close()

class TestXml2Sql(unittest.TestCase):
    def setUp(self):
        """Set up test database"""
        self.test_db = "/tmp/test_registers.db"
        self.conn = sqlite3.connect(self.test_db)
        self.cursor = self.conn.cursor()
        create_register_table(self.cursor)
        
    def tearDown(self):
        """Clean up test database"""
        self.conn.close()
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    def test_parse_register_with_read_action(self):
        """Test parsing of register with readAction attribute"""
        test_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <ipxact:component xmlns:ipxact="http://www.accellera.org/XMLSchema/IPXACT/1685-2014">
            <ipxact:memoryMaps>
                <ipxact:memoryMap>
                    <ipxact:name>TestMap</ipxact:name>
                    <ipxact:addressBlock>
                        <ipxact:name>TestBlock</ipxact:name>
                        <ipxact:register>
                            <ipxact:name>TestReg</ipxact:name>
                            <ipxact:description>Test Register</ipxact:description>
                            <ipxact:addressOffset>0x0</ipxact:addressOffset>
                            <ipxact:size>32</ipxact:size>
                            <ipxact:readAction>clear</ipxact:readAction>
                        </ipxact:register>
                    </ipxact:addressBlock>
                </ipxact:memoryMap>
            </ipxact:memoryMaps>
        </ipxact:component>
        """
        with open("/tmp/test.xml", "w") as f:
            f.write(test_xml)
        
        registers = parse_register_info("/tmp/test.xml")
        self.assertEqual(len(registers), 1)
        reg = registers[0]
        
        # Verify readAction attribute is correctly parsed
        self.assertEqual(reg['register_read_action'], 'clear')
        self.assertEqual(reg['register_name'], 'TestReg')

    def test_parse_register_with_field_read_action(self):
        """Test parsing of register field with readAction"""
        test_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <ipxact:component xmlns:ipxact="http://www.accellera.org/XMLSchema/IPXACT/1685-2014">
            <ipxact:memoryMaps>
                <ipxact:memoryMap>
                    <ipxact:name>TestMap</ipxact:name>
                    <ipxact:addressBlock>
                        <ipxact:name>TestBlock</ipxact:name>
                        <ipxact:register>
                            <ipxact:name>TestReg</ipxact:name>
                            <ipxact:addressOffset>0x0</ipxact:addressOffset>
                            <ipxact:size>32</ipxact:size>
                            <ipxact:fields>
                                <ipxact:field>
                                    <ipxact:name>TestField</ipxact:name>
                                    <ipxact:bitOffset>0</ipxact:bitOffset>
                                    <ipxact:bitWidth>1</ipxact:bitWidth>
                                    <ipxact:readAction>clear</ipxact:readAction>
                                </ipxact:field>
                            </ipxact:fields>
                        </ipxact:register>
                    </ipxact:addressBlock>
                </ipxact:memoryMap>
            </ipxact:memoryMaps>
        </ipxact:component>
        """
        with open("/tmp/test.xml", "w") as f:
            f.write(test_xml)
        
        registers = parse_register_info("/tmp/test.xml")
        self.assertEqual(len(registers), 1)
        reg = registers[0]
        
        # Verify field readAction is stored in elements list
        fields = json.loads(reg['register_fields'])
        self.assertEqual(len(fields), 1)
        field = fields[0]
        
        # Check if readAction is in the elements list
        read_action_element = next(
            (elem for elem in field['elements'] if elem['type'] == 'readAction'),
            None
        )
        self.assertIsNotNone(read_action_element)
        self.assertEqual(read_action_element['value'], 'clear')

    def test_parse_register_without_read_action(self):
        """Test parsing of register without readAction"""
        test_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <ipxact:component xmlns:ipxact="http://www.accellera.org/XMLSchema/IPXACT/1685-2014">
            <ipxact:memoryMaps>
                <ipxact:memoryMap>
                    <ipxact:name>TestMap</ipxact:name>
                    <ipxact:addressBlock>
                        <ipxact:name>TestBlock</ipxact:name>
                        <ipxact:register>
                            <ipxact:name>TestReg</ipxact:name>
                            <ipxact:addressOffset>0x0</ipxact:addressOffset>
                            <ipxact:size>32</ipxact:size>
                        </ipxact:register>
                    </ipxact:addressBlock>
                </ipxact:memoryMap>
            </ipxact:memoryMaps>
        </ipxact:component>
        """
        with open("/tmp/test.xml", "w") as f:
            f.write(test_xml)
        
        registers = parse_register_info("/tmp/test.xml")
        self.assertEqual(len(registers), 1)
        reg = registers[0]
        
        # Verify default value for readAction
        self.assertEqual(reg['register_read_action'], 'N/A')

    def test_registers_table_fields(self):
        """Test all fields in the registers table are correctly populated"""
        test_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <ipxact:component xmlns:ipxact="http://www.accellera.org/XMLSchema/IPXACT/1685-2014">
            <ipxact:memoryMaps>
                <ipxact:memoryMap>
                    <ipxact:name>TestMap</ipxact:name>
                    <ipxact:description>Test Memory Map</ipxact:description>
                    <ipxact:addressBlock>
                        <ipxact:name>TestBlock</ipxact:name>
                        <ipxact:baseAddress>0x1000</ipxact:baseAddress>
                        <ipxact:range>0x100</ipxact:range>
                        <ipxact:width>32</ipxact:width>
                        <ipxact:usage>register</ipxact:usage>
                        <ipxact:register>
                            <ipxact:name>TestReg</ipxact:name>
                            <ipxact:description>Test Register Description</ipxact:description>
                            <ipxact:addressOffset>0x0</ipxact:addressOffset>
                            <ipxact:size>32</ipxact:size>
                            <ipxact:access>read-write</ipxact:access>
                            <ipxact:readAction>clear</ipxact:readAction>
                            <ipxact:reset>
                                <ipxact:value>0xFFFF</ipxact:value>
                                <ipxact:mask>0xFFFF</ipxact:mask>
                            </ipxact:reset>
                            <ipxact:fields>
                                <ipxact:field>
                                    <ipxact:name>TestField</ipxact:name>
                                    <ipxact:description>Test Field Description</ipxact:description>
                                    <ipxact:bitOffset>0</ipxact:bitOffset>
                                    <ipxact:bitWidth>16</ipxact:bitWidth>
                                    <ipxact:access>read-write</ipxact:access>
                                    <ipxact:readAction>clear</ipxact:readAction>
                                    <ipxact:reset>
                                        <ipxact:value>0xF</ipxact:value>
                                    </ipxact:reset>
                                </ipxact:field>
                            </ipxact:fields>
                            <ipxact:vendorExtensions>
                                <ipxact:hdlPath>top.test.register</ipxact:hdlPath>
                            </ipxact:vendorExtensions>
                        </ipxact:register>
                    </ipxact:addressBlock>
                </ipxact:memoryMap>
            </ipxact:memoryMaps>
        </ipxact:component>
        """
        with open("/tmp/test.xml", "w") as f:
            f.write(test_xml)
        
        # Parse registers and insert into database
        registers = parse_register_info("/tmp/test.xml")
        self.assertEqual(len(registers), 1)
        reg = registers[0]
        
        # Verify all register fields
        self.assertEqual(reg['memory_map_name'], 'TestMap')
        self.assertEqual(reg['memory_map_description'], 'Test Memory Map')
        self.assertEqual(reg['block_name'], 'TestBlock')
        self.assertEqual(reg['block_base_address'], '0x1000')
        self.assertEqual(reg['block_range'], '0x100')
        self.assertEqual(reg['block_width'], '32')
        self.assertEqual(reg['block_usage'], 'register')
        self.assertEqual(reg['register_name'], 'TestReg')
        self.assertEqual(reg['register_offset'], '0x0')
        self.assertEqual(reg['register_size'], '32')
        self.assertEqual(reg['register_description'], 'Test Register Description')
        self.assertEqual(reg['register_access'], 'read-write')
        self.assertEqual(reg['register_reset_value'], '0xFFFF')
        self.assertEqual(reg['register_reset_mask'], '0xFFFF')
        self.assertEqual(reg['register_read_action'], 'clear')
        self.assertEqual(reg['hdl_path'], 'top.test.register')
        
        # Verify fields JSON structure
        fields = json.loads(reg['register_fields'])
        self.assertEqual(len(fields), 1)
        field = fields[0]
        
        # Verify field attributes
        self.assertEqual(field['name'], 'TestField')
        self.assertEqual(field['description'], 'Test Field Description')
        self.assertEqual(field['bit_offset'], '0')
        self.assertEqual(field['bit_width'], '16')
        self.assertEqual(field['access'], 'read-write')
        
        # Verify field elements
        elements = field['elements']
        self.assertTrue(any(elem['type'] == 'readAction' and elem['value'] == 'clear' 
                          for elem in elements))
        self.assertTrue(any(elem['type'] == 'reset' and elem['value'] == '0xF' 
                          for elem in elements))
        
        # Verify created_date is present and in ISO format
        self.assertTrue('created_date' in reg)
        try:
            datetime.fromisoformat(reg['created_date'])
        except ValueError:
            self.fail("created_date is not in valid ISO format")

    def test_register_with_multiple_fields(self):
        """Test parsing of register containing multiple fields"""
        test_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <ipxact:component xmlns:ipxact="http://www.accellera.org/XMLSchema/IPXACT/1685-2014">
            <ipxact:memoryMaps>
                <ipxact:memoryMap>
                    <ipxact:name>TestMap</ipxact:name>
                    <ipxact:addressBlock>
                        <ipxact:name>TestBlock</ipxact:name>
                        <ipxact:register>
                            <ipxact:name>MultiFieldReg</ipxact:name>
                            <ipxact:description>Register with multiple fields</ipxact:description>
                            <ipxact:addressOffset>0x0</ipxact:addressOffset>
                            <ipxact:size>32</ipxact:size>
                            <ipxact:access>read-write</ipxact:access>
                            <ipxact:fields>
                                <ipxact:field>
                                    <ipxact:name>field0</ipxact:name>
                                    <ipxact:description>Field 0</ipxact:description>
                                    <ipxact:bitOffset>0</ipxact:bitOffset>
                                    <ipxact:bitWidth>1</ipxact:bitWidth>
                                    <ipxact:access>read-write</ipxact:access>
                                </ipxact:field>
                                <ipxact:field>
                                    <ipxact:name>field1</ipxact:name>
                                    <ipxact:description>Field 1 with read clear</ipxact:description>
                                    <ipxact:bitOffset>1</ipxact:bitOffset>
                                    <ipxact:bitWidth>2</ipxact:bitWidth>
                                    <ipxact:access>read-write</ipxact:access>
                                    <ipxact:readAction>clear</ipxact:readAction>
                                </ipxact:field>
                                <ipxact:field>
                                    <ipxact:name>field2</ipxact:name>
                                    <ipxact:description>Field 2 with modified write</ipxact:description>
                                    <ipxact:bitOffset>3</ipxact:bitOffset>
                                    <ipxact:bitWidth>4</ipxact:bitWidth>
                                    <ipxact:modifiedWriteValue>oneToClear</ipxact:modifiedWriteValue>
                                </ipxact:field>
                                <ipxact:field>
                                    <ipxact:name>field3_reserved</ipxact:name>
                                    <ipxact:bitOffset>7</ipxact:bitOffset>
                                    <ipxact:bitWidth>1</ipxact:bitWidth>
                                    <ipxact:access>read-only</ipxact:access>
                                </ipxact:field>
                                <ipxact:field>
                                    <ipxact:name>field4</ipxact:name>
                                    <ipxact:bitOffset>8</ipxact:bitOffset>
                                    <ipxact:bitWidth>4</ipxact:bitWidth>
                                    <ipxact:access>write-only</ipxact:access>
                                </ipxact:field>
                                <ipxact:field>
                                    <ipxact:name>field5</ipxact:name>
                                    <ipxact:bitOffset>12</ipxact:bitOffset>
                                    <ipxact:bitWidth>1</ipxact:bitWidth>
                                    <ipxact:writeValueConstraint>
                                        <ipxact:minimum>0</ipxact:minimum>
                                        <ipxact:maximum>1</ipxact:maximum>
                                    </ipxact:writeValueConstraint>
                                </ipxact:field>
                                <ipxact:field>
                                    <ipxact:name>field6</ipxact:name>
                                    <ipxact:bitOffset>13</ipxact:bitOffset>
                                    <ipxact:bitWidth>2</ipxact:bitWidth>
                                    <ipxact:reset>
                                        <ipxact:value>0x2</ipxact:value>
                                    </ipxact:reset>
                                </ipxact:field>
                                <ipxact:field>
                                    <ipxact:name>field7</ipxact:name>
                                    <ipxact:bitOffset>15</ipxact:bitOffset>
                                    <ipxact:bitWidth>1</ipxact:bitWidth>
                                    <ipxact:modifiedWriteValue>set</ipxact:modifiedWriteValue>
                                </ipxact:field>
                                <ipxact:field>
                                    <ipxact:name>field8</ipxact:name>
                                    <ipxact:bitOffset>16</ipxact:bitOffset>
                                    <ipxact:bitWidth>4</ipxact:bitWidth>
                                    <ipxact:readAction>set</ipxact:readAction>
                                </ipxact:field>
                                <ipxact:field>
                                    <ipxact:name>field9</ipxact:name>
                                    <ipxact:bitOffset>20</ipxact:bitOffset>
                                    <ipxact:bitWidth>4</ipxact:bitWidth>
                                    <ipxact:modifiedWriteValue>clear</ipxact:modifiedWriteValue>
                                </ipxact:field>
                                <ipxact:field>
                                    <ipxact:name>field10</ipxact:name>
                                    <ipxact:bitOffset>24</ipxact:bitOffset>
                                    <ipxact:bitWidth>2</ipxact:bitWidth>
                                    <ipxact:modifiedWriteValue>modify</ipxact:modifiedWriteValue>
                                </ipxact:field>
                                <ipxact:field>
                                    <ipxact:name>field11</ipxact:name>
                                    <ipxact:bitOffset>26</ipxact:bitOffset>
                                    <ipxact:bitWidth>3</ipxact:bitWidth>
                                    <ipxact:readAction>modify</ipxact:readAction>
                                </ipxact:field>
                                <ipxact:field>
                                    <ipxact:name>field12</ipxact:name>
                                    <ipxact:bitOffset>29</ipxact:bitOffset>
                                    <ipxact:bitWidth>3</ipxact:bitWidth>
                                    <ipxact:reset>
                                        <ipxact:value>0x7</ipxact:value>
                                    </ipxact:reset>
                                </ipxact:field>
                            </ipxact:fields>
                        </ipxact:register>
                    </ipxact:addressBlock>
                </ipxact:memoryMap>
            </ipxact:memoryMaps>
        </ipxact:component>
        """
        with open("/tmp/test.xml", "w") as f:
            f.write(test_xml)
        
        registers = parse_register_info("/tmp/test.xml")
        self.assertEqual(len(registers), 1)
        reg = registers[0]
        
        # Verify register info
        self.assertEqual(reg['register_name'], 'MultiFieldReg')
        self.assertEqual(reg['register_size'], '32')
        
        # Verify fields
        fields = json.loads(reg['register_fields'])
        self.assertEqual(len(fields), 13)  # Check total number of fields
        
        # Verify specific fields
        field_tests = [
            ('field0', 0, 1, 'read-write', None),
            ('field1', 1, 2, 'read-write', 'clear'),  # with readAction
            ('field2', 3, 4, None, None, 'oneToClear'),  # with modifiedWriteValue
            ('field3_reserved', 7, 1, 'read-only', None),
            ('field4', 8, 4, 'write-only', None),
            ('field5', 12, 1, None, None),  # with writeValueConstraint
            ('field6', 13, 2, None, None, None, '0x2'),  # with reset value
            ('field7', 15, 1, None, None, 'set'),
            ('field8', 16, 4, None, 'set'),
            ('field9', 20, 4, None, None, 'clear'),
            ('field10', 24, 2, None, None, 'modify'),
            ('field11', 26, 3, None, 'modify'),
            ('field12', 29, 3, None, None, None, '0x7')
        ]
        
        for field_data in field_tests:
            name, offset, width, access, read_action, *extra = field_data + (None, None)
            field = next(f for f in fields if f['name'] == name)
            
            self.assertEqual(field['bit_offset'], str(offset))
            self.assertEqual(field['bit_width'], str(width))
            if access:
                self.assertEqual(field['access'], access)
                
            # Check for special attributes in elements
            elements = field.get('elements', [])
            if read_action:
                self.assertTrue(any(e['type'] == 'readAction' and e['value'] == read_action 
                                  for e in elements))
            if extra and extra[0]:  # modifiedWriteValue
                self.assertTrue(any(e['type'] == 'modifiedWriteValue' and e['value'] == extra[0] 
                                  for e in elements))
            if extra and extra[1]:  # reset value
                self.assertTrue(any(e['type'] == 'reset' and e['value'] == extra[1] 
                                  for e in elements))

    def test_register_without_fields(self):
        """Test parsing of register that has no fields"""
        test_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <ipxact:component xmlns:ipxact="http://www.accellera.org/XMLSchema/IPXACT/1685-2014">
            <ipxact:memoryMaps>
                <ipxact:memoryMap>
                    <ipxact:name>TestMap</ipxact:name>
                    <ipxact:addressBlock>
                        <ipxact:name>TestBlock</ipxact:name>
                        <ipxact:register>
                            <!-- Only mandatory attributes provided -->
                            <ipxact:name>NoFieldsReg</ipxact:name>
                            <ipxact:addressOffset>0x0</ipxact:addressOffset>
                        </ipxact:register>
                    </ipxact:addressBlock>
                </ipxact:memoryMap>
            </ipxact:memoryMaps>
        </ipxact:component>
        """
        with open("/tmp/test.xml", "w") as f:
            f.write(test_xml)
        
        registers = parse_register_info("/tmp/test.xml")
        self.assertEqual(len(registers), 1)
        reg = registers[0]
        
        # Verify mandatory fields
        self.assertEqual(reg['register_name'], 'NoFieldsReg')
        self.assertEqual(reg['register_offset'], '0x0')
        
        # Verify all optional fields default to 'N/A'
        expected_na_fields = {
            'memory_map_description': 'N/A',
            'block_base_address': 'N/A',
            'block_range': 'N/A',
            'block_width': 'N/A',
            'block_usage': 'N/A',
            'register_size': 'N/A',
            'register_description': 'N/A',
            'register_access': 'N/A',
            'register_reset_value': 'N/A',
            'register_reset_mask': 'N/A',
            'register_fields': 'N/A',
            'hdl_path': 'N/A',
            'register_read_action': 'N/A'
        }
        
        # Check each optional field
        for field, expected_value in expected_na_fields.items():
            self.assertEqual(reg[field], expected_value, 
                           f"Field '{field}' should be 'N/A' when missing")
        
        # Verify required fields from parent elements
        self.assertEqual(reg['memory_map_name'], 'TestMap')
        self.assertEqual(reg['block_name'], 'TestBlock')
        
        # Verify created_date is present and valid
        self.assertTrue('created_date' in reg)
        try:
            datetime.fromisoformat(reg['created_date'])
        except ValueError:
            self.fail("created_date is not in valid ISO format")

    def test_register_with_missing_attributes(self):
        """Test parsing of register with missing attributes"""
        test_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <ipxact:component xmlns:ipxact="http://www.accellera.org/XMLSchema/IPXACT/1685-2014">
            <ipxact:memoryMaps>
                <ipxact:memoryMap>
                    <ipxact:name>TestMap</ipxact:name>
                    <ipxact:addressBlock>
                        <ipxact:name>TestBlock</ipxact:name>
                        <ipxact:register>
                            <!-- Only mandatory attributes provided -->
                            <ipxact:name>MinimalReg</ipxact:name>
                            <ipxact:addressOffset>0x4</ipxact:addressOffset>
                        </ipxact:register>
                    </ipxact:addressBlock>
                </ipxact:memoryMap>
            </ipxact:memoryMaps>
        </ipxact:component>
        """
        with open("/tmp/test.xml", "w") as f:
            f.write(test_xml)
        
        registers = parse_register_info("/tmp/test.xml")
        self.assertEqual(len(registers), 1)
        
        # Test register with minimal attributes
        reg = registers[0]
        
        # Verify mandatory fields
        self.assertEqual(reg['register_name'], 'MinimalReg')
        self.assertEqual(reg['register_offset'], '0x4')
        
        # Verify all optional fields default to 'N/A'
        expected_na_fields = {
            'memory_map_description': 'N/A',
            'block_base_address': 'N/A',
            'block_range': 'N/A',
            'block_width': 'N/A',
            'block_usage': 'N/A',
            'register_size': 'N/A',
            'register_description': 'N/A',
            'register_access': 'N/A',
            'register_reset_value': 'N/A',
            'register_reset_mask': 'N/A',
            'register_fields': 'N/A',
            'hdl_path': 'N/A',
            'register_read_action': 'N/A'
        }
        
        # Check each optional field
        for field, expected_value in expected_na_fields.items():
            self.assertEqual(reg[field], expected_value, 
                           f"Field '{field}' should be 'N/A' when missing")
        
        # Verify required fields are present
        self.assertEqual(reg['memory_map_name'], 'TestMap')
        self.assertEqual(reg['block_name'], 'TestBlock')
        
        # Verify created_date is present and valid
        self.assertTrue('created_date' in reg)
        try:
            datetime.fromisoformat(reg['created_date'])
        except ValueError:
            self.fail("created_date is not in valid ISO format")