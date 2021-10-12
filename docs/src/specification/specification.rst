Specification
=============

.. toctree::
    :maxdepth: 1
    :caption: Contents:

..
    ### API The API is defined [here](https://named-data.github.io/StateVectorSync/API.html). In addition though, you may add `_Thread` to the end of any SVSync class to push SVS to a thread (SVSync normally runs on the current thread and requires a non-blocking program). The thread classes are derived from `threading.Thread` and use the same arguments as the normal classes. However, instead of passing the NDNApp as the first argument, you pass the face and keychain at the end of the parameters. Please call `wait()` after `start()` to allow the thread to fully intalize SVS. Also refer to the thread example for defining the missing data callback function. Otherwise, the thread class acts just the same as the normal class. To make a new thread class based on a new SVS class from the SVSyncBase, make a new thread class derived from the SVSyncBase_Thread. In this new created class, you must define this function `async def function(self) -> None:`. Simply set `self.svs` to the new SVSync class.
