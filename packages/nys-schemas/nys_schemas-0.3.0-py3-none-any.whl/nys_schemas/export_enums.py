"""
Export all Enum and IntEnum classes from nys_schemas to JSON format.

This module discovers all enum classes and module-level constants (arrays/lists)
from nys_schemas and exports them to JSON for use by React and other consumers.

Uses AST parsing to avoid importing modules that have external dependencies.
"""

import ast
import json
import os
import sys
from typing import Any, Dict, List, Set, Union
import pkgutil


def get_enums_from_file(filepath: str) -> Dict[str, Dict[str, Any]]:
    """Parse a Python file and extract all Enum and IntEnum classes."""
    try:
        with open(filepath, 'r') as file:
            tree = ast.parse(file.read(), filename=filepath)
    except Exception as e:
        return {}
    
    enums = {}
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            # Check if this class inherits from Enum or IntEnum
            is_enum = False
            for base in node.bases:
                if isinstance(base, ast.Name):
                    if base.id in ['Enum', 'IntEnum']:
                        is_enum = True
                        break
                elif isinstance(base, ast.Attribute):
                    if base.attr in ['Enum', 'IntEnum']:
                        is_enum = True
                        break
            
            if is_enum:
                enum_name = node.name
                enum_members = {}
                
                for n in node.body:
                    if isinstance(n, ast.Assign) and len(n.targets) == 1:
                        target = n.targets[0]
                        if isinstance(target, ast.Name):
                            # Extract the value - handle both old (ast.Str/ast.Num) and new (ast.Constant) syntax
                            value = None
                            if isinstance(n.value, ast.Str):
                                value = n.value.s
                            elif isinstance(n.value, ast.Num):
                                value = n.value.n
                            elif isinstance(n.value, ast.Constant):
                                value = n.value.value
                            
                            if value is not None:
                                enum_members[target.id] = value
                
                if enum_members:
                    enums[enum_name] = enum_members
    
    return enums


def get_constants_from_file(filepath: str) -> Dict[str, List[str]]:
    """Parse a Python file and extract module-level constants (lists/sets) containing enum references."""
    try:
        with open(filepath, 'r') as file:
            tree = ast.parse(file.read(), filename=filepath)
    except Exception as e:
        return {}
    
    constants = {}
    
    for node in ast.walk(tree):
        # Detect module-level array/list assignments
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name) and not target.id.startswith('_'):
                # Check if it's a list or set containing enum attribute references
                if isinstance(node.value, ast.List):
                    elements = node.value.elts
                    if elements and all(
                        (isinstance(elt, ast.Attribute) and isinstance(elt.value, ast.Name)) or
                        isinstance(elt, (ast.Str, ast.Constant))
                        for elt in elements
                    ):
                        array_values = []
                        for elt in elements:
                            if isinstance(elt, ast.Attribute) and isinstance(elt.value, ast.Name):
                                # Handle Enum member references like JobType.PICKING
                                array_values.append(elt.attr)
                            elif isinstance(elt, (ast.Str, ast.Constant)):
                                # Handle string literals
                                value = elt.s if hasattr(elt, 's') else (elt.value if isinstance(elt.value, str) else None)
                                if value:
                                    array_values.append(value)
                        if array_values:
                            constants[target.id] = array_values
                # For set literals like {StorageModuleType.X, StorageModuleType.Y}
                elif isinstance(node.value, ast.Set):
                    elements = node.value.elts
                    if elements and all(
                        isinstance(elt, ast.Attribute) and isinstance(elt.value, ast.Name)
                        for elt in elements
                    ):
                        array_values = []
                        for elt in elements:
                            if isinstance(elt, ast.Attribute) and isinstance(elt.value, ast.Name):
                                array_values.append(elt.attr)
                        if array_values:
                            constants[target.id] = array_values
    
    return constants


def export_all_enums(output_path: str) -> None:
    """Export all enums and constants from nys_schemas to JSON."""
    all_enums: Dict[str, Dict[str, Any]] = {}
    all_constants: Dict[str, List[str]] = {}
    
    # Find the nys_schemas package path without importing it
    # The script is in nys_schemas/nys_schemas/export_enums.py
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # script_dir is nys_schemas/nys_schemas/, so package_dir is nys_schemas/
    package_dir = script_dir
    
    # Walk through all Python files in the package directory
    for root, dirs, files in os.walk(package_dir):
        # Skip __pycache__ directories
        dirs[:] = [d for d in dirs if d != '__pycache__']
        
        for file in files:
            if not file.endswith('.py') or file == '__init__.py' or file == 'export_enums.py':
                continue
            
            filepath = os.path.join(root, file)
            
            try:
                # Parse the file using AST
                module_enums = get_enums_from_file(filepath)
                all_enums.update(module_enums)
                
                module_constants = get_constants_from_file(filepath)
                if module_constants:
                    all_constants.update(module_constants)
                    
            except Exception as e:
                # Skip files that can't be parsed
                print(f"Warning: Could not process {filepath}: {e}", file=sys.stderr)
                continue
    
    # Combine enums and constants
    result = {**all_enums, **all_constants}
    
    # Write to JSON file
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=4)


def main():
    """CLI entry point for exporting enums."""
    if len(sys.argv) != 2:
        print("Usage: python -m nys_schemas.export_enums <output_path>", file=sys.stderr)
        sys.exit(1)
    
    output_path = sys.argv[1]
    export_all_enums(output_path)
    print(f"Exported enums to {output_path}")


if __name__ == "__main__":
    main()

