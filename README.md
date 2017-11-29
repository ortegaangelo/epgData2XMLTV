# EPGData2XMLTV

Use EPG Data from www.epgdata.com on your Kodi Simple IPTV Client.
Since epgdata.com only provides one xml file (in a different structure) a day,
I had to find a solution that automatically fetches the provided data and merges it into a single xml file. 


## How it works

Get the current 6 days of epg data provided and merge them into a single xml file.

```
python app.py -p 12345678910
```

Only get a single day (0 = current day)
```
python app.py -p 12345678910 -d 0
```
