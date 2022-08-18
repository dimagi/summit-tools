import argparse

from accommodation.assignment import assign_rooms
from accommodation.parse import parse_attendees, parse_venues


def main(venues, attendees):
    assign_rooms(venues, attendees)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('attendees', help='CSV file of attendees')
    parser.add_argument('-v', '--venues', nargs='+', help='List of venues with capacity e.g. venue1:5 venue2:6')

    args = parser.parse_args()

    with open(args.attendees, 'r') as f:
        attendees = parse_attendees(f)

    venues = parse_venues(args.venues)

    main(venues, attendees)
