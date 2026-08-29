sshuttle: where transparent proxy meets VPN meets ssh
=====================================================

As far as I know, sshuttle is the only program that solves the following
common case:

- Your client machine (or router) is Linux, FreeBSD, MacOS or Windows.

- You have access to a remote network via ssh.

- You don't necessarily have admin access on the remote network.

- The remote network has no VPN, or only stupid/complex VPN
  protocols (IPsec, PPTP, etc). Or maybe you *are* the
  admin and you just got frustrated with the awful state of
  VPN tools.

- You don't want to create an ssh port forward for every
  single host/port on the remote network.

- You hate openssh's port forwarding because it's randomly
  slow and/or stupid.

- You can't use openssh's PermitTunnel feature because
  it's disabled by default on openssh servers; plus it does
  TCP-over-TCP, which has `terrible performance`_.

.. _terrible performance: https://sshuttle.readthedocs.io/en/stable/how-it-works.html

Obtaining sshuttle
------------------

Please see the documentation_.

.. _Documentation: https://sshuttle.readthedocs.io/en/stable/installation.html

Documentation
-------------
The documentation for the stable version is available at:
https://sshuttle.readthedocs.org/

The documentation for the latest development version is available at:
https://sshuttle.readthedocs.org/en/latest/


Running as a service
--------------------
Sshuttle can also be run as a service and configured using a config management system:
https://medium.com/@mike.reider/using-sshuttle-as-a-service-bec2684a65fe


Connection resilience
---------------------
The client can keep a tunnel alive and reconnect after an unexpected
sshuttle/SSH failure. By default, the built-in ``ssh`` command is given
``ServerAliveInterval=15``, ``ServerAliveCountMax=3`` and
``TCPKeepAlive=yes`` options. Reconnects use bounded exponential backoff,
starting at one second and reaching a maximum of 30 seconds.

For example::

    sshuttle --keepalive-interval 10 --keepalive-count 3 \
        --backoff-maximum 60 --max-restarts 5 -r user@host 10.0.0.0/8

``--max-restarts`` counts failed runs and defaults to unlimited. Supplying
``-e/--ssh-cmd`` disables automatic SSH keepalive modification and preserves
the command exactly as supplied. Daemon mode retains its historical one-shot
behavior because it forks away from the supervising process.
