def set_options(default_options: dict, custom_options: dict) -> dict:
    if custom_options is None:
        return default_options

    for key, value in custom_options.items():
        if key in default_options:
            default_options[key] = value
    return default_options
