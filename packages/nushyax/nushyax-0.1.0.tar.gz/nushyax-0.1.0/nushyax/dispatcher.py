def resolve(command, config):
    aliases = config.get("aliases", {})
    if command in aliases:
        command = aliases[command]

    return config.get("commands", {}).get(command)
