import pystache

def template(source, destination, values):
    source = open(os.path.join(os.path.dirname(__file__), "templates/%s", source)).read()
    destination_file = open(destination, 'w')

    content =  pystache.render(source, values)
    if destination_file:
        destination_file.write(content)
        destination_file.close()
        return True

    return False
    
