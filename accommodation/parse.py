import csv

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
            for yn, venue_name in zip(attendee_pref_row, venues):
                if yn.lower().startswith('yes'):
                    prefs.add(venue_name)

        attendees.append(Attendee(name, prefs))

    return attendees


def parse_venues(raw_venues):
    def _get_venue(raw):
        name, capacity = raw.split(':')
        try:
            capacity = int(capacity)
        except ValueError:
            raise Exception(f"capacity must be an int: {raw}")

        return Venue(name, capacity)

    return [_get_venue(raw) for raw in raw_venues]
