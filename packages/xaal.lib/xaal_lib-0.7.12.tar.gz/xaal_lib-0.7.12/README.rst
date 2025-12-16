
xaal.lib
========
**xaal.lib** is the official Python stack to develop home-automation devices and gateways
with the xAAL protocol. For a full description of the protocol check out
http://recherche.imt-atlantique.fr/xaal/


Dependencies
~~~~~~~~~~~~
xaal.lib depends on :
 * cbor2
 * pysodium
 * configobj
 * coloredlogs
 * decorator
 * tabulate
 * aioconsole


Install
~~~~~~~
Please refer to the official `full documentation to install the lib in a virtualenv
<https://gitlab.imt-atlantique.fr/xaal/code/python/-/blob/main/README.rst>`_


Usage
~~~~~
The main goal of xaal.lib is to provide an API to easily develop devices & gateways.
**xaal.lib.Engine send / receive / parse to|from xAAL Bus**.


To receive / parse / display incoming xAAL messages, you can simply try something like
this:

.. code-block:: python

   from xaal.lib import Engine

   def display(msg):
       print(msg)

   eng = Engine()
   eng.subscribe(display)
   eng.run()

The Engine will call the display function every time it receive a xAAL message.

Let's take a look at a simple lamp device :

.. code-block:: python

   from xaal.lib import Device,Engine,tools

   # create and configure the lamp device, with a random address
   dev = Device("lamp.basic", tools.get_random_uuid())
   dev.product_id = 'Dummy Lamp'
   dev.url  = 'http://www.acme.org'
   dev.info = 'My fake lamp'

   # add an xAAL attribute 'light'
   light = dev.new_attribute('light')

   # declare two device methods ON & OFF
   def on():
       light.value = True

   def off():
       light.value = False

   dev.add_method('turn_on',on)
   dev.add_method('turn_off',off)

   # last step, create an engine and register the lamp
   eng = Engine()
   eng.add_device(dev)
   eng.run()


To avoid to rewrite the same code for each device, you can use the `xaal.schemas package <https://gitlab.imt-atlantique.fr/xaal/code/python/-/tree/main/libs/schemas>`_.
This package provides a set of predefined devices, you can use them as a template to create your own device.

.. code-block:: python

   from xaal.schemas import devices
   from xaal.lib import Engine

   # create and configure the lamp device
   dev = devices.lamp()

   # last step, create an engine and register the lamp
   eng = Engine()
   eng.add_device(dev)
   eng.run()


FAQ
~~~
The core engine run forever so how can I use it in webserver, GUI or to develop device
with IO. The whole API is absolutely not thread safe, so **don't use threads** unless you
exactly know what's going on. Anyways, you have several options to fix this issue:

* You can use you own loop and periodically call *eng.loop()*
  for example, you can do something like this:

  .. code:: python

     while 1:
         do_some_stuff()
         eng.loop()

* You can use a engine timer, to perform some stuff.

  .. code:: python

     def read_io():
         pass

     # call the read_io function every 10 sec
     eng.add_timer(read_io,10)
     eng.run()

* Use the **AsyncEngine**. Python version > 3.8 provides async programming with **asyncio** package.
  *AsyncEngine* use the same API as *Engine*, but it is a **asynchronous** engine. You can use
  *coroutines* in device methods, timers functions and callbacks. It provides additionals features
  like the *on_start* and *on_stop* callbacks.

* Use an alternate coroutine lib, you can use **gevent** or **greenlet** for example. Look at
  apps/rest for a simple greenlet example.
