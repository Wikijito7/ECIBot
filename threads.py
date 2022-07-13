from threading import Thread

def launch(suspend_fun):
    try:
        print('launch >>> Launching thread')
        t = Thread(target=suspend_fun)
        t.start()
        print('launch >>> Thread launched')
    
    except Exception as e:
        print(f"launch >> There's an error launching the thread: {str(e)}")