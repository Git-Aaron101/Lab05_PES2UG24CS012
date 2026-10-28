
"""Manage parking permits and scan parking zones."""

import json
import secrets
from datetime import datetime, timedelta
from pathlib import Path

PERMIT_FILE = Path("permits.json")
permits = {}
ZONES = ("A", "B", "C")


def register_permit(vehicle_plate, zone_id, zone_records=None):
    """Register a valid vehicle permit and return its permit number."""
    if not isinstance(vehicle_plate, str) or not vehicle_plate.strip():
        return None
    if zone_id not in ZONES:
        return None

    if zone_records is None:
        zone_records = []

    permit_no = f"P{secrets.randbelow(90000) + 10000}"
    expiry = datetime.now() + timedelta(days=180)
    permits[vehicle_plate] = {
        "zone": zone_id,
        "permit": permit_no,
        "expiry": expiry.strftime("%Y-%m-%d"),
    }
    zone_records.append((vehicle_plate, zone_id))
    return permit_no


def revoke_permit(vehicle_plate):
    """Remove a vehicle permit if it exists."""
    return permits.pop(vehicle_plate, None) is not None


def is_expired(vehicle_plate):
    """Return whether a vehicle's permit has expired."""
    permit = permits.get(vehicle_plate)
    if permit is None:
        return False

    try:
        expiry = datetime.strptime(permit["expiry"], "%Y-%m-%d")
    except (KeyError, TypeError, ValueError):
        return False

    return expiry.date() < datetime.now().date()


def scan_zone(zone_id, plates_seen):
    """Return plates without a valid permit for the scanned zone."""
    return [
        plate for plate in plates_seen
        if (
            plate not in permits
            or permits[plate]["zone"] != zone_id
            or is_expired(plate)
        )
    ]


def load_permit_database(file=PERMIT_FILE):
    """Load permits from a JSON file."""
    try:
        with open(file, "r", encoding="utf-8") as database:
            data = json.load(database)
        permits.clear()
        if isinstance(data, dict):
            permits.update(data)
    except (OSError, json.JSONDecodeError):
        permits.clear()


def save_permit_database(file=PERMIT_FILE):
    """Save permits to a JSON file."""
    with open(file, "w", encoding="utf-8") as database:
        json.dump(permits, database, indent=2)


def set_expiry(vehicle_plate, date_text):
    """Update a permit's expiry date using YYYY-MM-DD format."""
    if vehicle_plate not in permits:
        return False

    try:
        expiry = datetime.strptime(date_text, "%Y-%m-%d")
    except (TypeError, ValueError):
        return False

    permits[vehicle_plate]["expiry"] = expiry.strftime("%Y-%m-%d")
    return True


def main():
    """Run the parking permit demonstration."""
    load_permit_database()
    register_permit("KA01AB1234", "A")
    register_permit("KA05XY9999", "Z")
    register_permit("", "B")
    register_permit(None, "C")
    set_expiry("KA01AB1234", "2020-01-01")
    revoke_permit("MH12ZZ0000")

    print(
        "Flagged in zone A:",
        scan_zone(
            "A",
            ["KA01AB1234", "KA05XY9999", "TN09QQ1111"],
        ),
    )
    plate = input("Plate to revoke (Enter to skip): ").strip()
    if plate:
        revoke_permit(plate)

    save_permit_database()
    print("Permits on file:", len(permits))


if __name__ == "__main__":
    main()
