import argparse
from operator import attrgetter

from accommodation import SummitException
from accommodation.assignment import assign_rooms
from accommodation.parse import parse_attendees, parse_venues


def main(venues, attendees):
    assign_rooms(venues, attendees)

    print("\n== Summary ==")
    got_pref_count = len([a for a in attendees if a.got_preference])
    not_pref = len(attendees) - got_pref_count
    print(f"{got_pref_count if not_pref else 'ALL'} attendees got one of their preferences")
    if not_pref:
        print(f"{not_pref} attendees did not get one of their preferences")

    print()
    print("\n".join(str(v) for v in venues))

    print("\n== Venue Assignments ==")
    print(f"venue name, capacity, capacity used, assigned attendees")
    for venue in venues:
        venue_attendees = ", ".join(sorted([a.name for a in venue.assigned]))
        print(f"{venue.name}, {venue.capacity}, {venue.used_capacity}, {venue_attendees}")

    print("\n== Attendee Assignments ==")
    print(f"attendee, assigned venue, got preference")
    for attendee in sorted(attendees, key=attrgetter('name')):
        got_preference = 'yes' if attendee.got_preference else 'no'
        print(f"{attendee.name},{attendee.venue.name},{got_preference}")


def check_venues(venues, attendees):
    preferences = set().union(*[attendee.preferences for attendee in attendees])
    venue_names = {venue.name for venue in venues}
    missing = preferences - venue_names
    if missing:
        missing = "', '".join(missing)
        raise SummitException(f"CSV file contains unknown venues: '{missing}'")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('attendees', help='CSV file of attendees')
    parser.add_argument('-v', '--venues', nargs='+', help='List of venues with capacity e.g. venue1:5 venue2:6')

    args = parser.parse_args()

    with open(args.attendees, 'r') as f:
        attendees = parse_attendees(f)

    venues = parse_venues(args.venues)

    try:
        check_venues(venues, attendees)
        main(venues, attendees)
    except SummitException as e:
        print(f"Error: {e}")
