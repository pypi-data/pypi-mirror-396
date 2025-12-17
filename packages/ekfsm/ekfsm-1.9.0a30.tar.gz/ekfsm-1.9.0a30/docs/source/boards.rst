.. _boards:

=========================
Supported Boards
=========================


.. toctree::
    :maxdepth: 1
    :glob:

    boards/*/*

Accessing Boards
----------------

Boards are appended to the system object and can be accessed e.g. via `system.ccu`.
Objects described in the board documentation are available via the boards object.

Example
~~~~~~~
>>> from ekfsm import System
>>> sm = System("path/to/config.yaml")
>>> sm.ccu.fan.fan_status()

IO4Edge Connections
-------------------

Objects attached to ekfsm IO4Edge devices rely on an active tcp connections to IO4Edge functionblocks implemented in the device firmware and propagated as MDNS services.

Those connections can be established in several ways.

Per-Command
~~~~~~~~~~~

This method automatically opens and closes the connection for each fired command.

**Example**

.. code-block:: python

    from ekfsm import System

    system = System("path/to/config.yaml")

    system.smc.i4e.ssm.kick() # Connection for watchdog kick opened and closed automatically


.. note::
    This method is the easiest to use and optimized for moderate ressource usage on unfrequent fired commands.

.. caution::
    For frequent successive commands, this method may introduce significant overhead due to repeated connection setups and teardowns.

Context Manager
~~~~~~~~~~~~~~~

This method uses a context manager to keep the connection open for the duration of the context.

**Example**

.. code-block:: python

    from ekfsm import System

    system = System("path/to/config.yaml")

    with system.smc.i4e.leds.client:
        # Inside this block, the connection is kept open
        system.smc.i4e.leds.led2.set(0, True)
        led2 = system.smc.i4e.leds.led2.get()
        assert led2 == (0, True)
        system.smc.i4e.leds.led5.set(3, True)
        led5 = system.smc.i4e.leds.led5.get()
        assert led5 == (3, True)
        system.smc.i4e.leds.led3.set(5, False)
        led3 = system.smc.i4e.leds.led3.get()
        assert led3 == (5, False)
    # Outside the block, the connection is closed

.. note::
    This method is recommended when a fixed set of multiple commands are fired in a frequent succession, as it reduces the overhead of connection setups and teardowns.

Persistent Connection
~~~~~~~~~~~~~~~~~~~~~

This method keeps the connection open for the lifetime of the object or until closed manually.

**Example**

.. code-block:: python

    from ekfsm import System
    system = System("path/to/config.yaml")

    # Open connection manually
    system.smc.i4e.leds.client.open()

    # Connection is now open for all commands
    system.smc.i4e.leds.led2.set(0, True)
    led2 = system.smc.i4e.leds.led2.get()
    assert led2 == (0, True)
    ...

    # Close connection manually
    system.smc.i4e.leds.client.close()

.. note::
    This method is useful when multiple commands are fired over an extended period, and the overhead of repeated connection setups is undesirable.

.. caution::
    For optimized ressource usage, it is not recommended to keep separate connections for many objects persistently open if not explicitly needed.
