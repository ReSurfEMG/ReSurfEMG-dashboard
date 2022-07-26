import webbrowser  # For launching web pages
from index import server
from threading import Timer  # For waiting before launching web page
from waitress import serve



def open_browser():
    """
    Open browser to localhost
    """
    webbrowser.open_new('http://127.0.0.1:8080/')


Timer(1, open_browser).start()  # Wait a second and then start the web page
serve(server)
