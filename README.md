# chromium-sync-server-gen
Utility to assemble a very basic version of chromium sync server from its repository

## Prerequisites
* [python > 2.7](https://www.python.org/downloads/release/python-279/)
* [Protocol Buffers compiler v2.6.1](https://github.com/google/protobuf/releases/download/v2.6.1/gprotoc-2.6.1-win32.zip)
* Virtualenv (optionally)

###Step 1
```batch
pip install protobuf==2.6.1
pip install tlslite==0.4.6
```
You should install those particular libraries' versions because they are currently used by Chromium project
After that you may run build.py with the following parameters
```batch
python build.py -p %USERPROFILE%\app\protoc\protoc.exe -t 39.0.2171.99 -o %USERPROFILE%\pyenvs\chrome-sync-server\server
```
```batch
python -B %USERPROFILE%\pyenvs\chrome-sync-server\server\sync_testserver.py --port 8079 --xmpp-port=8078
```
