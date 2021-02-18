# Burp Extension: Copy As FFUF

## Description

To be added

## Features

TODO 

## Requirements

- Python environment / Jython for Burp Suite

## Installation

TODO

## Known Issue

> __CompassSecurity__: If you are testing in a virtual machine, the clipboard can be messed up when
text is still selected after choosing a context menu entry. Therefore, when the
copy method of selected response data is choosen, the copying process is
started in a separate thread and copies the content after 1.5 seconds to the
clipboard. So you have to wait 1.5 seconds before switching to your reporting
tool.

## Author

- d3k4z

## Credits

- [burp-copy-requests-response](https://github.com/CompassSecurity/burp-copy-request-response)