# EPGData2XMLTV

Use EPG Data from www.epgdata.com on your Kodi Simple IPTV Client.

Since epgdata.com only provides one xml file (in a different structure) a day,

I had to find a solution that automatically fetches the provided data and merges it into a xml file. 


## How it works

Get the current 6 days of epg data provided and merge them into a single xml file.
Data older than Current-Day - 1 is automatically cleaned up.
```
python app.py -p 12345678910
```

Only get a single day (0 = current day)
```
python app.py -p 12345678910 -d 0
```

Specify the input path, where the raw epgdata is fetched to.
Data older than Current-Day - 1 is automatically cleaned up.
```
python app.py -p 12345678910 -i /path/
```

Specify the output path for the "mixed" xml.
```
python app.py -p 12345678910 -o /path/
```

## Info

Check your playlist.m3u file and change the names according to the <ch0>-Tag in the channel.xml file. 
```
        <ch0>Romance TV</ch0>
```

## File Structure

epgdata_files = The input folder, all fetched data lies in there. 

**output = The output folder with the mixed.xml you can use on Kodi Simple IPTV Client.**

app.py = The application start file.

channel.xml = A list of channels used for converting the data from epgdata - Do not change this.
