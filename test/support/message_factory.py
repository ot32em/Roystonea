from Roystonea.scripts.include import message

def create(name):
    return getattr(message, name)(*message.spec[name])

