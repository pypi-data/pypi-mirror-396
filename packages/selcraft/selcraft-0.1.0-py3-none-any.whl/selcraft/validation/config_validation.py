from pathlib import Path

from selcraft.validation.error import DuplicateUDSPathError
from selcraft.validation.rule import Rule


def group_sockets_by_directory(sockets: list[dict]) -> dict[str, list[dict]]:
    dir_to_sockets = {}

    for socket in sockets:
        path = socket.get("path", "")
        directory = str(Path(path).parent)

        if directory not in dir_to_sockets:
            dir_to_sockets[directory] = []
        dir_to_sockets[directory].append(socket)

    return dir_to_sockets


def check_for_duplicate_uds_paths(dir_to_sockets: dict) -> None:
    for directory, dir_sockets in dir_to_sockets.items():
        if len(dir_sockets) > 1:
            socket_names = [s.get("name", "unknown") for s in dir_sockets]
            raise DuplicateUDSPathError(socket_names, directory)


class NoDuplicateUDSPathRule(Rule):

    def validate(self, config: dict) -> None:
        sockets = config.get("ipc", {}).get("sockets", {}).get("uds", [])

        if len(sockets) <= 1:
            return

        dir_to_sockets = group_sockets_by_directory(sockets)
        check_for_duplicate_uds_paths(dir_to_sockets)


def validate_config(config: dict, rules: list[Rule] | set[Rule] | None = None) -> None:
    if rules is None:
        rules = [NoDuplicateUDSPathRule()]

    disabled_rules = config.get("validation", {}).get("disabled", [])

    for rule in rules:
        if rule.name in disabled_rules:
            continue
        rule.validate(config)
