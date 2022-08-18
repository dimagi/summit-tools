import csv
import dataclasses
import itertools
import random
from operator import attrgetter

from scipy.sparse import csr_matrix
from scipy.sparse.csgraph._matching import maximum_bipartite_matching


@dataclasses.dataclass
class Venue:
    name: str
    capacity: int
    assigned: list = dataclasses.field(default_factory=list)

    def has_capacity(self):
        return self.capacity > len(self.assigned)

    @property
    def room_list(self):
        return [f"{self.name}:{i + 1}" for i in range(self.capacity)]

    def venue_row(self):
        return [self] * self.capacity

    def assign(self, attendee: "Attendee"):
        self.assigned.append(attendee)
        attendee.venue = self


@dataclasses.dataclass
class Attendee:
    name: str
    preferences: set = dataclasses.field(default_factory=set)
    jitter: int = dataclasses.field(default_factory=random.random)
    venue: "Venue" = None

    @staticmethod
    def sort_key(num_venues):
        """Sort attendees according to the length of their preferences (+ jitter)"""
        def _key(attendee):
            pref_len = len(attendee.preferences) or num_venues
            return pref_len + attendee.jitter
        return _key

    def pick(self, venues, force=False):
        for venue in venues:
            if not venue.has_capacity():
                continue

            in_preferences = not self.preferences or venue.name in self.preferences
            if force or in_preferences:
                venue.assign(self)
                return True
        return False

    def get_matrix_row(self, venues):
        """Return a list of 1's and 0's indicating which venues the attendee has preference for.
        Each element represents one room at a specific venue. The venues are used in the order
        they are passed in.

        For example:

            >>> venues = [Venue('a', capacity=2), Venue('b', capacity=3)]
            >>> venues[0].room_list
            ['a:1', 'a:2']

            >>> attendee = Attendee('joe', preferences={'a'})
            >>> attendee.get_matrix_row(venues)
            [1, 1, 0, 0, 0]

        """
        row = []
        for venue in venues:
            in_preferences = not self.preferences or venue.name in self.preferences
            yes_no = 1 if in_preferences else 0
            row.extend([yes_no] * venue.capacity)
        return row


def parse_attendees(csv_data, ):
    attendees = []
    venues = []
    for i, row in enumerate(csv.reader(csv_data)):
        if i == 0:
            venues = row[1:]
            continue

        name = row[0]
        prefs = set()
        for yn, venue_name in zip(row[1:], venues):
            if yn.lower().startswith('yes'):
                prefs.add(venue_name)

        attendees.append(Attendee(name, prefs))

    return attendees


def sort_attendees(attendees, num_venues):
    return list(sorted(attendees, key=Attendee.sort_key(num_venues)))


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
    graph = get_preference_graph(venues, attendees)
    matches = maximum_bipartite_matching(graph, perm_type='column')
    venue_rooms = list(itertools.chain.from_iterable([venue.venue_row() for venue in venues]))
    for i, room_index in enumerate(matches):
        attendee = attendees[i]
        if room_index < 0:
            raise Exception(f"Unable to assign {attendee.name}")
        venue = venue_rooms[room_index]
        venue.assign(attendee)



def assign_venues(venues, attendees):
    check_capacity(venues, attendees)

    unassigned = attendees
    force = False
    while True:
        at_least_one_assigned = False
        skipped = []
        for attendee in sort_attendees(unassigned, len(venues)):
            if not attendee.pick(venues, force):
                print(f"Unassigned: {attendee}")
                skipped.append(attendee)
            else:
                at_least_one_assigned = True
        if not skipped:
            break

        if not at_least_one_assigned:
            raise Exception("Unable to assign all attendees")
        unassigned = skipped
        force = True

