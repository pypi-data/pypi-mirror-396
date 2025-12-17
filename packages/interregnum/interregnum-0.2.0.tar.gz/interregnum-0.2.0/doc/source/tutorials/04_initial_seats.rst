.. SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
..
.. SPDX-License-Identifier: LGPL-3.0-or-later

Tutorial 5: Initial seats
*************************

In this tutorial we will learn how to specify :class:`initial seats <interregnum.district.counting.InitialSeatsSource>` a candidate can receive before the allocation starts.

United States - Congressional Apportionment
===========================================

435 seats will be distributed among the 50 states according to the census. Each state gains 1 initial seat, and the remaining seats will be allocated using the :func:`Huntington-Hill method <interregnum.interregnum.divisors.huntington_hill_divisor>`.

.. code-block:: yaml
    :linenos:
    :emphasize-lines: 7,8

    name: United States Congressional Apportionment 2000
    method: highest_averages
    method_params:
        divisor_f: huntington_hill
    # 435 - 50
    seats: 385
    initial_seats: 1
    resume_allocation: true
    candidates:
    - name: Alabama
      votes: 4461130
    - name: Alaska
      votes: 628933
    - name: Arizona
      votes: 5140683
    ...
    - name: West Virginia
      votes: 1813077
    - name: Wisconsin
      votes: 5371210
    - name: Wyoming
      votes: 495304

In lines 7 and 8 we specifiy that each candidate will start with 1 seat (:attr:`~interregnum.district.node.NodeContext.initial_seats`), and that the allocation process will take into account the seats already allocated to candidates (:attr:`~interregnum.district.node.NodeContext.resume_allocation`). Since this is the default, the previous schema is equivalent to:

.. code-block:: yaml
    :linenos:
    :emphasize-lines: 7

    name: United States Congressional Apportionment 2000
    method: highest_averages
    method_params:
        divisor_f: huntington_hill
    # 435 - 50
    seats: 385
    initial_seats: 1
    candidates:
    - name: Alabama
      votes: 4461130
    - name: Alaska
      votes: 628933
    - name: Arizona
      votes: 5140683
    ...
    - name: West Virginia
      votes: 1813077
    - name: Wisconsin
      votes: 5371210
    - name: Wyoming
      votes: 495304


.. _tut_spain_parliament_district_app:

Spain - National Parliament - Districts apportionment
=====================================================

350 seats will be distributed among the 50 provinces and the 2 autonomous cities according to the census. Each autonomous city will receive 1 final seat. Each province will receive 2 initial seats, and the remaining seats will be allocated using the :class:`largest remainder method <interregnum.methods.LargestRemainderAllocator>` with a :func:`Hare quota <interregnum.quotas.hare_quota>` ignoring the already allocated seats, allocating again from scratch.

1) First, create the schema for the autonomous cities:

    .. code-block:: yaml
        :linenos:
        :emphasize-lines: 4-11

        name: Circunscripciones Congreso de los Diputados - 2015
        type: group
        divisions:
        - name: Ciudades autónomas
          method: noop
          initial_seats: 1
          candidates:
          - name: Ceuta
            votes: 84963
          - name: Melilla
            votes: 84509

   The :class:`noop <interregnum.methods.NoopAllocator>` method does not allocate any new seat, just returns its input with any initial seats assigned to candidates.

   If a different number of seats were assigned to each city, the property :attr:`~interregnum.district.contenders.Contender.min_seats`:

    .. code-block:: yaml
        :linenos:
        :emphasize-lines: 6,7,11,14

        name: Circunscripciones Congreso de los Diputados - 2015
        type: group
        divisions:
        - name: Ciudades autónomas
          method: noop
          # default value
          initial_seats: min_seats
          candidates:
          - name: Ceuta
            votes: 84963
            min_seats: 2
          - name: Melilla
            votes: 84509
            min_seats: 1

2) Then, add the schema for provinces:

    .. code-block:: yaml
        :linenos:
        :emphasize-lines: 14-31

        name: Circunscripciones Congreso de los Diputados - 2015
        type: group
        divisions:

        - name: Ciudades autónomas
          method: noop
          initial_seats: 1
          candidates:
          - name: Ceuta
            votes: 84963
          - name: Melilla
            votes: 84509

        - name: Provincias
          # 348 - 2*50
          seats: 248
          method: largest_remainder
          method_params:
            quota_f: hare
          initial_seats: 2
          resume_allocation: no
          candidates:
          - name: Alicante/Alacant
            votes: 1868438
          - name: Almería
            votes: 701688
          ...
          - name: Valladolid
            votes: 529157
          - name: Zaragoza
            votes: 960111

   Each province will get 2 free seats:

    .. code-block:: yaml
        :linenos:
        :emphasize-lines: 7

        - name: Provincias
          # 348 - 2*50
          seats: 248
          method: largest_remainder
          method_params:
            quota_f: hare
          initial_seats: 2
          resume_allocation: no


   The remaining seats will allocated by Hare, ignoring the initial free seats (:attr:`~interregnum.district.node.NodeContext.resume_allocation` is set to ``false``):

   .. code-block:: yaml
        :linenos:
        :emphasize-lines: 3-6,8

        - name: Provincias
          # 348 - 2*50
          seats: 248
          method: largest_remainder
          method_params:
            quota_f: hare
          initial_seats: 2
          resume_allocation: no
