SVSync Types
============

There are many types found in this library.
Each providing unique functionality that may be useful in some situations and harmful in others.

Items listed below are implemented.

    * **Shared**: cache other nodes' data to help spread their data!
    * **Health**: only track all nodes' aliveness, ensure that everyone is healthy! (only uses sync interests)

Items listed below are not implemented yet and will be added in the future!

    * **Prefetch**: send interests ahead of time to get data 1/2 RTT, reducing latency.
    * **Pubsub**: keep your unique data name and just use a mapping! publish and subscribe to data streams.
    * **Prefixed**: need multiple channels or need to 'reset' the state vector? control multiple prefixes.
    * **Uncapped**: automatic data segmentation, no more publication size limits!
    * **Secret**: keep things confidential with encryption. no unauthorized node needs to know who's in the system!
    * **Feed**: trying to reduce NFD prefix registrations? manually feed the interests!

Additionally, multiple types will later be combined to give users of this library ultimate functionality.

If you find one of the above types useful for your application or simply have a new type idea, please open an issue_!


.. _issue: https://github.com/justincpresley/ndn-python-svs/issues