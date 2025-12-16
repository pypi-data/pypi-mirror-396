#!/usr/bin/env python3
import logging

class Styling:
    def __init__(self):
        self.color_table = [{"name":"Black","ansi_code":30,"hex":"#000000"},{"name":"Red","ansi_code":31,"hex":"#FF0000"},{"name":"Green","ansi_code":32,"hex":"#008000"},{"name":"Yellow","ansi_code":33,"hex":"#FFFF00"},{"name":"Blue","ansi_code":34,"hex":"#0000FF"},{"name":"Magenta","ansi_code":35,"hex":"#FF00FF"},{"name":"Cyan","ansi_code":36,"hex":"#00FFFF"},{"name":"White","ansi_code":37,"hex":"#FFFFFF"},{"name":"Gray","ansi_code":90,"hex":"#808080"},{"name":"LightRed","ansi_code":91,"hex":"#FF8080"},{"name":"LightGreen","ansi_code":92,"hex":"#80FF80"},{"name":"LightYellow","ansi_code":93,"hex":"#FFFF80"},{"name":"LightBlue","ansi_code":94,"hex":"#8080FF"},{"name":"LightMagenta","ansi_code":95,"hex":"#FF80FF"},{"name":"LightCyan","ansi_code":96,"hex":"#80FFFF"},{"name":"LightWhite","ansi_code":97,"hex":"#F0F0F0"}]
    def view_all_colors(self):
        return self.color_table
    def get_color(self,color_name="",format=""):
        color_match=[color for color in self.color_table if color['name'].lower() == color_name.lower() ]
        # logging.info(f"color_match: {color_match}")
        # logging.info(f"color_match: {format}")
        if color_match == []:
            return ""
        else:
            if format == "html":
                color_pallet = "hex"
            elif format == "simple":
                color_pallet = "ansi_code"
            elif format == "github":
                return color_name
            else:
                return ""
        # logging.info(f"color_match: {color_match[0]}")
        return color_match[0][color_pallet]


    def apply(self,value="",format="",styling_attributes={}):
        logging.info(f"value: {value} / format: {format} / styling_attributes: {styling_attributes}")
        value_colorized = ""
        if "style" in styling_attributes:
            color_label = styling_attributes['style'].split(": ")[1]
        else:
            color_label = "white"
        text_formating = 0
        formating = ""
        # print(f"styling_attributes['formating']: {styling_attributes}")
        if "formating" in styling_attributes:
            formating = styling_attributes['formating']
        if formating == "normal" or formating == "":
            text_formating = 0
        elif formating == "bold":
            text_formating = 1
        elif formating == "dim":
            text_formating = 2
        elif formating == "italic":
            text_formating = 3
        elif formating == "underlined":
            text_formating = 4
        else:
            logging.error(f"Unknown formating: {formating}")
            exit(1)
        # color_corresp = self.get_color(color_label,"ansi_code")
        color_corresp = self.get_color(color_label,format)

        if color_corresp == "":
            if format == "html":
                value_colorized  = r'<span style="' + styling_attributes['style'] + ';">' + value + r"</span>"
            else:
                logging.info(f"style '{styling_attributes['style']}' not found, using default")
                # value_colorized = value
                return value

        else:
            if format == "simple":
                value_colorized = f"\x1b[{text_formating};{color_corresp}m{value}\x1b[0m"
            elif format == "github":
                # value_colorized = f"\x1b[{text_formating};{color_corresp}m{value}\x1b[0m"
                # value_colorized = f"$`\textcolor{{red}}{{\text{{Smith}}`$"
                logging.info(f"color_label: {color_label}")
                return r"$`\textcolor{"+ color_label + r"}{\text{" + value + "}}`$"
            elif format == "html":
                value_colorized  = r'<span style="' + styling_attributes['style'] + r';">' + value + r"</span>"
            else:
                value_colorized = f"\x1b[{text_formating};{color_corresp}m{value}\x1b[0m"

            logging.info(f"format: {format}")
        return value_colorized


if __name__ == "__main__":
    import json
    logging.basicConfig(level=logging.INFO)
    styler = Styling()
    sample_data = [
        {"name": "Alice", "age": 30, "city": "New York"},
        {"name": "Bob", "age": 25, "city": "Los Angeles"},
        {"name": "Charlie", "age": 35, "city": "Chicago"},
    ]
    for person in sample_data:
        styled_name = styler.apply(person['name'], format="simple", styling_attributes={"style": "color: Red", "formating": "bold"})
        print(f"Name: {styled_name}, Age: {person['age']}, City: {person['city']}")
    
    # print(Styling().color_table)
    json_output = json.dumps(Styling().color_table, indent=4)
    print(json_output)