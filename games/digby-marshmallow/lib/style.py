import caterpie


style = caterpie.Style(
    font_name = "Fontdinerdotcom",
    font_size = 0.03,
    outline = (1.0, 1.0, 1.0, 1.0),
    background = (0.3, 0.2, 0.4, 0.8),
    unselected_color = (200, 200, 0, 255),
    selected_color = (255, 255, 100, 255)
)

caterpie.set_default_style(style)
