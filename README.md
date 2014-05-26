System y
========

__System y__ (y/OS) is an overlay for POSIX-compliant systems to provide a environment to run massive distributed Python 3 as a SSI - at least in some respect. y/OS is not a new operating system, but a set of applications that support a particular programming model.

y/OS provides IPC, single process namespace and load balancing.

Applications that y/OS executes are __tasklets__, ie. special Python classes that use callback-based programming. Those that conform to some specifications can be freezed, migrated across y/OS __frames__ (ie. systems that are part of y/OS cluster), or checkpointed for error recovery.

Those tasklets that utilize local handles (sockets, files, DB connections) will not be eligible for migration.

Project will consist of some subprojects:

* ypage - y/Page - an enterprise-class y/OS runtime
* yos - y/OS Interface - a specification of application interface
* examples - a set of y/OS tasklet examples
* yframe - y/Frame - page coordinator on one node
* sysmultiplex - a interconnect facility to link multiple nodes into a SSI system

Also, extra tools are planned to empower y/OS:

* gigasaur - frame health monitoring utility
* supportelement - a SSH/telnet based admin command tasklet to manage the system with