import argparse
import os
from pathlib import Path
import xml.etree.ElementTree as ET

def elements_equal(e1, e2):
    if e1.tag != e2.tag:
        return False
    if (e1.text or '').strip() != (e2.text or '').strip():
        return False
    if (e1.tail or '').strip() != (e2.tail or '').strip():
        return False
    if sorted(e1.attrib.items()) != sorted(e2.attrib.items()):
        return False
    if len(e1) != len(e2):
        return False
    return all(elements_equal(c1, c2) for c1, c2 in zip(e1, e2))

def main():
    parser = argparse.ArgumentParser(description='Verify that generated XML files are functionally equivalent to the originals.')
    parser.add_argument('file_list', help='Text file with list of original XML file paths')
    parser.add_argument('generated_dir', help='Directory with generated XML files')
    args = parser.parse_args()

    generated_dir = Path(args.generated_dir)
    all_ok = True
    with open(args.file_list, 'r') as f:
        for line in f:
            orig_path = line.strip()
            if not orig_path:
                continue
            orig_file = Path(orig_path)
            gen_file = generated_dir / orig_file.name
            if not gen_file.exists():
                print(f"MISSING: {gen_file}")
                all_ok = False
                continue
            try:
                orig_xml = ET.parse(orig_file).getroot()
                gen_xml = ET.parse(gen_file).getroot()
                if elements_equal(orig_xml, gen_xml):
                    print(f"OK: {orig_file.name}")
                else:
                    print(f"DIFFER: {orig_file.name}")
                    all_ok = False
            except Exception as e:
                print(f"ERROR: {orig_file.name}: {e}")
                all_ok = False
    if all_ok:
        print("All files are functionally equivalent.")
    else:
        print("Some files differ or are missing.")

if __name__ == '__main__':
    main()