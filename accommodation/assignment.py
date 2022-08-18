import itertools
import logging

from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import maximum_bipartite_matching

log = logging.getLogger("summit")


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


def check_capacity(venues, attendees):
    total_capacity = sum(venue.capacity for venue in venues)
    if total_capacity < len(attendees):
        raise Exception("Not enough capacity")


def get_preference_graph(venues, attendees):
    """Build the CSR Matrix for attendees venue preference"""
    return csr_matrix([
        attendee.get_matrix_row(venues) for attendee in attendees
    ])
