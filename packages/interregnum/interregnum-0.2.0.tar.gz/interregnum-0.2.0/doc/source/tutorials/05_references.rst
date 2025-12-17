.. SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
..
.. SPDX-License-Identifier: LGPL-3.0-or-later

Tutorial 6: References
**********************

In this tutorial we will learn how to re-use data from other nodes using :attr:`references <interregnum.district.references.Reference.parse>`.

.. _tut-6-spanish-general:

Spain - General elections - Parliament - Full process
=====================================================

The elections for the National Parliament requires two steps:

- Distribution of seats among districts (see :ref:`tut_spain_parliament_district_app`)
- Seats allocation among candidates (see :ref:`tut_andalucia`)

Now we will compose the full schema:

We now have to sets of votes:

- census aggregated by province
- election vote to party lists


1) Census aggregated by province: we just need to copy the schema from the previous tutorial (:ref:`tut_spain_parliament_district_app`) and make some adjustments:

   .. code-block:: yaml
        :linenos:
        :emphasize-lines: 7,9-10

        name: Elecciones a Cortes Generales
        type: group
        divisions:

        - name: Distribución de escaños
          type: group
          aggregate: yes
          meta:
            notes: |
                Seats apportionment based on provintial census
          divisions:
          - name: Ciudades autónomas
            method: noop
            initial_seats: 1
          - name: Provincias
            seats: 248
            method: largest_remainder
            method_params:
              quota_f: hare
            initial_seats: 2
            resume_allocation: no


   In line 7 we enable the generation of a result, so that we can have a flattened list for both autonomous cities and provinces.

   In line 8-9, a comment was added. Custom properties can be added to a district using the :attr:`~interregnum.district.Node.meta` container.

2) Election vote to party lists: a schema similar to the one we used for :ref:`tut_andalucia` will be addded, but we will use references to the seats computed by the node ``Distribución de escaños``:

   .. code-block:: yaml
        :linenos:
        :emphasize-lines: 34,35,38,40,42,44,46,48,50,52,59,61,63

        name: Elecciones a Cortes Generales
        type: group
        divisions:

        - name: Distribución de escaños
          type: group
          aggregate: yes
          meta:
            notes: |
                Seats apportionment based on provintial census
          divisions:
          - name: Ciudades autónomas
            method: noop
            initial_seats: 1
          - name: Provincias
            seats: 248
            method: largest_remainder
            method_params:
              quota_f: hare
            initial_seats: 2

        - name: Circunscripciones
          type: group
          aggregate: yes
          method: highest_averages
          method_params:
            divisor_f: dhondt
          exclude: valid_votes < 3%
          meta:
            notes: |
                Seats allocation based on votes
          divisions:
          - name: Andalucía
            type: group
            aggregate: yes
            divisions:
            - name: Almería
              seats: Distribución de escaños
            - name: Cádiz
              seats: Distribución de escaños
            - name: Córdoba
              seats: Distribución de escaños
            - name: Granada
              seats: Distribución de escaños
            - name: Huelva
              seats: Distribución de escaños
            - name: Jaén
              seats: Distribución de escaños
            - name: Málaga
              seats: Distribución de escaños
            - name: Sevilla
              seats: Distribución de escaños
          ...
          - name: País Vasco
            type: group
            aggregate: yes
            divisions:
            - name: Araba/Álava
              seats: Distribución de escaños
            - name: Bizkaia
              seats: Distribución de escaños
            - name: Gipuzkoa
              seats: Distribución de escaños


   There are two differences from the old version:

   - An intermediate group level was added in order to get results aggregated by autonomous regions.
   - The seats for provinces are no longed hard-coded. Now they are using the values computed by the node ``Distribución de escaños``. If a candidate with the same name as the district who references is found, the computed seats will be used.


Zurich - Bi-proportional system
===============================

We will use more references defining a new kind of method, the bi-proportional allocation ([Zachariasen:2006]_, [Pukelsheim:2013]_, [Oelbermann:2016]_)

In 2006, the Canton of Zürich 125 seats were allocated among 9 districts keeping two proportionalities:

- The number of seats assigned to districts is proportional.
- The number of seats assigned to parties is also proportional.
- Seats are assigned to parties in district keeping the restrictions above.

In the first step party seats and district seats are computed for the whole Canton. Then, seats are reapportioned to parties in districts in a single allocation process using the :func:`Sainte-Laguë divisor <interregnum.divisors.sainte_lague_divisor>` method.


.. code-block:: yaml
    :linenos:
    :emphasize-lines: 5, 10,11, 17,18, 31

    name: Zürich Canton Parliament 2006
    type: group
    divisions:
    - name: biproportional
      method: alternate_scaling
      method_params:
          round_f: sainte_lague
          nice_quota: yes
          sort_parties: yes
      candidates: Wahlkreise
      party_seats:
          name: party seats
          method: highest_averages
          method_params:
            divisor_f: sainte_lague
          seats: 125
          candidates: id[Wahlkreise]
      district_seats:
          method: noop
          candidates:
          - {name: "WK1+2", min_seats: 12}
          - {name: "WK3", min_seats: 16}
          - {name: "WK4+5", min_seats: 13}
          - {name: "WK6", min_seats: 10}
          - {name: "WK7+8", min_seats: 17}
          - {name: "WK9", min_seats: 16}
          - {name: "WK10", min_seats: 12}
          - {name: "WK11", min_seats: 19}
          - {name: "WK12", min_seats: 10}

    - name: Wahlkreise
      method: noop
      candidates:
      - { district: WK1+2, name: SP, votes: 28518 }
      - { district: WK1+2, name: SVP, votes: 15305 }
      - { district: WK1+2, name: FDP, votes: 21833 }
      - { district: WK1+2, name: Grüne, votes: 12401 }
      - { district: WK1+2, name: CVP, votes: 7318 }
      - { district: WK1+2, name: EVP, votes: 2829 }
      - { district: WK1+2, name: AL, votes: 2413 }
      - { district: WK1+2, name: SD, votes: 1651 }

      ...

      - { district: WK12, name: SP, votes: 13215 }
      - { district: WK12, name: SVP, votes: 10248 }
      - { district: WK12, name: FDP, votes: 3066 }
      - { district: WK12, name: Grüne, votes: 2187 }
      - { district: WK12, name: CVP, votes: 4941 }
      - { district: WK12, name: EVP, votes: 0 }
      - { district: WK12, name: AL, votes: 429 }
      - { district: WK12, name: SD, votes: 2078 }


1) Create the electoral districts:


    .. code-block:: yaml
        :linenos:
        :lineno-start: 31
        :emphasize-lines: 2

        - name: Wahlkreise
          method: noop
          candidates:
          - { district: WK1+2, name: SP, votes: 28518 }
          - { district: WK1+2, name: SVP, votes: 15305 }
          - { district: WK1+2, name: FDP, votes: 21833 }
          - { district: WK1+2, name: Grüne, votes: 12401 }
          - { district: WK1+2, name: CVP, votes: 7318 }
          - { district: WK1+2, name: EVP, votes: 2829 }
          - { district: WK1+2, name: AL, votes: 2413 }
          - { district: WK1+2, name: SD, votes: 1651 }

          ...

          - { district: WK12, name: SP, votes: 13215 }
          - { district: WK12, name: SVP, votes: 10248 }
          - { district: WK12, name: FDP, votes: 3066 }
          - { district: WK12, name: Grüne, votes: 2187 }
          - { district: WK12, name: CVP, votes: 4941 }
          - { district: WK12, name: EVP, votes: 0 }
          - { district: WK12, name: AL, votes: 429 }
          - { district: WK12, name: SD, votes: 2078 }


   This node will be a simple container, with no allocation *per se*. Note that the field ``district`` is specified explicitly for contenders. This is the equivalent of this hierarchical schema:

    .. code-block:: yaml
        :linenos:
        :lineno-start: 31
        :emphasize-lines: 2

        - name: Wahlkreise
          type: group
          method: noop
          divisions:
          - name: WK1+2
            candidates:
            - { name: SP, votes: 28518 }
            - { name: SVP, votes: 15305 }
            - { name: FDP, votes: 21833 }
            - { name: Grüne, votes: 12401 }
            - { name: CVP, votes: 7318 }
            - { name: EVP, votes: 2829 }
            - { name: AL, votes: 2413 }
            - { name: SD, votes: 1651 }

          ...

          - name: WK12
            candidates:
            - { name: SP, votes: 13215 }
            - { name: SVP, votes: 10248 }
            - { name: FDP, votes: 3066 }
            - { name: Grüne, votes: 2187 }
            - { name: CVP, votes: 4941 }
            - { name: EVP, votes: 0 }
            - { name: AL, votes: 429 }
            - { name: SD, votes: 2078 }


2) Create a node for district seats. This is not computed here:

    .. code-block:: yaml
        :linenos:
        :lineno-start: 18

        district_seats:
            method: noop
            candidates:
            - {name: "WK1+2", min_seats: 12}
            - {name: "WK3", min_seats: 16}
            - {name: "WK4+5", min_seats: 13}
            - {name: "WK6", min_seats: 10}
            - {name: "WK7+8", min_seats: 17}
            - {name: "WK9", min_seats: 16}
            - {name: "WK10", min_seats: 12}
            - {name: "WK11", min_seats: 19}
            - {name: "WK12", min_seats: 10}

  Seats are set using ``min_seats``.


3) Allocate seats to parties:

    .. code-block:: yaml
        :linenos:
        :lineno-start: 11
        :emphasize-lines: 7

        party_seats:
            name: party seats
            method: highest_averages
            method_params:
                divisor_f: sainte_lague
            seats: 125
            candidates: id[Wahlkreise]

  Note that instead of giving a list of candidates, a reference is used: ``id[Wahlkreise]``. This will get the `Wahlkreise` node's candidates and will apply a transformation by ``id`` (it will remove districts).


4) Allocate bi-proportionally:

    .. code-block:: yaml
        :linenos:
        :lineno-start: 4
        :emphasize-lines: 2,7

        - name: biproportional
          method: alternate_scaling
          method_params:
            round_f: sainte_lague
            nice_quota: yes
            sort_parties: yes
          candidates: Wahlkreise
          party_seats:
            ...
          district_seats:
            ...

   It will use the :class:`alternate scaling <interregnum.methods.interregnum.methods.BiproportionalAllocator>` method, and the candidates will be retrieved from `Wahlkreise` again, but no transformations are made (name, alliance and district is preserved).