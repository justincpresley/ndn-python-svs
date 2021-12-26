Application User Interface
==========================

The API according to the specification is defined here_.

In addition though, the enhancements have changed the API or more so added to it.
Now, you may add `_Thread` to the end of any SVSync class to push SVSync to a thread (SVSync normally runs on the current thread and requires a non-blocking program)
The thread classes are derived from `threading.Thread` and use the same arguments as the normal classes. However, instead of passing the NDNApp as the first argument, you pass the face and keychain at the end of the parameters.
Please call `wait()` after `start()` to allow the thread to fully initialize SVS. Also refer to the thread example for defining the missing data callback function.
Otherwise, the thread class acts just the same as the normal class.

Please note. Thread classes expect a Uninitialized storage while non-thread classes expect the storage to already be initialized.

To make a new thread class based on a new SVS class from the SVSyncBase, make a new thread class derived from the SVSyncBase_Thread.
In this new created class, you must define this function `async def function(self) -> None:`. Simply set `self.svs` to the new SVSync class.

There is also a SVSyncShared and SVSyncShared_Thread classes as well that allow one to cache other's data.

Aside from other tool-related or extra minor classes, the API is defined as specificied. If you need help, take a look at the examples or
create an issue_.

.. _here: https://named-data.github.io/StateVectorSync/API.html
.. _issue: https://github.com/justincpresley/ndn-python-svs/issues