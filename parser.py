#!/usr/bin/python

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

   # Call when an elements ends
   def endElement(self, tag):
      if tag == "entry" and self.is_song:
         # End of song entry
         if "Magic" in self.song["artist"]:
            print(self.song)
         self.library.append(self.song)
         self.is_song = False
         self.song = {"artist":"", "album":"", "title":"", "play-count":0}
      self.tag = ""
      

   # Call when a character is read
   def characters(self, content):
      if self.tag in {"artist", "album", "title"} and self.is_song:
         self.song.update({self.tag: self.song[self.tag] + content})
      elif self.tag == "play-count" and self.is_song:
         self.song.update({"play-count": self.song["play-count"] + int(content)})
  
if ( __name__ == "__main__"):
   
   # create an XMLReader
   parser = xml.sax.make_parser()
   parser.setFeature(xml.sax.handler.feature_namespaces, 0)

   # use our custom MusicHandler
   Handler = MusicHandler()
   parser.setContentHandler(Handler)
   
   # parse the rhythmbox database
   parser.parse("rhythmdb.xml")
   print(len(Handler.library))

   import jaydebeapi
   conn = jaydebeapi.connect("org.hsqldb.jdbcDriver", "jdbc:hsqldb:./db/airsonic", ["sa", ""], "hsqldb/lib/hsqldb.jar",)
   curs = conn.cursor()

   # Create a table for Rhythmbox data
   curs.execute("""CREATE TABLE RHYTHMBOX (
                      artist VARCHAR(256),
                      album VARCHAR(256),
                      title VARCHAR(256),
                      play_count INT )""")

   # Insert our entries from the XML database
   for song in Handler.library:
      curs.execute("INSERT INTO RHYTHMBOX VALUES (?, ?, ?, ?)", 
         (song["artist"], song["album"], song["title"], song["play-count"]))

   # Change airsonic playcounts to Rhythmbox - TODO: find some substitute for GREATER so I can use the max value
   curs.execute('UPDATE MEDIA_FILE M SET M.play_count = \
                    ( IFNULL ( (SELECT R.play_count FROM RHYTHMBOX R WHERE R.artist=M.artist AND R.album=M.album and R.title=M.title LIMIT 1), 0) )')
   
   # Clean up so I can run it again
   curs.execute('DROP TABLE RHYTHMBOX')

#   curs.execute('SELECT artist,album,title from MEDIA_FILE')
 
   curs.close()
   conn.close()
