# playcount-sync

Use Python to sync a Rhythmbox xml database to an Airsonic HSQLDB

Requires JPype and JayDeBeApi. Use: `pip install JPype1 JayDeBeApi`

So far this just adds a new HSQLDB table, so there will be no effect on either player yet. Todo:
- full playcount sync
- add default database locations
- add command line options for paths, sync options
- support for more music players
