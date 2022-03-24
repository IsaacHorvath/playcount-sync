#!/usr/bin/python

import sys, os, getopt
import xml.sax
import jaydebeapi

class MusicHandler(xml.sax.ContentHandler):
   def __init__(self):
      self.tag = ""
      self.song = {"artist":"", "album":"", "title":"", "play-count":0}
      self.is_song = False
      self.library = []

   # Call when an element starts
   def startElement(self, tag, attributes):
      self.tag = tag
      if tag == "entry":
         etype = attributes["type"]
         if etype == "song":
            self.is_song = True

   # Call when an elements ends, add song into library dict
   def endElement(self, tag):
      if tag == "entry" and self.is_song:
         # End of song entry
         self.library.append(self.song)
         self.is_song = False
         self.song = {"artist":"", "album":"", "title":"", "play-count":0}
      self.tag = ""
      

   # Call when a character is read, collect into self.song if it is a song
   def characters(self, content):
      if self.tag in {"artist", "album", "title"} and self.is_song:
         self.song.update({self.tag: self.song[self.tag] + content})
      elif self.tag == "play-count" and self.is_song:
         self.song.update({"play-count": self.song["play-count"] + int(content)})


if ( __name__ == "__main__"):
   # Grab command line arguments
   rhdb = os.environ['HOME'] + "/.local/share/rhythmbox/rhythmdb.xml"
   asdb = "./db/airsonic"
   try:
      options, args = getopt.getopt(sys.argv,"hr:a:",["rhythmbox=","airsonic="])

      for o, arg in options:
         if o == '-h':
            print("Usage: parser.py -r <rhythmbox database> -a <airsonic database>")
            sys.exit()
         elif o in ("-r", "--rhythmbox"):
            rhdb = arg
         elif o in ("-a", "--airsonic"):
            asdb = arg
   except getopt.GetoptError:
      pass
   
   # Create an XMLReader
   parser = xml.sax.make_parser()
   parser.setFeature(xml.sax.handler.feature_namespaces, 0)

   # Use our custom MusicHandler
   Handler = MusicHandler()
   parser.setContentHandler(Handler)
   
   # Parse the rhythmbox database
   print("Scanning rhythmbox library: " + rhdb)
   parser.parse(rhdb)
   print("Found "+str(len(Handler.library))+" entries.")

   # Open the Airsonic HSQLDB
   print("Opening Airsonic database: " + asdb)
   conn = jaydebeapi.connect("org.hsqldb.jdbcDriver", "jdbc:hsqldb:"+asdb, ["sa", ""], "hsqldb/lib/hsqldb.jar",)
   conn.jconn.setAutoCommit(True)
   curs = conn.cursor()

   # Create a table for Rhythmbox data
   #curs.execute("""CREATE TABLE RHYTHMBOX (
   #                   artist VARCHAR(256),
   #                   album VARCHAR(256),
   #                   title VARCHAR(256),
   #                   play_count INT )""")

   # Insert our Rhythmbox entries from the XML database
   #for song in Handler.library:
   #   curs.execute("INSERT INTO RHYTHMBOX VALUES (?, ?, ?, ?)", 
   #      (song["artist"], song["album"], song["title"], song["play-count"]))

   # Add Rhythmbox playcounts to Airsonic table
   print("Adding Rhythmbox play counts to Airsonic...")
   for song in Handler.library:
       curs.execute("""UPDATE MEDIA_FILE 
                          SET play_count = play_count + ?
                             WHERE artist = ?
                             AND album = ?
                             AND title = ?
                             AND type=\'MUSIC\'""",
                       (song["play-count"], song["artist"], song["album"], song["title"]));

   # Shutdown properly to commit changes
   print("Finished! Cleaning up...")
   curs.execute('SHUTDOWN')
   
   # Commit and close
   conn.close()

