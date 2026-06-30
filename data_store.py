import json
from datetime import UTC, datetime
from pathlib import Path

from seed_data import SEED_FILES

DATA_DIR = Path(__file__).parent / "data"


def utc_now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_json(filename: str) -> list[dict]:
    path = DATA_DIR / filename
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def save_json(filename: str, data: list[dict]) -> None:
    path = DATA_DIR / filename
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)
        file.write("\n")


def ensure_data_files() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for filename, seed_data in SEED_FILES.items():
        path = DATA_DIR / filename
        if not path.exists():
            save_json(filename, seed_data)


def find_customer(customer_id_or_email: str) -> dict | None:
    needle = customer_id_or_email.strip().lower()
    for customer in load_json("customers.json"):
        if customer["id"].lower() == needle or customer["email"].lower() == needle:
            return customer
    return None


def find_ticket(ticket_id: str) -> dict | None:
    for ticket in load_json("tickets.json"):
        if ticket["id"] == ticket_id:
            return ticket
    return None


def next_id(prefix: str, existing_ids: list[str]) -> str:
    numbers = []
    for item_id in existing_ids:
        if item_id.startswith(prefix):
            suffix = item_id[len(prefix) :]
            if suffix.isdigit():
                numbers.append(int(suffix))
    next_number = max(numbers, default=0) + 1
    width = 3 if prefix in ("ref_", "aud_") else 4
    return f"{prefix}{next_number:0{width}d}"


def add_audit_log(
    action: str,
    resource_type: str,
    resource_id: str,
    details: dict | None = None,
) -> None:
    logs = load_json("audit_logs.json")
    entry = {
        "id": next_id("aud_", [log["id"] for log in logs]),
        "timestamp": utc_now(),
        "action": action,
        "resource_type": resource_type,
        "resource_id": resource_id,
        "details": details or {},
    }
    logs.append(entry)
    save_json("audit_logs.json", logs)


def ticket_counts_by_status(customer_id: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for ticket in load_json("tickets.json"):
        if ticket["customer_id"] != customer_id:
            continue
        status = ticket["status"]
        counts[status] = counts.get(status, 0) + 1
    return counts


def customer_summary(customer: dict) -> dict:
    return {
        "id": customer["id"],
        "name": customer["name"],
        "email": customer["email"],
        "company": customer["company"],
        "plan": customer["plan"],
        "status": customer["status"],
    }


def ticket_summary(ticket: dict) -> dict:
    return {
        "id": ticket["id"],
        "customer_id": ticket["customer_id"],
        "subject": ticket["subject"],
        "status": ticket["status"],
        "priority": ticket["priority"],
        "created_at": ticket["created_at"],
        "updated_at": ticket["updated_at"],
        "assigned_to": ticket["assigned_to"],
        "tags": ticket["tags"],
    }
