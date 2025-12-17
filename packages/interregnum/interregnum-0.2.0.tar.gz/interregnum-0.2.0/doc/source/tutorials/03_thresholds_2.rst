.. SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
..
.. SPDX-License-Identifier: LGPL-3.0-or-later

Tutorial 4: More on thresholds
******************************

In this tutorial we will specify restrictions that requires results on certains nodes.

Several ways on restricting parties are found in Spanish regional elections, so we will try to replicate three regional electoral systems: Valencia, Extremadura and Islas Canarias. These systems are similar to :ref:`tut_andalucia` from the previous tutorial.

Spain - Comunitat Valenciana (regional election)
=================================================

In Comunitat Valenciana, parties must reach 5% of the total vote in the whole region (invalid vote included) or else they will be excluded from apportionments.

.. code-block:: yaml
    :linenos:
    :emphasize-lines: 2,7

    name: Cortes Valencianas 2011
    key: comunitat
    type: group
    method: highest_averages
    method_params:
        divisor_f: dhondt
    exclude: "comunitat.alliance_total_votes < 5% => id"
    divisions:
    - name: Alicante
      seats: 35
    - name: Castellón
      seats: 24
    - name: Valencia
      seats: 40


We can see 4 differences from previous examples:

1) In line 2, a short and unique :attr:`~interregnum.district.node.Node.key` is defined for the root node. When no key is explicitly defined, the node :attr:`~interregnum.district.node.Node.name` will be used as key.

2) The vote threshold is referencing the root node (with key ``comunitat``), so in each leaf node, each party will be evaluated against the vote visible at the root node.

3) The threshold comparison is made against :attr:`alliances <interregnum.district.restriction.Attribute.ALLIANCE_TOTAL_VOTES>`, not parties: some parties change their names depending on the province, but they concur as an alliance on the regional level. If an alliance is excluded, all parties in that alliance will be excluded.

4) The threshold defines a candidate transformation:

    1) Candidates from the 3 provinces are gathered. In the root node, a party identified by (:attr:`~interregnum.district.contenders.Contender.name`, :attr:`~interregnum.district.contenders.Contender.alliance`) inside a province is now identified by (:attr:`~interregnum.district.contenders.Contender.name`, :attr:`~interregnum.district.contenders.Contender.alliance`, :attr:`~interregnum.district.contenders.Contender.district`).
    2) Candidates from that list are compared against the threshold.
    3) Because the threshold is computed for each province, candidates need to recover their original identifiers, so they are transformed by :attr:`id <interregnum.district.contenders.GroupBy.ID>` and once again, they are identified by (:attr:`~interregnum.district.contenders.Contender.name`, :attr:`~interregnum.district.contenders.Contender.alliance`).


Spain - Extremadura (regional election)
=======================================

In Extremadura, the same threshold than :ref:`tut_andalucia` is used (5% of valid votes). However, parties that reach the 5% of all the valid votes in the region are allowed to contend to the apportionments.

.. code-block:: yaml
    :linenos:
    :emphasize-lines: 2,7,8

    name: Asamblea de Extremadura - 2011
    key: comunidad
    type: group
    method: highest_averages
    method_params:
        divisor_f: dhondt
    exclude: valid_votes < 5%
    include: "comunidad.alliance_valid_votes >= 5% => id"
    divisions:
    - name: Badajoz
      seats: 36
    - name: Cáceres
      seats: 29


Spain - Islas Canarias (regional election)
==========================================

In Islas Canarias (before 2019), any party must reach 30% of the valid votes in the district, but that threshold is ignored:

- if a party is the most voted at least one of the islands,
- or if a party reaches the 6% of valid votes in the whole archipelago

.. code-block:: yaml
    :linenos:
    :emphasize-lines: 2,7,8

    name: Parlamento de Canarias 2011
    key: archipielago
    type: group
    method: highest_averages
    method_params:
        divisor_f: dhondt
    exclude: valid_votes < 30%
    include: any{rank <= 1 | archipielago.alliance_valid_votes >= 6% => id}
    divisions:
    - name: El Hierro
      seats: 3
    - name: Gran Canaria
      seats: 15
    - name: Fuerteventura
      seats: 7
    - name: Lanzarote
      seats: 8
    - name: La Gomera
      seats: 4
    - name: Tenerife
      seats: 15
    - name: La Palma
      seats: 8


In line 7, the exclusion restriction is implemented.

In line 8, the operator ``any{}`` indicates that a party which comply to any of the rules will be added to the list (the inclusion list in this case)

- ``rank <= 1``: any party whose vote rank is #1 in a district
- ``archipielago.alliance_valid_votes >= 6% => id``: any party whose alliance has at least 6% of the archipelago valid votes
