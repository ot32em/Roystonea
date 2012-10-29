import os
import pystache

def template(source, values, destination=None):
    source = open(os.path.join(os.path.dirname(__file__), "templates/%s" % (source))).read()
    content =  pystache.render(source, values)

    if destination==None:
        return content

    destination_file = open(destination, 'w')
    if destination_file:
        destination_file.write(content)
        destination_file.close()
        return content

    return False
    
