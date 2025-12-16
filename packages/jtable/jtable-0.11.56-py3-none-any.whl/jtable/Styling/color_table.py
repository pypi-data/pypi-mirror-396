#!/usr/bin/env python3


color_table_base_16 =[
    {
        "name": "Black",
        "ansi_code": 30,
        "hex": "#000000"
    },
    {
        "name": "Red",
        "ansi_code": 31,
        "hex": "#FF0000"
    },
    {
        "name": "Green",
        "ansi_code": 32,
        "hex": "#008000"
    },
    {
        "name": "Yellow",
        "ansi_code": 33,
        "hex": "#FFFF00"
    },
    {
        "name": "Blue",
        "ansi_code": 34,
        "hex": "#0000FF"
    },
    {
        "name": "Magenta",
        "ansi_code": 35,
        "hex": "#FF00FF"
    },
    {
        "name": "Cyan",
        "ansi_code": 36,
        "hex": "#00FFFF"
    },
    {
        "name": "White",
        "ansi_code": 37,
        "hex": "#FFFFFF"
    },
    {
        "name": "Gray",
        "ansi_code": 90,
        "hex": "#808080"
    },
    {
        "name": "LightRed",
        "ansi_code": 91,
        "hex": "#FF8080"
    },
    {
        "name": "LightGreen",
        "ansi_code": 92,
        "hex": "#80FF80"
    },
    {
        "name": "LightYellow",
        "ansi_code": 93,
        "hex": "#FFFF80"
    },
    {
        "name": "LightBlue",
        "ansi_code": 94,
        "hex": "#8080FF"
    },
    {
        "name": "LightMagenta",
        "ansi_code": 95,
        "hex": "#FF80FF"
    },
    {
        "name": "LightCyan",
        "ansi_code": 96,
        "hex": "#80FFFF"
    },
    {
        "name": "LightWhite",
        "ansi_code": 97,
        "hex": "#F0F0F0"
    }
]


color_table_base_256 = [
    # Standard colors (0-15)
    {"name": "black_1", "ansi_code": 0, "hex": "#000000"},
    {"name": "red_1", "ansi_code": 1, "hex": "#800000"},
    {"name": "green_1", "ansi_code": 2, "hex": "#008000"},
    {"name": "yellow_1", "ansi_code": 3, "hex": "#808000"},
    {"name": "blue_1", "ansi_code": 4, "hex": "#000080"},
    {"name": "magenta_1", "ansi_code": 5, "hex": "#800080"},
    {"name": "cyan_1", "ansi_code": 6, "hex": "#008080"},
    {"name": "white_1", "ansi_code": 7, "hex": "#c0c0c0"},
    {"name": "gray_1", "ansi_code": 8, "hex": "#808080"},
    {"name": "red_2", "ansi_code": 9, "hex": "#ff0000"},
    {"name": "green_2", "ansi_code": 10, "hex": "#00ff00"},
    {"name": "yellow_2", "ansi_code": 11, "hex": "#ffff00"},
    {"name": "blue_2", "ansi_code": 12, "hex": "#0000ff"},
    {"name": "magenta_2", "ansi_code": 13, "hex": "#ff00ff"},
    {"name": "cyan_2", "ansi_code": 14, "hex": "#00ffff"},
    {"name": "white_2", "ansi_code": 15, "hex": "#ffffff"},

    # 6x6x6 RGB cube (16-231)
    # Reds (darker to lighter)
    {"name": "red_3", "ansi_code": 52, "hex": "#5f0000"},
    {"name": "red_4", "ansi_code": 88, "hex": "#870000"},
    {"name": "red_5", "ansi_code": 124, "hex": "#af0000"},
    {"name": "red_6", "ansi_code": 160, "hex": "#d70000"},
    {"name": "red_7", "ansi_code": 196, "hex": "#ff0000"},
    {"name": "red_8", "ansi_code": 203, "hex": "#ff5f5f"},
    {"name": "red_9", "ansi_code": 210, "hex": "#ff8787"},
    {"name": "red_10", "ansi_code": 217, "hex": "#ffafaf"},

    # Greens
    {"name": "green_3", "ansi_code": 22, "hex": "#005f00"},
    {"name": "green_4", "ansi_code": 28, "hex": "#008700"},
    {"name": "green_5", "ansi_code": 34, "hex": "#00af00"},
    {"name": "green_6", "ansi_code": 40, "hex": "#00d700"},
    {"name": "green_7", "ansi_code": 46, "hex": "#00ff00"},
    {"name": "green_8", "ansi_code": 83, "hex": "#5fff5f"},
    {"name": "green_9", "ansi_code": 120, "hex": "#87ff87"},
    {"name": "green_10", "ansi_code": 157, "hex": "#afffaf"},

    # Blues
    {"name": "blue_3", "ansi_code": 17, "hex": "#00005f"},
    {"name": "blue_4", "ansi_code": 18, "hex": "#000087"},
    {"name": "blue_5", "ansi_code": 19, "hex": "#0000af"},
    {"name": "blue_6", "ansi_code": 20, "hex": "#0000d7"},
    {"name": "blue_7", "ansi_code": 21, "hex": "#0000ff"},
    {"name": "blue_8", "ansi_code": 75, "hex": "#5fafff"},
    {"name": "blue_9", "ansi_code": 111, "hex": "#87afff"},
    {"name": "blue_10", "ansi_code": 153, "hex": "#afd7ff"},

    # Yellows
    {"name": "yellow_3", "ansi_code": 58, "hex": "#5f5f00"},
    {"name": "yellow_4", "ansi_code": 94, "hex": "#875f00"},
    {"name": "yellow_5", "ansi_code": 136, "hex": "#af8700"},
    {"name": "yellow_6", "ansi_code": 178, "hex": "#d7af00"},
    {"name": "yellow_7", "ansi_code": 226, "hex": "#ffff00"},
    {"name": "yellow_8", "ansi_code": 228, "hex": "#ffff87"},
    {"name": "yellow_9", "ansi_code": 230, "hex": "#ffffaf"},
    {"name": "yellow_10", "ansi_code": 231, "hex": "#ffffd7"},

    # Magentas
    {"name": "magenta_3", "ansi_code": 53, "hex": "#5f005f"},
    {"name": "magenta_4", "ansi_code": 89, "hex": "#87005f"},
    {"name": "magenta_5", "ansi_code": 125, "hex": "#af005f"},
    {"name": "magenta_6", "ansi_code": 161, "hex": "#d7005f"},
    {"name": "magenta_7", "ansi_code": 201, "hex": "#ff00ff"},
    {"name": "magenta_8", "ansi_code": 207, "hex": "#ff5fff"},
    {"name": "magenta_9", "ansi_code": 213, "hex": "#ff87ff"},
    {"name": "magenta_10", "ansi_code": 219, "hex": "#ffafff"},

    # Cyans
    {"name": "cyan_3", "ansi_code": 23, "hex": "#005f5f"},
    {"name": "cyan_4", "ansi_code": 29, "hex": "#00875f"},
    {"name": "cyan_5", "ansi_code": 35, "hex": "#00af5f"},
    {"name": "cyan_6", "ansi_code": 41, "hex": "#00d75f"},
    {"name": "cyan_7", "ansi_code": 51, "hex": "#00ffff"},
    {"name": "cyan_8", "ansi_code": 87, "hex": "#5fffff"},
    {"name": "cyan_9", "ansi_code": 123, "hex": "#87ffff"},
    {"name": "cyan_10", "ansi_code": 159, "hex": "#afffff"},

    # Oranges
    {"name": "orange_1", "ansi_code": 130, "hex": "#af5f00"},
    {"name": "orange_2", "ansi_code": 166, "hex": "#d75f00"},
    {"name": "orange_3", "ansi_code": 172, "hex": "#d78700"},
    {"name": "orange_4", "ansi_code": 202, "hex": "#ff5f00"},
    {"name": "orange_5", "ansi_code": 208, "hex": "#ff8700"},
    {"name": "orange_6", "ansi_code": 214, "hex": "#ffaf00"},
    {"name": "orange_7", "ansi_code": 220, "hex": "#ffd700"},

    # Purples
    {"name": "purple_1", "ansi_code": 54, "hex": "#5f0087"},
    {"name": "purple_2", "ansi_code": 55, "hex": "#5f00af"},
    {"name": "purple_3", "ansi_code": 56, "hex": "#5f00d7"},
    {"name": "purple_4", "ansi_code": 57, "hex": "#5f00ff"},
    {"name": "purple_5", "ansi_code": 93, "hex": "#8700ff"},
    {"name": "purple_6", "ansi_code": 129, "hex": "#af00ff"},
    {"name": "purple_7", "ansi_code": 165, "hex": "#d700ff"},

    # Pinks
    {"name": "pink_1", "ansi_code": 168, "hex": "#d75f87"},
    {"name": "pink_2", "ansi_code": 169, "hex": "#d75faf"},
    {"name": "pink_3", "ansi_code": 205, "hex": "#ff5faf"},
    {"name": "pink_4", "ansi_code": 206, "hex": "#ff5fd7"},
    {"name": "pink_5", "ansi_code": 211, "hex": "#ff87af"},
    {"name": "pink_6", "ansi_code": 212, "hex": "#ff87d7"},

    # Browns
    {"name": "brown_1", "ansi_code": 52, "hex": "#5f0000"},
    {"name": "brown_2", "ansi_code": 58, "hex": "#5f5f00"},
    {"name": "brown_3", "ansi_code": 94, "hex": "#875f00"},
    {"name": "brown_4", "ansi_code": 95, "hex": "#875f5f"},
    {"name": "brown_5", "ansi_code": 130, "hex": "#af5f00"},
    {"name": "brown_6", "ansi_code": 131, "hex": "#af5f5f"},

    # Grays/Grayscale (232-255)
    {"name": "gray_2", "ansi_code": 232, "hex": "#080808"},
    {"name": "gray_3", "ansi_code": 233, "hex": "#121212"},
    {"name": "gray_4", "ansi_code": 234, "hex": "#1c1c1c"},
    {"name": "gray_5", "ansi_code": 235, "hex": "#262626"},
    {"name": "gray_6", "ansi_code": 236, "hex": "#303030"},
    {"name": "gray_7", "ansi_code": 237, "hex": "#3a3a3a"},
    {"name": "gray_8", "ansi_code": 238, "hex": "#444444"},
    {"name": "gray_9", "ansi_code": 239, "hex": "#4e4e4e"},
    {"name": "gray_10", "ansi_code": 240, "hex": "#585858"},
    {"name": "gray_11", "ansi_code": 241, "hex": "#626262"},
    {"name": "gray_12", "ansi_code": 242, "hex": "#6c6c6c"},
    {"name": "gray_13", "ansi_code": 243, "hex": "#767676"},
    {"name": "gray_14", "ansi_code": 244, "hex": "#808080"},
    {"name": "gray_15", "ansi_code": 245, "hex": "#8a8a8a"},
    {"name": "gray_16", "ansi_code": 246, "hex": "#949494"},
    {"name": "gray_17", "ansi_code": 247, "hex": "#9e9e9e"},
    {"name": "gray_18", "ansi_code": 248, "hex": "#a8a8a8"},
    {"name": "gray_19", "ansi_code": 249, "hex": "#b2b2b2"},
    {"name": "gray_20", "ansi_code": 250, "hex": "#bcbcbc"},
    {"name": "gray_21", "ansi_code": 251, "hex": "#c6c6c6"},
    {"name": "gray_22", "ansi_code": 252, "hex": "#d0d0d0"},
    {"name": "gray_23", "ansi_code": 253, "hex": "#dadada"},
    {"name": "gray_24", "ansi_code": 254, "hex": "#e4e4e4"},
    {"name": "gray_25", "ansi_code": 255, "hex": "#eeeeee"},
]


if __name__ == "__main__":
    # for color in color_table_base_256:
    #     print(f"{color['name']} - ANSI: {color['ansi_code']} - HEX: {color['hex']}")
    import json
    json_output = json.dumps(color_table_base_256, indent=4)
    print(json_output)

    # for ansi_code in range(0, 255):
    #     print(f"\e[0;{ansi_code}m Hello World\e[0m")

    for ansi_code in range(0, 255):
        print(f"\033[0;{ansi_code}m Color {ansi_code} \033[0m")
    # Source - https://stackoverflow.com/a
    # Posted by Richard, modified by community. See post 'Timeline' for change history
    # Retrieved 2025-11-09, License - CC BY-SA 4.0

    #!/usr/bin/env python3

    for i in range(30, 37 + 1):
        print("\033[%dm%d\t\t\033[%dm%d" % (i, i, i + 60, i + 60))

    print("\\033[39m\\033[49m                 - Reset color")
    print("\\033[2K                          - Clear Line")
    print("\\033[<L>;<C>H or \\033[<L>;<C>f   - Put the cursor at line L and column C.")
    print("\\033[<N>A                        - Move the cursor up N lines")
    print("\\033[<N>B                        - Move the cursor down N lines")
    print("\\033[<N>C                        - Move the cursor forward N columns")
    print("\\033[<N>D                        - Move the cursor backward N columns\n")
    print("\\033[2J                          - Clear the screen, move to (0,0)")
    print("\\033[K                           - Erase to end of line")
    print("\\033[s                           - Save cursor position")
    print("\\033[u                           - Restore cursor position\n")
    print("\\033[4m                          - Underline on")
    print("\\033[24m                         - Underline off\n")
    print("\\033[1m                          - Bold on")
    print("\\033[21m                         - Bold off")
