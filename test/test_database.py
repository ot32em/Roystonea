from Roystonea.scripts.database import *

def test_base_mixin():

    class A(BaseMixin):
        pass


    container = {'called': False}
    def test_handle_function(name):
        container['called'] = "Hello %s" % (name)

    A.register_event_callback("test_event", test_handle_function)

    assert ("test_event" in A.event_handlers_dict)
    assert (test_handle_function in A.event_handlers_dict["test_event"])

    A.trigger_event("test_event", "World")
    assert container['called'] == "Hello World"

    A.unregister_event_callback("test_event", test_handle_function)
    assert (test_handle_function in A.event_handlers_dict["test_event"]) == False


# Test only if database on
def test_vm_pooling_vmstatus_prepare_to_start():
    return

    container = {'called': False}
    def test_handle_function(record):
        container['called'] = True

    VM.register_event_callback("start_vm_record_inserted", test_handle_function)
    VM.pooling_vmstatus_prepare_to_start()

    assert container['called']


