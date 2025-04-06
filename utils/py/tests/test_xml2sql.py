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
    create_database
)

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
    conn = create_database(db_path, header)
    
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM ipxact_header')
    row = cursor.fetchone()
    
    assert row[1] == '1.0'  # xml_version
    assert row[2] == 'UTF-8'  # xml_encoding
    assert row[4] == 'example.com'  # vendor
    conn.close()