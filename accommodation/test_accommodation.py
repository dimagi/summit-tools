import random
from unittest.mock import patch

import pytest

from accommodation import SummitException
from .models import Attendee, Venue
from .assignment import assign_rooms, get_preference_graph
from .parse import parse_attendees, parse_venues


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
        assert attendee.got_preference


def test_check_capacity():
    venues = get_venues()
    capacity = sum(v.capacity for v in venues)
    attendees = [
        Attendee(str(i), {'a'})
        for i in range(capacity + 1)
    ]

    with pytest.raises(SummitException, match="Not enough capacity"):
        assign_rooms(venues, attendees)


def test_check_capacity_at_end():
    venues = get_venues()
    capacity = sum(v.capacity for v in venues)
    attendees = [
        Attendee(str(i), {'a'})
        for i in range(capacity + 1)
    ]

    with patch("accommodation.assignment.check_capacity", return_value=None), \
         pytest.raises(SummitException, match="No capacity remaining"):
            assign_rooms(venues, attendees)


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

    assert {a.name: a.got_preference for a in attendees} == {
        '1': True,
        '2': True,
        '3': False,
        '4': True,
        '5': True,
    }

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


@pytest.mark.parametrize("line,expected", [
    pytest.param("1,  yes,yes  ,  Yes", Attendee("1", {"a", "b", "c"}), id='trim whitespace'),
    pytest.param("2,yes,yes please,No", Attendee("2", {"a", "b"}), id='extra text'),
    pytest.param("2,YES,Yes,No", Attendee("2", {"a", "b"}), id='case sensitive'),
    pytest.param("4", Attendee("4", {"a", "b", "c"}), id='no preferences'),
    pytest.param("", None, id='blank'),
    pytest.param(",,,,", None, id='blank-cells'),
])
def test_parse_attendees(line, expected):
    csv_data = f"name,a,  b  ,c\n{line}\n".splitlines()
    attendees = parse_attendees(csv_data)
    if not expected:
        assert not attendees
    else:
        attendee = attendees[0]
        assert (attendee.name, attendee.preferences) == (expected.name, expected.preferences)


@pytest.mark.parametrize("line,message", [
    pytest.param("1,yes,hello", "Unrecognised.*", id='not yes or no'),
    pytest.param("2,yes,yes,no", "Row count mismatch", id='mismatched count'),
])
def test_parse_attendees_errors(line, message):
    csv_data = f"name,a,b\n{line}\n".splitlines()
    with pytest.raises(SummitException, match=message):
        parse_attendees(csv_data)


def test_get_venues():
    venues = parse_venues(["v1:3", "v2:5", "venue 3:1", "venue: great:8"])
    assert [v.name for v in venues] == ['v1', 'v2', 'venue 3', 'venue: great']
    assert [v.capacity for v in venues] == [3, 5, 1, 8]
