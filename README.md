# GTD Summit Tools

## Accommodation Assignment
Assign summit attendees to the various venues based on preference.

```shell
python cli path/to/csv -v "venue A":5 venueB:3
```

Venues are supplied on the command line: `"venue name":<capacity>`

The CSV file should contain the list of attendees and their accommodation preferences:

```csv
name, venue A, venueB
joe, yes, yes
gill, yes, no
jack, no, yes
molly,
```

`molly` has no preferences listed so may get assigned to any venue.
