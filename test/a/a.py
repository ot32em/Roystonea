

def get_unused_port( base_port, count):
    result_port = int(base_port)
    import os
    tmpdir = "tmp_fortest"
    if not os.path.exists( tmpdir ) :
        os.mkdir( tmpdir )
    used_ports = sorted( os.listdir( tmpdir )  )
    for used_port in used_ports :
        if int(used_port) == result_port:
            result_port= int(used_port)+ 1
    for i in range( count):
        os.mkdir( tmpdir +  "/" + str( result_port+i) )
    return result_port

