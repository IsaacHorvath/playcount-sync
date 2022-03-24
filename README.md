# playcount-sync

Use Python to sync a Rhythmbox xml database to an Airsonic HSQLDB

Requires JPype and JayDeBeApi. Use: `pip install JPype1 JayDeBeApi`

One script is called rhythmbox-sync.py, which adds play counts from a rhythmbox XML database. The other is backup-sync.py, which adds play counts from previous Airsonic databases into a third Airsonic database. Neither script is very configurable, but you can use:
`rhythmbox-sync -r /path/to/rhythmdb.xml -a /path/to/airsonic/db`
To set the locations. The defaults are `~/.local/share/rhythmbox/rhthmdb` and an Airsonic database in the current folder. Defaults have been provided.

Todo:
- full playcount sync
- add command line options for sync options
- support for more music players
