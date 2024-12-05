import re
import json


# Regular expressions for identifying headers and key-value pairs
section_header_pattern = re.compile(r'---+\s*([\w\s]+)\s*---+')
key_value_pattern = re.compile(r'(\w[\w\s]+):\s*(.*)')

# Dictionary to hold parsed data
parsed_data = {}

def convert2json(result):
    sections = re.split(section_header_pattern, result)

    # Start parsing sections
    for i in range(1, len(sections), 2):
        section_name = sections[i].strip()  # Header name
        section_content = sections[i + 1].strip()  # Content following the header
        
        # Initialize section data as a list to handle unique entries
        if section_name not in parsed_data:
            parsed_data[section_name] = []
        
        section_items = {}

        # Find key-value pairs within the section content
        for match in re.finditer(key_value_pattern, section_content):
            key, value = match.groups()
            
            # Normalize the key and value
            key = key.strip()
            
            # Remove prefix characters like ": " and normalize to lowercase
            value = value.strip().lower()
            if value.startswith(": "):
                value = value[2:].strip()
            
            # Append to existing lists or create new entries
            if key in section_items:
                if isinstance(section_items[key], list):
                    section_items[key].append(value)
                else:
                    section_items[key] = [section_items[key], value]
            else:
                section_items[key] = value
        
        # Remove duplicates in each key's value list
        for key, values in section_items.items():
            if isinstance(values, list):
                # Convert list to a set to remove duplicates, then back to a list
                section_items[key] = list(set(values))
        
        # Add unique items to the parsed_data dictionary
        if section_items not in parsed_data[section_name]:
            parsed_data[section_name].append(section_items)

    # Convert the parsed data to JSON format
    parsed_json = json.dumps(parsed_data, indent=4)
    return parsed_json

text = """


****************Info Tracer****************
Full Name:, Alexander Bogod
First Name:, Alexander
Last Name:, Bogod
Age:, 49
Address:, New York, NY, United States
Country Code:, US
Organization Name N1:, Broadway Realty
Organization Title N1:, Real Estate Broker
University Name N1:, 1703030558-LIU Brooklyn
University Degree N1:, Bachelor's degree, Statistic,Economics,Math,Physics
University End Year N1:, 1996
University Name N2:, LIU Brooklyn
University Degree N2:, Statistic,Economics,Math,Physics
University End Year N2:, 1996
University Name N3:, Long Island University, Brooklyn Campus
University End Year N3:, 1996
Url N1:, http://nycrealestatemarket.blogspot.com/
Url N2:, http://www.Lincolnsquarerealty.com/


"""

print(convert2json(text))