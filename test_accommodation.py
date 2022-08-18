import random
from accommodation import Venue, Attendee, assign_venues, sort_attendees, parse_attendees, get_preference_graph, \
    assign_rooms


def setup_module():
    random.seed(0)


def get_venues():
    return [
        Venue('a', 2),
        Venue('b', 1),
        Venue('c', 3),
    ]


def test_get_matrix():
    matrix = get_preference_graph(get_venues(), [
        Attendee('1'),
        Attendee('2', {"a"}),
        Attendee('3', {"a", "b"}),
        Attendee('4', {"a", "b", "c"}),
        Attendee('5', {"b", "c"}),
        Attendee('6', {"c"}),
    ])
    assert matrix.toarray().tolist() == [
        [1, 1, 1, 1, 1, 1],
        [1, 1, 0, 0, 0, 0],
        [1, 1, 1, 0, 0, 0],
        [1, 1, 1, 1, 1, 1],
        [0, 0, 1, 1, 1, 1],
        [0, 0, 0, 1, 1, 1],
    ]



def test_sort_order():
    attendees = [
        Attendee('1'),
        Attendee('2', {"a"}),
        Attendee('3', {"a", "b"}),
        Attendee('4', {"a", "b", "c"}),
        Attendee('5', {"b", "c"}),
        Attendee('6', {"c"}),
    ]

    names = [a.name for a in sort_attendees(attendees, 4)]
    assert names == ['6', '2', '3', '5', '4', '1']


def test_basic():
    attendees = [
        Attendee('1', {"a"}),
        Attendee('2', {"a"}),
        Attendee('3', {"c"}),
        Attendee('4', {"c"}),
        Attendee('5', {"c"}),
    ]

    assign_rooms(get_venues(), attendees)
    for attendee in attendees:
        assert attendee.venue
        assert attendee.venue.name in attendee.preferences


def test_not_first_choice():
    attendees = [
        Attendee('1', {"a"}),
        Attendee('2', {"a"}),
        Attendee('3', {"a"}),
        Attendee('4', {"c"}),
        Attendee('5', {"c"}),
    ]

    venues = get_venues()
    assign_rooms(venues, attendees)
    for attendee in attendees:
        assert attendee.venue
        assert [(a.name, a.venue.name) for a in attendees] == [
            ('1', 'a'),
            ('2', 'a'),
            ('3', 'b'),
            ('4', 'c'),
            ('5', 'c'),
        ]


def test_assigned_to_capacity():
    attendees = [
        Attendee('1', {"c"}),
        Attendee('2', {"a", "b", "c"}),
        Attendee('3', {"b"}),
        Attendee('4', {"c"}),
        Attendee('5', {"a", "c"}),
        Attendee('6', {"b", "a"}),
    ]

    venues = get_venues()
    assign_rooms(venues, attendees)
    for attendee in attendees:
        assert attendee.venue
        assert [(a.name, a.venue.name) for a in attendees] == [
            ('1', 'c'),
            ('2', 'a'),
            ('3', 'b'),
            ('4', 'c'),
            ('5', 'c'),
            ('6', 'a'),
        ]


def test_parse_attendees():
    csv_data = [l.strip() for l in """
    name,a,b,c
    1,yes,yes,yes
    2,yes,yes,no
    3,yes,no,yes
    4,""".splitlines() if l.strip()]

    attendees = parse_attendees(csv_data)
    assert [(a.name, a.preferences) for a in attendees] == [
        ("1", {"a", "b", "c"}),
        ("2", {"a", "b"}),
        ("3", {"a", "c"}),
        ("4", set()),
    ]
