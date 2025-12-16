import re


def to_snake_case(name: str) -> str:
    """Converts a PascalCase or CamelCase string to snake_case."""
    s1 = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', name)
    s2 = re.sub(r'([a-z\d])([A-Z])', r'\1_\2', s1)
    return s2.lower()

def pluralize(name: str) -> str:
    """Pluralizes a word."""
    suffix_bypass_list = ['prefs', 'data', 'stats']
    if name.endswith(tuple(suffix_bypass_list)):
        return name
    elif name.endswith('y'):
        return name[:-1] + 'ies'
    elif name.endswith('s'):
        return name + 'es'
    else:
        return name + 's'

def convert_entity_type_to_table_name(entity_type: str) -> str:
    """Converts an entity type (singular PascalCase) to a table name (plural snake_case)."""
    return pluralize(to_snake_case(entity_type))