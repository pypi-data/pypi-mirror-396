.. SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
..
.. SPDX-License-Identifier: LGPL-3.0-or-later

Tutorial 6: Preferences and external data files
***********************************************

Before we fight the final bosses, the compensatory systems, let's practice two other concepts:

- Preferential vote method
- Retrieving data from external files


Wikipedia - Condorcet method example
====================================

We will define an schema for the example in the en.Wikipedia page `Condorcet method <https://en.wikipedia.org/w/index.php?title=Condorcet_method&oldid=1320007514>`_:

Voters from Tennessee should order 4 possible candidates in the order they prefer to be their new capital city:

- 42% of voters prefers Memphis, then Nashville, then Chattanooga, then Knoxville
- 26% of voters prefers Nashville, then Chattanooga, then Knoxville, then Memphis
- 15% of voters prefers Chattanooga, then Knoxville, then Nashville, then Memphis
- 17% of voters prefers Knoxville, then Chattanooga, then Nashville, then Memphis

This data can't be provided using the :class:`~interregnum.district.contenders.Contender`. We need to use :class:`~interregnum.methods.preferential.Preference` instead.


.. code-block:: yaml
    :linenos:
    :emphasize-lines: 2, 4-11

    name: Tennessee - Capital city
    method: copeland
    preferences:
    - votes: 42
      preference: ["Memphis", "Nashville", "Chattanooga", "Knoxville"]
    - votes: 26
      preference: ["Nashville", "Chattanooga", "Knoxville", "Memphis"]
    - votes: 15
      preference: ["Chattanooga", "Knoxville", "Nashville", "Memphis"]
    - votes: 17
      preference: ["Knoxville", "Chattanooga", "Nashville", "Memphis"]


We have used the :class:`Copeland's method <interregnum.methods.CondorcetCopelandAllocator>`, but it could be replaced by any method in :mod:`interregnum.methods.preferential`.


Australia - Senate 2002 - Northern Territory
============================================

Each district is a multi-seat constituency where the contenders are candidates that can be allied to parties. Winners are elected using the :class:`Single Transferable Vote <interregnum.methods.SingleTransferableVoteAllocator>` method with a :func:`Droop quota <interregnum.quotas.droop_quota>`. Votes are transferred by the :func:`Weighted Inclusive Gregory's transfer method <interregnum.methods.preferential.transferable_vote.transfer_functions.inclusive_gregory_transfer>`.

The Northern Territory will be represented by 2 senators.


.. code-block:: yaml
    :linenos:
    :emphasize-lines: 4-7,12,53-56

    name: Australia - Senate 2002
    type: group
    method: single_transferable_vote
    method_params:
        quota_f: droop
        transfer_f: weighted_inclusive_gregory
        round_f: int
    divisions:

    - name: Northern Territory
      seats: 2
      candidates:
      - name: PRICE Jacinta Nampijinpa [PJN]
        alliance: NT CLP
      - name: CIVITARESE Kris [CK]
        alliance: NT CLP

      - name: McMAHON Sam [MS]
        alliance: Liberal Democrats

      - name: McCARTHY Malarndirri [MM]
        alliance: A.L.P.
      - name: GANLEY Kate [GK]
        alliance: A.L.P.

      - name: LAWRENCE Lance [LL]
        alliance: Legalise Cannabis Australia
      - name: HIBBERT Kelly-Anne [HKA]
        alliance: Legalise Cannabis Australia

      - name: WHYTE Lamaan [WL]
        alliance: Sustainable Australia Party - Stop Overdevelopment / Corruption
      - name: BELCHER Richard [BR]
        alliance: Sustainable Australia Party - Stop Overdevelopment / Corruption

      - name: ARRIGO Steve [AS]
        alliance: The Great Australian Party
      - name: MARCUS Angela [MA]
        alliance: The Great Australian Party

      - name: CAMPBELL Trudy [CT]
        alliance: Citizens Party
      - name: FLYNN Peter [FP]
        alliance: Citizens Party

      - name: ANLEZARK Jane [AJ]
        alliance: The Greens
      - name: STOKES Dianne [SD]
        alliance: The Greens

      - name: RAJWIN Raj [RR]

      preferences:
          type: preferences-file
          format: pref
          path: au_senate_northern_territory_2002.pref



Registered candidates are provided for two reasons:

- This allows to specify alliances,
- Some methods require the full list of candidates, even if nobody voted for them.

Since the list of preferences is large, it will be tedious to add it to the schema. We will declare the use of an :class:`external file <interregnum.district.io.PreferencesFile>` instead:

.. code-block:: yaml
    :linenos:
    :lineno-start: 53

    preferences:
        type: preferences-file
        format: pref
        path: au_senate_northern_territory_2002.pref


The format ``pref`` allows to write files in a more compact way:

.. code-block:: text

    !!preference >
    !!equal =
    !!score :
    !a=PRICE Jacinta Nampijinpa [PJN]
    !b=McCARTHY Malarndirri [MM]
    !c=HIBBERT Kelly-Anne [HKA]
    !d=CIVITARESE Kris [CK]
    !e=BELCHER Richard [BR]
    !f=LAWRENCE Lance [LL]
    !g=CAMPBELL Trudy [CT]
    !h=STOKES Dianne [SD]
    !i=MARCUS Angela [MA]
    !j=ANLEZARK Jane [AJ]
    !k=WHYTE Lamaan [WL]
    !l=ARRIGO Steve [AS]
    !m=McMAHON Sam [MS]
    !n=GANLEY Kate [GK]
    !o=FLYNN Peter [FP]
    !p=RAJWIN Raj [RR]
    !q=HANSEN Jed [HJ]
    5206:a>d>m>q>b>n>f>c>k>e>l>i
    4272:b>n>j>h>m>q>f>c>k>e>a>d
    1787:a>d>m>q>b>n>f>c>k>e>l>i>g>o>j>h
    1385:j>h>b>n>f>c>k>e>a>d>m>q
    709:b>n
    660:b>n>l>i>m>q>f>c>k>e>a>d
    530:a>d
    ...


Spain - General elections - Parliament (revisited... again)
===========================================================

In :ref:`tut-6-spanish-general` we omitted candidates to keep the schema short. Now we will use an :class:`external file <interregnum.district.io.CandidatesFile>`


.. code-block:: yaml
    :linenos:
    :emphasize-lines: 11-13, 36-38

    name: Elecciones a Cortes Generales
    type: group
    divisions:

    - name: Distribución de escaños
      type: group
      aggregate: yes
      meta:
        notes: |
            Seats apportionment based on provintial census
      fill_candidates:
          path: censo_provincial_2015.csv
          format: csv
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
      fill_candidates:
        path: votos_generales_2015.csv
        format: csv
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


When file is provided to a node through :func:`~interregnum.district.serialize.unserialize_node`, files with candidates data will be injected to that node or some of its children:

- If a row has a column ``node``, the value will be used to identify the node.
- Otherwise, if a row has a column ``district``, the vlaue will be used to identify the node.
- If no node could be identified, all candidates will be assigned to the root node where the file was declared.

Let's see the head of the file ``censo_provincial_2015.csv``:

.. code-block:: text

    district,name,votes
    Ciudades autónomas,Ceuta,84963
    Ciudades autónomas,Melilla,84509
    Provincias,Almería,701688
    Provincias,Cádiz,1240175
    Provincias,Córdoba,799402
    Provincias,Granada,919455
    Provincias,Huelva,519229
    Provincias,Jaén,659033
    Provincias,Málaga,1621968


And the head of ``votos_generales_2015.csv``:

.. code-block:: text

    district,name,votes
    Almería,PARTIDO POPULAR,117635
    Almería,PARTIDO SOCIALISTA OBRERO ESPAÑOL,89434
    Almería,CIUDADANOS-PARTIDO DE LA CIUDADANÍA,44494
    Almería,PODEMOS,39780
    Almería,"UNIDAD POPULAR: IZQUIERDA UNIDA, UNIDAD POPULAR EN",10828
    Almería,PARTIDO ANIMALISTA CONTRA EL MALTRATO ANIMAL,2126
    Almería,UNIÓN PROGRESO Y DEMOCRACIA,1532
    Almería,VOX,558
    Almería,FALANGE ESPAÑOLA DE LAS J.O.N.S.,343
    Almería,PARTIDO COMUNISTA DE LOS PUEBLOS DE ESPAÑA,318
    Almería,RECORTES CERO-GRUPO VERDE,297
    Almería,POR UN MUNDO MÁS JUSTO,176
    Almería,DEMOCRACIA NACIONAL,164
    Cádiz,PARTIDO SOCIALISTA OBRERO ESPAÑOL,180895
    Cádiz,PARTIDO POPULAR,179319
    Cádiz,PODEMOS,130734


External files can also be specified when using the :doc:`../cli`.