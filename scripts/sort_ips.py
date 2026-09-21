import ipaddress
from pathlib import Path

path = Path("ips.txt")
original_content = path.read_text()

networks = set()

for line_number, raw_line in enumerate(original_content.splitlines(), 1):
    value = raw_line.strip()

    if not value:
        continue

    try:
        if "/" not in value:
            suffix = "/128" if ":" in value else "/32"
            network = ipaddress.ip_network(value + suffix)
        else:
            network = ipaddress.ip_network(value, strict=False)

        networks.add(network)

    except ValueError as error:
        raise SystemExit(
            f"Invalid IP address or range on line {line_number}: {value}"
        ) from error


def sort_key(network):
    return (
        network.version,
        int(network.network_address),
        network.prefixlen,
    )


normalized_content = "\n".join(
    str(network)
    if network.prefixlen != (128 if network.version == 6 else 32)
    else str(network.network_address)
    for network in sorted(networks, key=sort_key)
)

if normalized_content:
    normalized_content += "\n"

if normalized_content != original_content:
    path.write_text(normalized_content)
