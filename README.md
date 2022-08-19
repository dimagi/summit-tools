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
The order of the venues provided is significant. Venues appearing earlier in the list will be
allocated first.


### Technical notes
This tool models the venue assignment as a [bipartite graph][1] and uses a [maximum matching algorithm][2] to
perform the assignments.

In the instance that an attendee fails to be matched to one of their preferences the tool falls back to
assigning the attendee to the first venue that has capacity.

[1]: https://en.wikipedia.org/wiki/Bipartite_graph
[2]: https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.csgraph.maximum_bipartite_matching.html
