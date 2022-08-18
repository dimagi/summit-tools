# GTD Summit Tools

## Accommodation Assignment
Assign summit attendees to the various venues based on preference.

```shell
python cli.py accommodation/example/attendees.csv -v venue1:22 venue2:13 venue3:4 venue4:14 "Venue 5":7
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

### Venue priority
The order of the venues provided is significant. In certain cases the tool will prioritize
venues earlier in the list over ones later in the list.
