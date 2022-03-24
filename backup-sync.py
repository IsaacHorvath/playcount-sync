#!/usr/bin/python

import jaydebeapi

if ( __name__ == "__main__"):
   asdb1 = "./backup1/airsonic"
   asdb2 = "./backup2/airsonic"
   asdb = "./db/airsonic"

   # Open the Airsonic HSQLDB
   print("Opening Airsonic backup database 1 : " + asdb1)
   bconn1 = jaydebeapi.connect("org.hsqldb.jdbcDriver", "jdbc:hsqldb:"+asdb1, ["sa", ""], "hsqldb/lib/hsqldb.jar",)
   curs = bconn1.cursor()
   curs.execute("SELECT play_count,artist,album,title FROM MEDIA_FILE WHERE type=\'MUSIC\' AND play_count>0")
   bckp1 = curs.fetchall()
   print("Found " + str(len(bckp1)) + " entries with play_count > 0")
   bconn1.close()
   
   print("Opening Airsonic backup database 2 : " + asdb2)
   bconn2 = jaydebeapi.connect("org.hsqldb.jdbcDriver", "jdbc:hsqldb:"+asdb2, ["sa", ""], "hsqldb/lib/hsqldb.jar",)
   curs = bconn2.cursor()
   curs.execute("SELECT play_count,artist,album,title FROM MEDIA_FILE WHERE type=\'MUSIC\' AND play_count>0")
   bckp2 = curs.fetchall()
   print("Found " + str(len(bckp2)) + " entries with play_count > 0")
   bconn2.close()


   print("Opening target Airsonic database : " + asdb)
   conn = jaydebeapi.connect("org.hsqldb.jdbcDriver", "jdbc:hsqldb:"+asdb, ["sa", ""], "hsqldb/lib/hsqldb.jar",)
   conn.jconn.setAutoCommit(True)
   curs = conn.cursor()

   # Add Rhythmbox playcounts to Airsonic table
   print("Adding backup play counts to Airsonic...")
   for entry in bckp1 + bckp2:
       curs.execute("""UPDATE MEDIA_FILE 
                          SET play_count = play_count + ?
                             WHERE artist = ?
                             AND album = ?
                             AND title = ?
                             AND type=\'MUSIC\'""", entry);
   
   # Clean up and shutdown properly to commit changes
   print("Finished! Cleaning up...")
   curs.execute('SHUTDOWN')
   
   # Commit and close
   conn.close()

