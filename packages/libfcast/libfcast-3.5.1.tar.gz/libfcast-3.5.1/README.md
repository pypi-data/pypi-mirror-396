# Description
This is best-effort python implementation of the FCast protocol by FUTO: https://gitlab.futo.org/videostreaming/fcast

**I'm not affiliated nor endorsed by FUTO**

Currently only protocol version 3 is targeted

# Installation

``` pip install libfcast ```

# Usage

Send message:
```
import fcast

fc = fcast.FCastSession(<IP/Host>)
fc.connect()
fc.send(fcast.message.Ping())
```

Handle received messages:
```
import fcast

def callback(msg: fcast.message.Message):
	<do stuff>

fc = fcast.FCastSession(<IP/Host>)
fc.connect()
fc.subscribe((fcast.message.PingMessage, callback))
fc.receive()	
```

Run receive loop in a separate thread:
```
import fcast
from threading import Thread

def callback(msg: fcast.message.Message):
    <do stuff>

fc = fcast.FCastSession(<IP/Host>)
fc.connect()
fc.subscribe((fcast.message.PingMessage,callback))
recv_thread = Thread(target=fc.receive)
recv_thread.start()
<do other stuff>
fc.disconnect()
recv_thread.join()
```
