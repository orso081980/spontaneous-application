"""
Backfill city and country fields for all existing Company records.

Address format expected: "Street, City PostalCode, Country"
  e.g. "Kerkstraat 106, 9050 Gent, Belgium"

Run from the project root (with venv active):
    python scripts/backfill_address_fields.py
"""
import os
import sys
import django

# Ensure the project root is on sys.path so "config.settings" is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from api.models import Company  # noqa: E402 — must come after django.setup()


def backfill() -> None:
    companies = Company.objects.all()
    updated = skipped = invalid = 0

    for company in companies:
        address = (company.address or '').strip()
        if not address:
            skipped += 1
            continue

        parts = [p.strip() for p in address.split(',')]
        if len(parts) != 3 or not all(parts):
            print(f"  SKIP (bad format) [{company.id}] {company.name!r}: {address!r}")
            invalid += 1
            continue

        new_city = parts[1]
        new_country = parts[2]

        if company.city == new_city and company.country == new_country:
            skipped += 1
            continue

        company.city = new_city
        company.country = new_country
        company.save(update_fields=['city', 'country'])
        print(f"  OK [{company.id}] {company.name!r} → city={new_city!r}, country={new_country!r}")
        updated += 1

    print(f"\nDone — updated: {updated}, skipped: {skipped}, invalid format: {invalid}")


if __name__ == '__main__':
    backfill()
