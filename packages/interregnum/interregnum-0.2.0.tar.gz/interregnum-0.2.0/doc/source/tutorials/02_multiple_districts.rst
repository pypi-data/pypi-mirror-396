.. SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
..
.. SPDX-License-Identifier: LGPL-3.0-or-later

Tutorial 3: Playing with more than one district
***********************************************

Until now, we limited th examples to one-district systems. But in the real world, systems contains multiple divisions. In this tutorial a new type of node will be introduced: the :class:`group <interregnum.district.Group>` of districts or nodes.

UK - General election (complete schema)
=======================================

Let's go back to the :ref:`tut_uk_general_election_const` tutorial. Then, we defined the system for just one constituency. Now, we will include all constituencies:

1) Create a group of nodes, and put our constituency (`Caerfyrddin`) into its divisions (candidates are not shown):

    .. code-block:: yaml
        :linenos:
        :emphasize-lines: 2-3

        name: 2024 UK General election
        type: group
        divisions:
        - name: Caerfyrddin
          method: first_past_the_post

2) Add the remaining 649 constituencies:

    .. code-block:: yaml
        :linenos:
        :emphasize-lines: 4-6,9-11

        name: 2024 UK General election
        type: group
        divisions:
        - name: Amber Valley
          method: first_past_the_post
        ...
        - name: Caerfyrddin
          method: first_past_the_post
        ...
        - name: West Tyrone
          method: first_past_the_post

3) Since all the constituencies share the same method, it will be easier if we define it once for all the divisions:

    .. code-block:: yaml
        :linenos:
        :emphasize-lines: 3

        name: 2024 UK General election
        type: group
        method: first_past_the_post
        divisions:
        - name: Amber Valley
        ...
        - name: Caerfyrddin
        ...
        - name: West Tyrone


   Now, all the constituencies will inherit the method defined by its parent. There are other properties that are inherited by children (see :class:`~interregnum.district.node.NodeContext`).


4) If we want to get an aggregated result (for example, get a result grouped by parties), a criterion can be added to the root node:

    .. code-block:: yaml
        :linenos:
        :emphasize-lines: 4-7

        name: 2024 UK General election
        type: group
        method: first_past_the_post
        # enable aggregated result
        aggregate: yes
        # group seats by parties
        groupby: "alliance"
        divisions:
        - name: Amber Valley
        ...
        - name: Caerfyrddin
        ...
        - name: West Tyrone
        ...

   Aggregated results can be controled by using the properties :attr:`~interregnum.district.Group.aggregate` and :attr:`~interregnum.district.Group.groupby`.

.. _tut_andalucia:

Spain - Andalusian regional election
====================================

Andalusian Parliament electoral system uses 8 districts, one per province. Each distrct apportions a number of seats using the :class:`highest averages <interregnum.methods.singlevote.HighestAveragesAllocator>` method with :func:`d'Hondt divisors <interregnum.divisors.dhondt_divisor>`. Candidates with less votes than the 3% of total valid votes in the district are excluded from the apportionment for that district.

The system for the Spanish Parliament would be exactly the same, but with 52 leaf districts.

.. code-block:: yaml
    :linenos:
    :emphasize-lines: 6

    name: Parlamento Andaluz 2015
    type: group
    method: highest_averages
    method_params:
        divisor_f: dhondt
    exclude: "valid_votes < 3%"
    divisions:
    -   name: Almería
        seats: 12
    -   name: Cádiz
        seats: 15
    -   name: Córdoba
        seats: 12
    -   name: Granada
        seats: 13
    -   name: Huelva
        seats: 11
    -   name: Jaén
        seats: 11
    -   name: Málaga
        seats: 17
    -   name: Sevilla
        seats: 18


Since ``include`` and ``exclude`` restrictions are inherited by chldren, the threshold is defined once by the root node, but applied at each province. A restriction that does not reference to node will use the district where it is been used as reference.
