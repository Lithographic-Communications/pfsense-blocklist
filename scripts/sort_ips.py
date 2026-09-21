import ipaddress
from datetime import datetime, timezone
from pathlib import Path

LOG_DUPLICATES = True

blocklist_path = Path("blocklist.txt")
log_path = Path("duplicates.log")

original_content = blocklist_path.read_text()
networks = set()
duplicates = []

for line_number, raw_line in enumerate(original_content.splitlines(), 1):
    value = raw_line.strip()

    if not value or value.startswith("#"):
        continue

    try:
        if "/" not in value:
            suffix = "/128" if ":" in value else "/32"
            network = ipaddress.ip_network(value + suffix)
        else:
            network = ipaddress.ip_network(value, strict=False)
    except ValueError as error:
        raise SystemExit(
            f"Invalid IP address or range on line {line_number}: {value}"
        ) from error

    normalized_value = str(network)

    if network in networks:
        duplicates.append(
            f"Line {line_number}: {value} "
            f"(normalized as {normalized_value})"
        )
    else:
        networks.add(network)


def sort_key(network):
    return (
        network.version,
        int(network.network_address),
        network.prefixlen,
    )


normalized_content = "\n".join(
    str(network)
    if network.prefixlen != (32 if network.version == 4 else 128)
    else str(network.network_address)
    for network in sorted(networks, key=sort_key)
)

if normalized_content:
    normalized_content += "\n"

if normalized_content != original_content:
    blocklist_path.write_text(normalized_content)

if LOG_DUPLICATES:
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    log_lines = [
        f"Duplicate removal report - {timestamp}",
        f"Duplicates removed: {len(duplicates)}",
        "",
    ]

    if duplicates:
        log_lines.extend(duplicates)
    else:
        log_lines.append("No duplicates found.")

    log_path.write_text("\n".join(log_lines) + "\n")
