import csv

from accommodation import SummitException
from accommodation.models import Attendee, Venue


def parse_attendees(csv_data):
    """Parse data in following format:

        attendee name, venue A name, venue B name
        jack, yes, yes
        gill, yes, no
    """
    attendees = []
    venues = []
    for i, row in enumerate(csv.reader(csv_data)):
        row = [v.strip() for v in row]
        if not row or all(not v for v in row):
            continue
        if i == 0:
            venues = row[1:]
            continue

        name = row[0]
        prefs = set()
        attendee_pref_row = row[1:]
        if not any(attendee_pref_row):
            # user has not preferences declared
            prefs = set(venues)
        else:
            if len(attendee_pref_row) != len(venues):
                raise SummitException("Row count mismatch")

            for yn, venue_name in zip(attendee_pref_row, venues):
                if _check_yes_no(yn):
                    prefs.add(venue_name)

        attendees.append(Attendee(name, prefs))

    return attendees


def _check_yes_no(value):
    value = value.lower()
    if value.startswith('yes'):
        return True
    if value.startswith('no'):
        return False
    raise SummitException(f"Unrecognised preference value '{value}'. Value must start with 'yes' or 'no'")


def parse_venues(raw_venues):
    def _get_venue(raw):
        name, capacity = raw.rsplit(':', 1)
        try:
            capacity = int(capacity)
        except ValueError:
            raise SummitException(f"capacity must be an int: {raw}")

        return Venue(name, capacity)

    return [_get_venue(raw) for raw in raw_venues]
