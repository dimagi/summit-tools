import dataclasses

from accommodation import SummitException


@dataclasses.dataclass
class Venue:
    name: str
    capacity: int
    assigned: list = dataclasses.field(default_factory=list)

    def has_capacity(self):
        return self.capacity > self.used_capacity

    @property
    def used_capacity(self):
        return len(self.assigned)

    def venue_row(self):
        return [self] * self.capacity

    def assign(self, attendee: "Attendee"):
        if not self.has_capacity():
            raise SummitException(f"No more capacity at '{self.name}'")

        self.assigned.append(attendee)
        attendee.assign(self)

    def __str__(self):
        return f"{self.name}: Capacity (used,total): {self.used_capacity} / {self.capacity}"


@dataclasses.dataclass
class Attendee:
    name: str
    preferences: set = dataclasses.field(default_factory=set)
    venue: "Venue" = None
    got_preference: bool = None

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

    def assign(self, venue):
        self.venue = venue
        self.got_preference = venue.name in self.preferences
