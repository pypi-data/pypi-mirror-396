# ----------------------------------------------------------------------------
# Copyright (c) Omnissa, LLC. All rights reserved.
# This product is protected by copyright and intellectual property laws in the
# United States and other countries as well as by international treaties.
# ----------------------------------------------------------------------------

import os
import random
import string
from typing import Callable

import OpenSSL.crypto as crypto
from hcs_core.ctxp import profile
from InquirerPy import inquirer
from InquirerPy.base import Choice
import yaml

from ohcs.lcm.config import Config, load_config, save_config
from ohcs.common.utils import error_details, fail, good, run_cli, trivial


def pair_existing(org_id: str, customization_file: str, provider_id: str):
    def custom_fn(config):
        _verify_custom_provider(provider_id, fail_on_not_found=True)

    return _pair_impl(org_id, customization_file, custom_fn)


def pair_existing_or_new(org_id: str, customization_file: str):
    def custom_fn(config):
        if config.hcs.providerId:
            provider_id = _verify_custom_provider(config.hcs.providerId, fail_on_not_found=False)
            if not provider_id:
                trivial(
                    f"Previous configured provider instance {config.hcs.providerId} not found. A new one will be created."
                )

    return _pair_impl(org_id, customization_file, custom_fn)


def _pair_impl(org_id: str, customization_file: str, custom_fn: Callable[[Config], None]) -> Config:
    _login(org_id)
    _ensure_directories()
    config, config_file_path = _get_config(create_if_not_exists=True)
    config.hcs.orgId = org_id

    config.mqtt.host = profile.current().hcs.mqtt

    # workaround for feature stack
    if profile.current().hcs.url.find(".fs.devframe.cp.horizon.omnissa.com") > -1:
        config.mqtt.port = 8883

    custom_fn(config)

    output = _apply_pairing_plan(config.clientId, customization_file)
    if not output or not output.get("myProvider") or not output.get("myEdge"):
        fail("Failed to apply pairing plan.")

    provider_id = output["myProvider"]["id"]
    config.hcs.edgeId = output["myEdge"]["id"]
    config.hcs.providerId = provider_id
    cert_path, key_path = _request_cert(org_id, provider_id)
    config.mqtt.ssl.cert = cert_path
    config.mqtt.ssl.key = key_path
    save_config(config, config_file_path)
    trivial(f"Configuration updated: {config_file_path}")
    good("Pairing completed.")

    return config


def _delete_file(path: str):
    path = os.path.abspath(path)
    if not os.path.exists(path):
        return
    # On Windows, read-only files cannot be deleted without first removing the read-only attribute
    try:
        os.chmod(path, 0o600)  # Add write permission before deletion
    except Exception:
        pass  # If chmod fails, try deletion anyway
    os.unlink(path)
    trivial(f"File removed: {path}")


def reset(org_id: str, confirm: bool):
    config, config_file_path = _get_config(create_if_not_exists=False)
    if config is not None:
        if org_id and config.hcs.orgId and org_id != config.hcs.orgId:
            fail(
                f"The specified organization ID {org_id} does not match the existing configuration organization ID {config.hcs.orgId}."
            )
            return
        if not org_id:
            org_id = config.hcs.orgId
    if not org_id:
        trivial("No organization ID specified and no previous configuration found. Nothing to reset.")
    else:
        if not confirm:
            msg = "Are you sure you want to reset the pairing? This will delete cloud records and local configuration."
            confirm = inquirer.confirm(msg).execute()
            if not confirm:
                return 1

        provider_id = None
        if config:
            _login(org_id)
            if config.clientId:
                _destroy_pairing_plan(config.clientId)
            else:
                trivial("No client ID found in configuration. Nothing to destroy.")
            if config.hcs.edgeId:
                run_cli(f"hcs edge delete -y {config.hcs.edgeId} -w10m", inherit_output=False, raise_on_error=False)
            if config.hcs.providerId:
                run_cli(f"hcs provider delete -y {config.hcs.providerId}", inherit_output=False, raise_on_error=False)
                provider_id = config.hcs.providerId

        if provider_id:
            _delete_file(f"certs/lcm-{provider_id}-.key")
            _delete_file(f"certs/lcm-{provider_id}-.crt")
            _delete_file(f"certs/lcm-{provider_id}.key")
            _delete_file(f"certs/lcm-{provider_id}.crt")

    _delete_file("config.yml")
    _delete_file("certs/ca.crt")
    _delete_file(".ohcs_context.json")
    _delete_file(".demo-store")


def reset_all(org_id: str, confirm: bool):
    reset(org_id, confirm)
    custom_edge_ids = run_cli(
        "hcs edge list -s 'providerLabel $eq custom AND name $like lcm-plugin-' --ids", output_json=True
    )
    for edge_id in custom_edge_ids:
        run_cli(f"hcs edge delete -y {edge_id}", inherit_output=False, raise_on_error=False)

    first = True
    for edge_id in custom_edge_ids:
        if first:
            timeout = "10m"
            first = False
        else:
            timeout = "1m"
        run_cli(f"hcs edge delete -y {edge_id} -w{timeout}", inherit_output=False, raise_on_error=False)

    sites = run_cli("hcs site list", output_json=True)
    for site in sites:
        edges = site.get("edges", [])
        need_to_delete = True
        for edge in edges:
            if edge.get("edgeDeploymentId") not in custom_edge_ids:
                need_to_delete = False
                break
        if need_to_delete:
            run_cli(f"hcs site delete -y {site.get('id')}", inherit_output=False, raise_on_error=False)
    custom_provider_ids = run_cli(
        "hcs provider list --label custom --search 'name $like lcm-plugin-' --ids", output_json=True
    )
    for provider_id in custom_provider_ids:
        run_cli(f"hcs provider delete -y {provider_id}", inherit_output=False, raise_on_error=False)


def _apply_pairing_plan(deployment_id: str, customization_file: str):
    plan_file = "pairing.plan.yml"
    template_path = os.path.join(os.path.dirname(__file__), plan_file)
    with open(template_path, "r") as f:
        template = yaml.safe_load(f)

    template["deploymentId"] = deployment_id
    if not customization_file:
        customization_file = "pairing.override.properties"
        _create_file_from_template(
            "pairing.example.properties", customization_file, {"${deploymentId}": deployment_id}, overwrite=True
        )

    customization = {}
    with open(customization_file, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                customization[key.strip()] = value.strip()

    provider_name = customization.get("provider.name")
    provider_getLocationLat = customization.get("provider.geoLocationLat")
    provider_getLocationLong = customization.get("provider.geoLocationLong")
    site_name = customization.get("site.name")
    site_description = customization.get("site.description")
    edge_name = customization.get("edge.name")
    edge_description = customization.get("edge.description")
    edge_fqdn = customization.get("edge.fqdn")

    if provider_name:
        template["var"]["provider"]["name"] = provider_name
    if provider_getLocationLat:
        template["var"]["provider"]["geoLocationLat"] = provider_getLocationLat
    if provider_getLocationLong:
        template["var"]["provider"]["geoLocationLong"] = provider_getLocationLong
    if site_name:
        template["var"]["site"]["name"] = site_name
    if site_description:
        template["var"]["site"]["description"] = site_description
    if edge_name:
        template["var"]["edge"]["name"] = edge_name
    if edge_description:
        template["var"]["edge"]["description"] = edge_description
    if edge_fqdn:
        template["var"]["edge"]["fqdn"] = edge_fqdn

    with open(plan_file, "w") as f:
        yaml.safe_dump(template, f)
    trivial(f"Pairing plan file created: {plan_file}")

    trivial("Applying pairing plan ...")
    try:
        # TODO: inherite output and log error after the edge deployment failure is fixed
        run_cli(f"hcs plan apply -f {plan_file}")
    except Exception as e:
        # work around temp edge deployment failure
        msg = error_details(e)
        trivial(f"Failed to apply pairing plan: {msg}")

    ret = run_cli("hcs plan output --details", output_json=True)
    _delete_file(f"{deployment_id}.state.yml")
    return ret


def _destroy_pairing_plan(deployment_id: str):
    trivial("Destroying pairing plan ...")
    if not os.path.exists("pairing.plan.yml"):
        trivial("Pairing plan file not found. Skipping.")
        return
    run_cli("hcs plan destroy -f pairing.plan.yml", raise_on_error=False)
    _delete_file(f"{deployment_id}.state.yml")
    _delete_file("pairing.plan.yml")


def _login(org_id: str):
    trivial(f"Login Horizon Cloud Service with organization {org_id}...")
    run_cli(f"hcs login --org {org_id}", inherit_output=False)
    good("Login successful.")


def _get_config(create_if_not_exists: bool = True) -> tuple[Config, str]:
    config_file_path = os.path.abspath("config.yml")
    if os.path.exists(config_file_path):
        trivial(f"Found existing configuration: {config_file_path}")
        try:
            config = load_config(config_file_path, log_path=False)
            trivial(f"Client ID: {config.clientId}")
            trivial(f"Provider ID: {config.hcs.providerId}")
            return config, config_file_path
        except Exception as e:
            trivial(f"Error loading configuration: {e}.")

    if not create_if_not_exists:
        trivial("Previous configuration file not found.")
        return None, None

    trivial("Creating new configuration...")
    config = _create_default_config()
    trivial(f"Client ID: {config.clientId}")
    return config, config_file_path


def _ensure_directories():
    os.makedirs("certs", exist_ok=True)
    os.makedirs("logs", exist_ok=True)


def _identify_custom_provider():
    trivial("Identifying CUSTOM provider instance...")
    providers = run_cli("hcs provider list --label CUSTOM", output_json=True)

    if len(providers) == 0:
        fail("No CUSTOM provider instance found. ")
        return

    if len(providers) == 1:
        p = providers[0]
        good(f"Using CUSTOM provider instance '{p['name']}' ({p['id']}).")
        return p["id"]

    trivial(f"Multiple CUSTOM provider instances found: {', '.join([p['name'] for p in providers])}")
    trivial("Use '--provider' parameter to specify the provider instance to use.")

    choices = []
    for p in providers:
        choices.append(Choice(value=p["id"], enabled=True, name=f"{p['name']} ({p['id']}, {p['location']})"))
    provider_id = inquirer.select(
        message="Choose provider instance to reuse:",
        choices=choices,
    ).execute()
    if not provider_id:
        fail("No provider instance selected.")
    return provider_id


def _verify_custom_provider(provider_id: str, fail_on_not_found: bool = True):
    providers = run_cli("hcs provider list", output_json=True)
    for p in providers:
        if p["id"] == provider_id:
            if p["providerLabel"].lower() == "custom":
                good(f"Specified provider instance {provider_id} exists and is of type CUSTOM.")
                return p["id"]
            else:
                fail(f"Provider instance {provider_id} is of type {p['providerLabel']}, not a CUSTOM provider.")
                return
    if fail_on_not_found:
        fail(f"Provider instance {provider_id} not found.")


def _request_cert(org_id: str, provider_id: str):
    cn = f"lcm-{provider_id}"
    trivial(f"Requesting certificate, CN={cn} ...")
    csr, key = _generate_CSR(nodename=cn)
    cmd = f"hcs api --post --header Content-Type:application/x-pem-file /admin/v3/providers/instances/{provider_id}/certificate?org_id={org_id}"
    process = run_cli(cmd, input=csr, inherit_output=False, raise_on_error=True)

    ca = "-----BEGIN CERTIFICATE-----" + process.stdout.split("-----BEGIN CERTIFICATE-----")[-1]

    key_path = f"certs/{cn}.key"
    if os.path.exists(key_path):
        os.remove(key_path)
    with open(key_path, "w") as file:
        file.write(key)
    os.chmod(key_path, 0o400)

    crt_path = f"certs/{cn}.crt"
    with open(crt_path, "w") as file:
        file.write(process.stdout)
    with open("certs/ca.crt", "w") as file:
        file.write(ca)

    return crt_path, key_path


def _ascii(text: str) -> bytes:
    return text.encode("ascii")


def _generate_CSR(nodename: str, sans: list[str] = [], key_length: int = 4096):
    C = "US"
    ST = "California"
    L = "Palo Alto"
    ORG = "VMware, Inc."
    OU = "EUC"

    ss = []
    for i in sans:
        ss.append("DNS: %s" % i)
    subject_alt_name = ", ".join(ss)

    req = crypto.X509Req()
    req.get_subject().CN = nodename
    req.get_subject().countryName = C
    req.get_subject().stateOrProvinceName = ST
    req.get_subject().localityName = L
    req.get_subject().organizationName = ORG
    req.get_subject().organizationalUnitName = OU
    # Add in extensions
    base_constraints = [
        crypto.X509Extension(_ascii("keyUsage"), False, _ascii("Digital Signature, Non Repudiation, Key Encipherment")),
        crypto.X509Extension(_ascii("basicConstraints"), False, _ascii("CA:FALSE")),
    ]
    x509_extensions = base_constraints
    # If there are SAN entries, append the base_constraints to include them.
    if subject_alt_name:
        san_constraint = crypto.X509Extension(_ascii("subjectAltName"), False, _ascii(subject_alt_name))
        x509_extensions.append(san_constraint)
    req.add_extensions(x509_extensions)
    # Utilizes generateKey function to kick off key generation.
    key = crypto.PKey()
    key.generate_key(crypto.TYPE_RSA, key_length)

    req.set_pubkey(key)
    req.sign(key, "sha256")
    csr_pem = crypto.dump_certificate_request(crypto.FILETYPE_PEM, req).decode("ascii")
    private_key_pem = crypto.dump_privatekey(crypto.FILETYPE_PEM, key).decode("ascii")
    return csr_pem, private_key_pem


def create_stub_plugin_and_tutorial(config: Config) -> None:
    trivial("Creating stub plugin and tutorial ...")

    _create_file_from_template("../examples/lcm_plugin.py", "lcm_plugin.py", overwrite=False)

    _create_file_from_template(
        "../examples/tutorial.plan.yml",
        "tutorial.plan.yml",
        {
            "{{providerId}}": config.hcs.providerId,
            "{{edgeId}}": config.hcs.edgeId,
        },
        overwrite=True,
    )


def _create_file_from_template(
    template_relative_path: str, destination_path: str, replacements: dict[str, str] = None, overwrite: bool = False
) -> None:
    if os.path.exists(destination_path) and not overwrite:
        trivial(f"File already exists: {destination_path}. Skip creation.")
        return

    parts = template_relative_path.split("/")
    template_path = os.path.join(os.path.dirname(__file__), *parts)
    with open(template_path, "r") as f:
        content = f.read()
    if replacements:
        for key, value in replacements.items():
            new_content = content.replace(key, value)
            if new_content == content:
                raise Exception(f"Placeholder {key} not found in template {template_path}.")
            content = new_content
    with open(destination_path, "w") as f:
        f.write(content)
    trivial(f"File created: {destination_path}")


def _create_default_config() -> Config:
    template_config_path = os.path.join(os.path.dirname(__file__), "default_config.yml")
    config = load_config(template_config_path, log_path=False)
    config.clientId = random.choice(string.ascii_lowercase) + "".join(
        random.choices(string.ascii_lowercase + string.digits, k=3)
    )
    return config
