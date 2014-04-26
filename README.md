System y
========

''System y'' (y/OS) is an overlay for POSIX-compliant systems to provide a environment to run massive distributed Python 3 as a SSI - at least in some respect. y/OS is not a new operating system, but a set of applications that support a particular programming model.

y/OS provides IPC, single process namespace and load balancing.

Applications that y/OS executes are ''tasklets'', ie. special Python classes that use callback-based programming. Those that conform to some specifications can be freezed, migrated across y/OS ''books'' (ie. systems that are part of y/OS cluster), or checkpointed for error recovery.

Those tasklets that utilize local handles (sockets, files, DB connections) will not be eligible for migration.
