from threading import Thread
import logging as log

def launch(suspend_fun):
    try:
        log.info('launch >>> Launching thread')
        t = Thread(target=suspend_fun)
        t.start()
        log.info('launch >>> Thread launched')
    
    except Exception as e:
        log.warning(f"launch >> There's an error launching the thread: {str(e)}")
