.. SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
..
.. SPDX-License-Identifier: LGPL-3.0-or-later

Tutorial 2: Adding electoral thresholds and other restrictions
**************************************************************

In this tutorial we will learn how to aplly certain rules to exclude or include candidates.

Spain - Local elections
=======================

In the Spanish local elections, seats are allocated by the :class:`highest averages <interregnum.methods.singlevote.HighestAveragesAllocator>` method with :func:`d'Hondt divisors <interregnum.divisors.dhondt_divisor>`, the same way we did in :ref:`tut_spain_eu_parliament`. But a restriction is added to the system:

- Candidates with a tallied vote that does not reach the 5% of all the valid vote are excluded from the apportionment.

In 2011, 27 seats were allocated to the city of `Algeciras <https://es.wikipedia.org/wiki/Algeciras>`_.

.. code-block:: yaml
    :linenos:
    :emphasize-lines: 5

    name: Elecciones Municipales - Algeciras 2011
    method: highest_averages
    method_params:
        divisor_f: dhondt
    exclude: valid_votes < 5%
    seats: 27
    candidates:
    -   name: "? en blanco"
        votes: 1444
    -   name: "! nulo"
        votes: 744
    -   name: "PP"
        votes: 22463
    -   name: "PSOE de Andalucía"
        votes: 8104
    -   name: "IULV-CA"
        votes: 5282
    -   name: "PA - EP-And"
        votes: 3356
    -   name: "UPyD"
        votes: 1339
    -   name: "JAU"
        votes: 620
    -   name: "CDL"
        votes: 362
    -   name: "PDMA"
        votes: 258
    -   name: "AuN"
        votes: 129

In line 5 we implemented the required threshold using an exclusion :class:`restriction <interregnum.district.restriction.Restriction>`. Let's see it with more details:

.. code-block:: yaml
    :linenos:
    :lineno-start: 5
    :emphasize-lines: 1

    exclude: valid_votes < 5%

Two fields can be used to define restrictions:

- :attr:`~interregnum.district.node.NodeContext.exclude`: candidates that comply with the restriction will be added to the exclusion list, so the allocator will not give seats to them.
- :attr:`~interregnum.district.node.NodeContext.include`: candidates that comply with the restriction will be added to the inclusion list, so the allocator will take them into account even if the are in the exclusion list too.

We used the attribute :attr:`valid_votes <interregnum.district.restriction.Attribute.VALID_VOTES>` because it is specified that the blank vote should be taken into account in addition to the vote to candidates.


Denmark - Folketing elections (first step)
==========================================

It can happen that the list that a party presents is shorter (a small party or an independent candidate) than the total number of seats allocated to the district.

Danish electoral system is complex, so for now we will only look at how a single district works:

Candidates are elected using the :class:`highest averages <interregnum.methods.singlevote.HighestAveragesAllocator>` method with :func:`d'Hondt divisors <interregnum.divisors.dhondt_divisor>`. Both parties and independent candidates can contend to the election. Independent candidates can only win 1 seat each.

Let's design the schema for the Copenhaguen district in 2011 (15 seats):

.. code-block:: yaml
    :linenos:
    :emphasize-lines: 19-24

    name: København
    seats: 15
    candidates:
    - name: "? blank"
      votes: 2588
    - name: "! void"
      votes: 1870
    # parties
    - {name: Socialdemokratiet, votes: 80705}
    - {name: Radikale Venstre, votes: 71264}
    - {name: Konservative Folkeparti, votes: 23262}
    - {name: SF - Socialistisk Folkeparti, votes: 52870}
    - {name: Liberal Alliance, votes: 24882}
    - {name: Kristendemokraterne, votes: 1185}
    - {name: Dansk Folkeparti, votes: 35887}
    - {name: Venstre, votes: 64914}
    - {name: Enhedslisten, votes: 70831}
    # independent candidates
    - {max_seats: 1, name: Tom Gillesberg, votes: 123}
    - {max_seats: 1, name: Klaus Trier Tuxen, votes: 161}
    - {max_seats: 1, name: Morten Versner, votes: 10}
    - {max_seats: 1, name: Mads Vestergaard, votes: 54}
    - {max_seats: 1, name: John Erik Wagner, votes: 43}
    - {max_seats: 1, name: Per Zimmermann, votes: 14}


When a candidate wins the quantity in :attr:`~interregnum.district.contenders.Contender.max_seats`, the allocator will ignore that candidate from that moment when assigning the remaining seats.


Life of Brian - Limiting the number of seats an alliance can win
================================================================

Seats to alliances can also be limited. Let's imagine a situation:

1st Century, Judea. The region is occupied by the Roman Empire, and `prophet Brian starts his teachings <https://en.wikipedia.org/wiki/Monty_Python%27s_Life_of_Brian>`_. The independentist movement is vibrant, but most of the independentist fighters disagree in the way they should fight. In order to reach some common ground, 10 of them are elected for the creation of a basic statute. In order to avoid concentration of power, only half of the members of a faction can be elected.

`The People's Front of Judea` is composed by only 4 members, therefore only 2 members can join the committee.


.. code-block:: yaml
    :linenos:
    :emphasize-lines: 5-7

    name: Statue for Judea Liberation Fronts
    seats: 10
    method: limited_voting
    alliances:
    - { name: "The People's Front of Judea", max_seats: 2 }
    - { name: "Judea People's Front", max_seats: 8 }
    - { name: "Judean People's Front", max_seats: 6 }
    candidates:
    - { name: "Reg", alliance: "The People's Front of Judea" }
    - { name: "Francis", alliance: "The People's Front of Judea" }
    - { name: "Loretta", alliance: "The People's Front of Judea" }
    - { name: "Judith Iscariot", alliance: "The People's Front of Judea" }
    ...

The :attr:`~interregnum.district.district.BallotsNode.alliances` field allows to define :attr:`~interregnum.district.contenders.Alliance.max_seats` to alliances.

The line 5 limits the number of seats that the alliance `The People's Front of Judea` can win to 2. If 2 of their members are elected, the allocation system will add the non-elected members to the exclusion list.

.. code-block:: yaml
    :linenos:
    :lineno-start: 5
    :emphasize-lines: 1

    - { name: "The People's Front of Judea", max_seats: 2 }
