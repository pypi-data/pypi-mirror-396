import os
from datetime import datetime
from typing import Optional

PKG_PREFIX = ""
QM_ROOTFS = "/usr/lib/qm/rootfs"


def normalize_name(name: str) -> str:
    return name.replace("-", "_")


def build_jinja_data(config: dict) -> dict:
    pkg_name = f"{config['info']['name']}"

    apps_data = build_apps_data(config["apps"])
    ipc_data = build_ipc_data(config["ipc"])
    permissions_data = build_permissions_data(
        config["permissions"], apps_data, ipc_data
    )
    data = {
        "date": datetime.today().strftime("%a %b %d %Y"),
        "policy": {**config["info"]},
        "apps": apps_data,
        "ipc": ipc_data,
        "permissions": permissions_data,
        "output": {"files": build_output_files_data(pkg_name)},
    }

    return data


def build_apps_data(apps: dict) -> dict:

    def build_binaries_data(binaries: list[dict]) -> list[dict]:
        data = []
        for binary in binaries:
            name = normalize_name(binary["name"])
            path = binary["path"]
            is_qm = binary.get("is_qm", False)

            label = f"qm_{name}_t" if is_qm else f"{name}_t"
            path = (
                path
                if not is_qm
                else os.path.join(QM_ROOTFS, path[1:] if path.startswith("/") else path)
            )

            data.append(
                {
                    "type": "binary",
                    "name": name,
                    "path": path,
                    "label": label,
                    "is_qm": is_qm,
                }
            )

        return data

    def build_containers_data(containers: list[dict]) -> list[dict]:
        data = []
        for container in containers:
            name = normalize_name(container["name"])
            label = container["label"]
            is_qm = container.get("is_qm", False)

            data.append(
                {"type": "container", "name": name, "label": label, "is_qm": is_qm}
            )

        return data

    binaries = build_binaries_data(apps.get("binaries", []))
    containers = build_containers_data(apps.get("containers", []))
    return {"binaries": binaries, "containers": containers}


def build_ipc_data(ipc: dict) -> dict:
    def build_uds_data(uds: dict) -> list[dict]:
        data = []
        for entry in uds:
            name = normalize_name(entry["name"])
            path = entry["path"]
            label = f"{name}_uds_t"

            data.append(
                {
                    "name": name,
                    "label": label,
                    "path": path,
                    "dir": os.path.dirname(path),
                }
            )
            # Since /var/run is canonical in rhel9 and /run in rhel10
            # we apply the context for both directories
            if path.startswith("/var/run/"):
                run_path = path.rstrip("/var")
                data.append(
                    {
                        "name": name,
                        "label": label,
                        "path": run_path,
                        "dir": os.path.dirname(run_path),
                    }
                )
            elif path.startswith("/run/"):
                var_run_path = f"/var{path}"
                data.append(
                    {
                        "name": name,
                        "label": label,
                        "path": var_run_path,
                        "dir": os.path.dirname(var_run_path),
                    }
                )

        return data

    def build_shm_data(shm: list):
        data = []
        for entry in shm:
            name = normalize_name(entry["name"])
            path = entry["path"]
            label = f"{name}_shm_t"

            data.append(
                {
                    "name": name,
                    "path": path,
                    "label": label,
                    "dir": os.path.dirname(path),
                }
            )

        return data

    data = {
        "uds": build_uds_data(ipc.get("sockets", {}).get("uds", {})),
        "shm": build_shm_data(ipc.get("shm", [])),
    }
    return data


def build_permissions_data(
    perms: dict, mapped_app_data: dict, mapped_ipc_data: dict
) -> list[dict]:

    def find_app(name: str) -> Optional[dict]:
        all_apps = mapped_app_data.get("binaries", []) + mapped_app_data.get(
            "containers", []
        )
        for entry in all_apps:
            if entry.get("name", "") == name:
                return entry

    def find_ipc(name: str) -> Optional[dict]:
        for key, entries in mapped_ipc_data.items():
            for entry in entries:
                if entry.get("name", "") == name:
                    ipc = dict(entry)
                    ipc["type"] = key
                    return ipc

    data = []

    for permission in perms:
        app_name = normalize_name(permission["app"])
        app = find_app(app_name)
        if app is None:
            raise Exception(f"App '{permission['app']}' not found for permission")

        ipc_name = normalize_name(permission["ipc"])
        ipc = find_ipc(ipc_name)
        if ipc is None:
            raise Exception(f"IPC '{permission['ipc']}' not found for permission")

        # Find the creator of this IPC (app with CREATE permissions)
        creator_app = None
        for other_permission in perms:
            if (
                other_permission["ipc"] == permission["ipc"]
                and "CREATE" in other_permission["allow"]
            ):
                other_app_name = normalize_name(other_permission["app"])
                creator_app = find_app(other_app_name)
                break

        data.append(
            {
                "app": app,
                "ipc": ipc,
                "permissions": permission["allow"],
                "creator": creator_app,
            }
        )

    return data


def build_output_files_data(pkg_name: str) -> dict:
    return {
        "te_file": f"{pkg_name}.te",
        "fc_file": f"{pkg_name}.fc",
        "if_file": f"{pkg_name}.if",
        "qm_dropin_file": f"{pkg_name}.conf",
        "build_script_file": "build.sh",
        "make_file": "Makefile",
        "spec_file": f"{pkg_name}.spec",
        "container_file": "Containerfile",
    }
