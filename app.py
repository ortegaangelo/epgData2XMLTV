import datetime
import os
from optparse import OptionParser
import glob
import httplib
import urllib
import zipfile
from StringIO import StringIO
from xml.dom import minidom
from xml.dom.minidom import getDOMImplementation


class App:
    INPUT_PATH = 'epgdata_files'
    OUTPUT_PATH = 'output'
    PIN = '######################'
    DAY = 0
    URL = 'www.epgdata.com'
    DATEFORMAT = '%Y%m%d'

    def __init__(self):
        parser = OptionParser()
        parser.add_option("-i", "--input", help="The path for the input files.")
        parser.add_option("-o", "--output", help="The path for the output files.")
        parser.add_option("-p", "--pin", help="The pin code for epgdata.com")
        parser.add_option("-d", "--day", help="The day to retrieve from epgdata.com")
        (options, args) = parser.parse_args()

        if options.input is not None:
            self.INPUT_PATH = options.input
        if options.output is not None:
            self.OUTPUT_PATH = options.output
        if options.pin is not None:
            self.PIN = options.pin
        if options.day is not None:
            self.DAY = options.day

        # Clean old files
        self.cleanup()

        # Fetch new files
        if self.DAY != 0:
            self.fetch_data(self.DAY)
        else:
            while self.DAY <= 6:
                self.fetch_data(self.DAY)
                self.DAY += 1

        # Generated Merged File
        self.generate_merged('channel.xml')

    def cleanup(self):
        files = os.listdir(self.INPUT_PATH)
        for filename in files:
            try:
                splitted = filename.split('_')
                file_date = datetime.datetime.strptime(splitted[0], self.DATEFORMAT)
                date = (datetime.datetime.now() + datetime.timedelta(days=-1))
                if file_date < date:
                    os.remove('{}/{}'.format(self.INPUT_PATH, filename))
                    print '{} deleted.'.format(filename)

            except Exception:
                print '{} failed to delete.'.format(filename)

    def fetch_data(self, day):
        # Exists
        date = (datetime.datetime.now() + datetime.timedelta(days=day))
        files = os.listdir(self.INPUT_PATH)
        for filename in files:
            if filename.startswith(date.strftime(self.DATEFORMAT)):
                print 'Already fetched.'
                return

        # Fetch data
        params = urllib.urlencode(
            {'action': 'sendPackage', 'iOEM': 'vdr', 'dayOffset': self.DAY, 'pin': self.PIN, 'dataType': 'xml'})
        params = params.encode('ascii')
        headers = {'Content-type': 'application/x-www-form-urlencoded', 'Cache-Control': 'no-cache'}
        conn = httplib.HTTPConnection("www.epgdata.com")
        conn.request('GET', '/index.php?{}'.format(params), None, headers)
        response = conn.getresponse()
        content_type = response.getheader('content-type')
        print params
        print (content_type)
        print (response.status)

        if response.status == 200 and content_type == 'application/x-zip-compressed':
            # Content
            content = response.read()

            # Uncompress ZIP and save XML
            xml_zip = zipfile.ZipFile(StringIO(content))
            for name in xml_zip.namelist():
                uncompressed = xml_zip.read(name)
                output_filename = '{}/{}'.format(self.INPUT_PATH, name)
                output = open(output_filename, 'wb')
                output.write(uncompressed)
                output.close()

    def generate_merged(self, channel_path):
        # Channel File
        channel_doc = minidom.parse(channel_path)
        channel_items = channel_doc.getElementsByTagName('data')

        # New xml
        impl = getDOMImplementation()
        new_doc = impl.createDocument(None, "tv", None)
        top_element = new_doc.documentElement
        top_element.setAttribute("generator-info-name", 'EPGData2XMLTV')
        top_element.setAttribute("generator-info-url", 'http://github.com/angeloortega/EPGData2XMLTV')

        # Generate Channels
        for program in channel_items:
            child = self.generate_channel_element(program)
            top_element.appendChild(child)

        files = glob.glob(self.INPUT_PATH + "/*.xml")
        for xml_file in files:
            top_element = self.generate_program_data(top_element, xml_file)

        # Write to file
        xml = ['<?xml version="1.0" encoding="utf-8" standalone="yes"?>', top_element.toprettyxml()]
        file_handle = open(self.OUTPUT_PATH + "/mixed.xml", "wb")
        file_handle.write(''.join(xml))
        file_handle.close()

    def generate_program_data(self, parent, epg_path):

        # Program File
        epg_doc = minidom.parse(epg_path)
        epg_items = epg_doc.getElementsByTagName('data')

        # Generate Programs
        for program in epg_items:
            child = self.generate_program_element(program)
            parent.appendChild(child)

        return parent

    def generate_channel_element(self, data):
        id = self.get_value(data, 'ch4')
        display_name_0 = self.get_value(data, 'ch0')
        display_name_1 = self.get_value(data, 'ch1')
        display_name_2 = self.get_value(data, 'ch11')

        impl = getDOMImplementation()
        new_doc = impl.createDocument(None, "channel", None)
        top_element = new_doc.documentElement
        top_element.setAttribute("id", id)

        if display_name_0 is not None:
            display_name_node = new_doc.createElement("display-name")
            display_name_node.setAttribute("lang", 'de')
            display_name = new_doc.createTextNode(display_name_0)
            display_name_node.appendChild(display_name)
            top_element.appendChild(display_name_node)

        return top_element

    def generate_program_element(self, data):
        tv_channel_id = self.get_value(data, 'd2')
        start = self.get_value(data, 'd4')
        stop = self.get_value(data, 'd5')
        title = self.get_value(data, 'd19')
        subtitle = self.get_value(data, 'd20')
        description = self.get_value(data, 'd21')

        impl = getDOMImplementation()
        new_doc = impl.createDocument(None, "programme", None)
        top_element = new_doc.documentElement
        top_element.setAttribute("channel", tv_channel_id)
        top_element.setAttribute("start", datetime.datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
                                 .strftime('%Y%m%d%H%M%S +0000'))
        top_element.setAttribute("stop", datetime.datetime.strptime(stop, '%Y-%m-%d %H:%M:%S')
                                 .strftime('%Y%m%d%H%M%S +0000'))

        if title is not None:
            title_node = new_doc.createElement("title")
            title_node.setAttribute("lang", 'de')
            title_text = new_doc.createTextNode(title)
            title_node.appendChild(title_text)
            top_element.appendChild(title_node)

        if subtitle is not None:
            subtitle_node = new_doc.createElement("sub-title")
            subtitle_node.setAttribute("lang", 'de')
            subtitle_text = new_doc.createTextNode(subtitle)
            subtitle_node.appendChild(subtitle_text)
            top_element.appendChild(subtitle_node)

        if description is not None:
            desc_node = new_doc.createElement("desc")
            desc_node.setAttribute("lang", 'de')
            desc_text = new_doc.createTextNode(description)
            desc_node.appendChild(desc_text)
            top_element.appendChild(desc_node)

        return top_element

    @staticmethod
    def get_value(data, tag):
        elements = data.getElementsByTagName(tag)
        if elements.length > 0:
            element = elements[0]
            if element.childNodes.length > 0:
                return element.firstChild.data.encode('utf-8')
        return None


App()
