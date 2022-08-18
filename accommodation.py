import csv
import dataclasses
import itertools
import logging

from scipy.sparse import csr_matrix
from scipy.sparse.csgraph._matching import maximum_bipartite_matching


log = logging.getLogger("summit")


@dataclasses.dataclass
class Venue:
    name: str
    capacity: int
    assigned: list = dataclasses.field(default_factory=list)

    def has_capacity(self):
        return self.capacity > len(self.assigned)

    def venue_row(self):
        return [self] * self.capacity

    def assign(self, attendee: "Attendee"):
        if not self.has_capacity():
            raise Exception(f"No more capacity at '{self.name}'")

        self.assigned.append(attendee)
        attendee.venue = self


@dataclasses.dataclass
class Attendee:
    name: str
    preferences: set = dataclasses.field(default_factory=set)
    venue: "Venue" = None

    def get_matrix_row(self, venues):
        """Return a list of 1's and 0's indicating which venues the attendee has preference for.
        Each element represents one room at a specific venue. The venues are used in the order
        they are passed in.

        For example:

            >>> venues = [Venue('a', capacity=2), Venue('b', capacity=3)]
            >>> attendee = Attendee('joe', preferences={'a'})

        Venue 'a' has 2 rooms and 'b' has 3 rooms so expect 5 elements in the result

            >>> attendee.get_matrix_row(venues)
            [1, 1, 0, 0, 0]

        """
        row = []
        for venue in venues:
            in_preferences = not self.preferences or venue.name in self.preferences
            yes_no = 1 if in_preferences else 0
            row.extend([yes_no] * venue.capacity)
        return row


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


def check_capacity(venues, attendees):
    total_capacity = sum(venue.capacity for venue in venues)
    if total_capacity < len(attendees):
        raise Exception("Not enough capacity")


def get_preference_graph(venues, attendees):
    """Build the CSR Matrix for attendees venue preference"""
    return csr_matrix([
        attendee.get_matrix_row(venues) for attendee in attendees
    ])


def assign_rooms(venues, attendees):
    """Perform the venue assignment based on attendees preferences.

    If an attendees preferences can not be met they will be assigned to the first
    venue in the list that has capacity.

    This will update both the venue and attendee objects with the assignments.
    """
    check_capacity(venues, attendees)
    graph = get_preference_graph(venues, attendees)
    matches = maximum_bipartite_matching(graph, perm_type='column')

    # one element per room per venue
    venue_row = list(itertools.chain.from_iterable([
        venue.venue_row() for venue in venues
    ]))

    unassigned = []
    for i, room_index in enumerate(matches):
        attendee = attendees[i]

        if room_index < 0:
            unassigned.append(attendee)
            continue

        venue = venue_row[room_index]
        venue.assign(attendee)

    if unassigned:
        log.warning("%s attendees could not be assigned their preference\n\t%s", len(unassigned), [
            attendee.name for attendee in unassigned
        ])

        # fall back to assigning to first venue that has capacity
        for attendee in unassigned:
            for venue in venues:
                if venue.has_capacity():
                    venue.assign(attendee)
                    break
            else:
                # should never happen so fail loud
                raise Exception("No capacity remaining")
