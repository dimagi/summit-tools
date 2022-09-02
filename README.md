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

### Randomizing results
Each run of the command will randomize the attendee order before performing the assignment. The command
output will include the random seed that was used:

```
==> Random Seed: 1043
```

To generate reproducible results pass the seed number to the command with `--seed <random integer>`

### Technical notes
This tool models the venue assignment as a [bipartite graph][1] and uses a [maximum matching algorithm][2] to
perform the assignments.

In the instance that an attendee fails to be matched to one of their preferences the tool falls back to
assigning the attendee to the first venue that has capacity.

[1]: https://en.wikipedia.org/wiki/Bipartite_graph
[2]: https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.csgraph.maximum_bipartite_matching.html

## GDT Summit 2022

1. Get data from Google Form
2. Delete the following columns:
   - 'Timestamp'
   - 'I have read and understand the disclaimers.'
   - 'Would you like to record your preferences?'
3. Add in any attendees who have not completed the survey (leave the preferences blank)
4. Save as CSV
5. Run the tool

```
python cli.py path/to/summit_accom.csv \
    -v "Main site: Bush camp":22 \
    "Main site: Guinea Fowl Lodge":13 \
    "Main site: Guinea Fowl Lodge - Log Cabin":4 \
    "Raptor Rise (various rooms)":14 \
    "Reflections Guest Farm (various rooms)":7
```
