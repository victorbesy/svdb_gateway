import pytest
import sqlite3
# import os
from pathlib import Path
from sql2xml import (
    setup_argument_parser,
    validate_input_file,
    get_output_path,
    fetch_header_info,
    create_xml_tree,
    write_xml_file
)

@pytest.fixture
def temp_db_file(tmp_path):
    """Create a temporary SQLite database for testing."""
    db_file = tmp_path / "test_registers.db"
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE ipxact_header (
            id INTEGER PRIMARY KEY,
            xml_version TEXT,
            xml_encoding TEXT,
            schema_version TEXT,
            vendor TEXT,
            library TEXT,
            name TEXT,
            version TEXT,
            description TEXT,
            created_date TEXT
        )
    ''')

    cursor.execute('''
        INSERT INTO ipxact_header (
            xml_version, xml_encoding, schema_version, vendor, library,
            name, version, description, created_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        '1.0',
        'UTF-8',
        'http://www.accellera.org/XMLSchema/IPXACT/1685-2014',
        'example.com',
        'test_lib',
        'test_component',
        '1.0',
        'Test description',
        '2025-04-05T12:00:00'
    ))

    conn.commit()
    conn.close()
    return db_file

def test_parser_required_input():
    """Test that parser requires input argument."""
    parser = setup_argument_parser()
    with pytest.raises(SystemExit):
        parser.parse_args([])

def test_parser_with_input(temp_db_file):
    """Test parser with only input file."""
    parser = setup_argument_parser()
    args = parser.parse_args(['-i', str(temp_db_file)])
    assert args.input == str(temp_db_file)
    assert args.output is None

def test_parser_with_input_and_output(temp_db_file, tmp_path):
    """Test parser with both input and output arguments."""
    output_file = tmp_path / "output.xml"
    parser = setup_argument_parser()
    args = parser.parse_args(['-i', str(temp_db_file), '-o', str(output_file)])
    assert args.input == str(temp_db_file)
    assert args.output == str(output_file)

def test_validate_input_file_exists(temp_db_file):
    """Test validation of existing database file."""
    validate_input_file(str(temp_db_file))

def test_validate_input_file_not_exists():
    """Test validation of non-existing file."""
    with pytest.raises(FileNotFoundError):
        validate_input_file('nonexistent.db')

def test_validate_input_file_wrong_extension(tmp_path):
    """Test validation of file with wrong extension."""
    wrong_file = tmp_path / "test.txt"
    wrong_file.write_text("content")
    with pytest.raises(ValueError):
        validate_input_file(str(wrong_file))

def test_get_output_path_with_output(temp_db_file, tmp_path):
    """Test output path when output is provided."""
    output_file = tmp_path / "custom.xml"

    class Args:
        def __init__(self, input_path, output_path):
            self.input = input_path
            self.output = output_path

    args = Args(str(temp_db_file), str(output_file))
    output_path = get_output_path(args)
    assert output_path == output_file

def test_get_output_path_without_output(temp_db_file):
    """Test output path generation when no output is provided."""
    class Args:
        def __init__(self, input_path):
            self.input = input_path
            self.output = None

    args = Args(str(temp_db_file))
    output_path = get_output_path(args)
    assert output_path == Path(temp_db_file).with_suffix('.xml')

def test_fetch_header_info(temp_db_file):
    """Test fetching header information from database."""
    header_info = fetch_header_info(str(temp_db_file))
    assert header_info['xml_version'] == '1.0'
    assert header_info['xml_encoding'] == 'UTF-8'
    assert header_info['vendor'] == 'example.com'
    assert header_info['library'] == 'test_lib'
    assert header_info['name'] == 'test_component'
    assert header_info['version'] == '1.0'
    assert header_info['description'] == 'Test description'

def test_create_xml_tree(temp_db_file):
    """Test XML tree creation with header information."""
    header_info = fetch_header_info(str(temp_db_file))
    root = create_xml_tree(header_info)

    assert root.tag.endswith('component')
    assert root.find('.//{*}vendor').text == 'example.com'
    assert root.find('.//{*}library').text == 'test_lib'
    assert root.find('.//{*}name').text == 'test_component'
    assert root.find('.//{*}version').text == '1.0'
    assert root.find('.//{*}description').text == 'Test description'

def test_write_xml_file(temp_db_file, tmp_path):
    """Test XML file writing with proper declaration."""
    header_info = fetch_header_info(str(temp_db_file))
    root = create_xml_tree(header_info)
    output_path = tmp_path / "output.xml"

    write_xml_file(root, header_info, output_path)

    with open(output_path, 'r', encoding='utf-8') as f:
        content = f.read()
        assert '<?xml version="1.0" encoding="UTF-8"?>' in content
        assert '<ipxact:vendor>example.com</ipxact:vendor>' in content
