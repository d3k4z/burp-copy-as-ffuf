from burp import IBurpExtender, IContextMenuFactory, IHttpRequestResponse
from java.io import PrintWriter
from java.util import ArrayList
from javax.swing import JMenuItem
from java.awt import Toolkit
from java.awt.datatransfer import StringSelection
from javax.swing import JOptionPane
import subprocess
import tempfile
import threading
import time

class BurpExtender(IBurpExtender, IContextMenuFactory, IHttpRequestResponse):

    def create_ffuf(self, request):
        request_str = self.helpers.bytesToString(request)
        request_lines = request_str.strip().split('\n')

        # extract method, path, and protocol
        method, path, protocol = request_lines[0].split()

        # extract host header
        host_header = next((header for header in request_lines if header.startswith("Host:")), None)
        if not host_header:
            raise ValueError("Request does not contain a Host header")

        # extract host and port from host header
        host = host_header[len("Host:"):].strip()
        port = "80" if protocol == "HTTP/1.1" else "443"

        # construct the FFUF command
        url_prefix = "https" if port != "80" else "http"
        url = "{}://{}/{}".format(url_prefix, host, path.lstrip("/"))
        ffuf_cmd = "ffuf -X {} -u '{}'".format(method, url)

        # extract headers and add them to FFUF command
        headers = [header for header in request_lines[1:] if not header.startswith("Host:")]
        for header in headers:
            header_parts = header.split(':', 1)
            if len(header_parts) == 2:
                header_name, header_value = header_parts
                ffuf_cmd += " -H '{}:{}'".format(header_name.strip(), header_value.strip())

        return ffuf_cmd

    def str_to_array(self, string):
        return [ord(c) for c in string]

    def registerExtenderCallbacks(self, callbacks):
        callbacks.setExtensionName("Copy as ffuf command")

        stdout = PrintWriter(callbacks.getStdout(), True)
        stderr = PrintWriter(callbacks.getStderr(), True)

        self.helpers = callbacks.getHelpers()
        self.callbacks = callbacks
        callbacks.registerContextMenuFactory(self)

    def createMenuItems(self, invocation):
        self.context = invocation
        menuList = ArrayList()

        menuList.add(JMenuItem("Copy and transforms in ffuf command",
                actionPerformed=self.copyRequest))

        menuList.add(JMenuItem("Copy Request, ffuf command and tips",
                actionPerformed=self.copyAllRequest))

        return menuList

    def copyRequest(self, event):
        httpTraffic = self.context.getSelectedMessages()[0]
        httpRequest = httpTraffic.getRequest()
        httpRequest = self.helpers.bytesToString(httpRequest)

        RequestToFfuf = httpRequest

        ffuf_cmd = self.create_ffuf(RequestToFfuf)

        self.copyToClipboard(ffuf_cmd)

        t = threading.Thread(target=self.copyToClipboard, args=(data,True))
        t.start()

    def copyAllRequest(self, event):
        httpTraffic = self.context.getSelectedMessages()[0]
        httpRequest = httpTraffic.getRequest()
        httpRequest = self.helpers.bytesToString(httpRequest)

        RequestToFfuf = httpRequest

        ffuf_cmd = self.create_ffuf(RequestToFfuf)

        copy = "---------------------------------\nFrom {httpService}\n---------------------------------\nHEADERS:\n\nEOF\n\n{httpRequest}\nEOF\n---------------------------------\nFFUF COMMAND:\n\n{ffuf_cmd}\n_____________________________________________________________\nThese are the headers and the ffuf command of your request.\nHappy FUZZING and good luck! :)\n_____________________________________________________________"

        data = copy.format(httpService=httpTraffic.getHttpService(),httpRequest=httpRequest, ffuf_cmd=ffuf_cmd )

        self.copyToClipboard(data)

        t = threading.Thread(target=self.copyToClipboard, args=(data,True))
        t.start()

    def copyToClipboard(self, data, sleep=False):
        if sleep is True:
            time.sleep(1.5)

        data = self.helpers.bytesToString(data)
        systemClipboard = Toolkit.getDefaultToolkit().getSystemClipboard()
        systemSelection = Toolkit.getDefaultToolkit().getSystemSelection()
        transferText = StringSelection(data)
        systemClipboard.setContents(transferText, None)
        systemSelection.setContents(transferText, None)
