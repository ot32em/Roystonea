from Roystonea.scripts.include import message

def create(name, caller_addr = None):
    values = message.spec[name][:]
    if "Req" in name:
        values += [caller_addr]
    return getattr(message, name)(*values)

