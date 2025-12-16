import os
import stat
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader


def render_template(template: str, template_dir: str, data: Dict[str, Any]) -> str:
    tmpl = Environment(loader=FileSystemLoader(template_dir)).get_template(template)
    return tmpl.render(data)


def generate_new_policy(data: dict, template_dir: str, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)

    files = data["output"]["files"]

    policy_fc_content = render_template("fc.tmpl", template_dir, data)
    policy_te_content = render_template("te.tmpl", template_dir, data)
    policy_if_content = render_template("if.tmpl", template_dir, data)
    policy_fc_file_name = files["fc_file"]
    with open(os.path.join(output_dir, policy_fc_file_name), "w") as f:
        f.write(policy_fc_content)
        f.flush()
    policy_te_file_name = files["te_file"]
    with open(os.path.join(output_dir, policy_te_file_name), "w") as f:
        f.write(policy_te_content)
        f.flush()
    policy_if_file_name = files["if_file"]
    with open(os.path.join(output_dir, policy_if_file_name), "w") as f:
        f.write(policy_if_content)
        f.flush()

    qm_dropin_content = render_template("qm_dropin.tmpl", template_dir, data)
    qm_dropin_file_name = files["qm_dropin_file"]
    with open(os.path.join(output_dir, qm_dropin_file_name), "w") as f:
        f.write(qm_dropin_content)
        f.flush()

    build_sh_content = render_template("build.sh.tmpl", template_dir, data)
    build_sh_file_name = files["build_script_file"]
    with open(os.path.join(output_dir, build_sh_file_name), "w") as f:
        f.write(build_sh_content)
        f.flush()
    st = os.stat(os.path.join(output_dir, build_sh_file_name))
    os.chmod(os.path.join(output_dir, build_sh_file_name), st.st_mode | stat.S_IEXEC)

    make_file_content = render_template("makefile.tmpl", template_dir, data)
    make_file_name = files["make_file"]
    with open(os.path.join(output_dir, make_file_name), "w") as f:
        f.write(make_file_content)
        f.flush()

    spec_file_content = render_template("spec.tmpl", template_dir, data)
    spec_file_name = files["spec_file"]
    with open(os.path.join(output_dir, spec_file_name), "w") as f:
        f.write(spec_file_content)
        f.flush()

    build_container_file_content = render_template("container.tmpl", template_dir, data)
    build_container_file_name = files["container_file"]
    with open(os.path.join(output_dir, build_container_file_name), "w") as f:
        f.write(build_container_file_content)
        f.flush()
