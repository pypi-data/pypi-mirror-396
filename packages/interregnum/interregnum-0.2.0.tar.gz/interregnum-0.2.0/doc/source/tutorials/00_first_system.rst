.. SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
..
.. SPDX-License-Identifier: LGPL-3.0-or-later

Tutorial 1: Our first electoral system
**************************************

Let's start defining real elections that are plain and simple.

.. _tut_uk_general_election_const:

UK - General election (Caerfyrddin)
====================================

In the UK General election, a Parliament member is elected from each constituency using the :class:`first-past-the-post <interregnum.methods.singlevote.WinnerTakesAllAllocator>` system.

For out example, we will define the Caerfyrddin constituency (2014 General election).

We will use the YAML format for electoral systems definitions:

1. Create a :class:`district <interregnum.district.District>` and set an identifier:

    .. code-block:: yaml
        :linenos:
        :emphasize-lines: 1

        name: Caerfyrddin constituency (2014 UK General election)


2. Add the election method (:class:`first-past-the-post <interregnum.methods.singlevote.WinnerTakesAllAllocator>`). This method can be accessed by two keys: `first_past_the_post` and `winner_takes_all`.

    .. code-block:: yaml
        :linenos:
        :emphasize-lines: 2

        name: Caerfyrddin constituency (2014 UK General election)
        method: first_past_the_post

3. Add votes for candidates:

    .. code-block:: yaml
        :linenos:
        :emphasize-lines: 3-27

        name: Caerfyrddin constituency (2014 UK General election)
        method: first_past_the_post
        candidates:
        - name: DAVIES, Ann
          alliance: PC
          votes: 15520
        - name: O'NEIL, Martha
          alliance: Lab
          votes: 10985
        - name: HART, Simon
          alliance: Con
          votes: 8825
        - name: HOLTON, Bernard
          alliance: RUK
          votes: 6944
        - name: BECKETT, Nick
          alliance: LD
          votes: 1461
        - name: BEASLEY, Will
          alliance: Green
          votes: 1371
        - name: COLE, Nancy
          alliance: WEP
          votes: 282
        - name: EVANS, David
          alliance: WPB
          votes: 216

4. We can add invalid votes inserting a special candidate whose name starts with ``!``:

    .. code-block:: yaml
        :linenos:
        :emphasize-lines: 4-5

        name: Caerfyrddin constituency (2014 UK General election)
        method: first_past_the_post
        candidates:
        - name: "! invalid vote"
          votes: 187
        - name: DAVIES, Ann
          alliance: PC
          votes: 15520
        - name: O'NEIL, Martha
          alliance: Lab
          votes: 10985
        - name: HART, Simon
          alliance: Con
          votes: 8825
        - name: HOLTON, Bernard
          alliance: RUK
          votes: 6944
        - name: BECKETT, Nick
          alliance: LD
          votes: 1461
        - name: BEASLEY, Will
          alliance: Green
          votes: 1371
        - name: COLE, Nancy
          alliance: WEP
          votes: 282
        - name: EVANS, David
          alliance: WPB
          votes: 216

    There are two special candidates recognised by a name prefix:

    - Invalid votes, with prefix ``!``.
    - Blank votes (valid empty votes), with prefix ``?``.

    Candidates can be provided directly from file. That will be covered soon.

5. Save the file as ``Caerfyrddin_2014.yaml``.

Now, this system can be computed using the command :doc:`interregnum-cli <../cli>`:

.. code-block:: console

    interregnum-cli calc Caerfyrddin_2014.yaml results.yaml


.. _tut_spain_eu_parliament:

Spain - European Parliament
===========================

No regional districts are considered for the Spanish EU Parliament elections:

- Seats are apportioned using the :class:`highest averages <interregnum.methods.singlevote.HighestAveragesAllocator>` method with :func:`d'Hondt divisors <interregnum.divisors.dhondt_divisor>`.
- In addition to invalid votes, blank votes (valid votes to no candidate) are also considered.
- In the year 2024 61 members of the European Parliament were allocated to Spain.

We can reuse the schema for the UK General election, but with some additions:

    .. code-block:: yaml
        :linenos:
        :emphasize-lines: 3-5,9-10

        name: Spain 2024 - European Parliament
        method: highest_averages
        method_params:
            divisor_f: dhondt
        seats: 61
        candidates:
        - name: "! invalid vote"
          votes: 124569
        - name: "? blank vote"
          votes: 124655
        ...

1. The :class:`~interregnum.methods.singlevote.HighestAveragesAllocator` requires a parameter ``divisor_f`` with the name of the divisor function:


    .. code-block:: yaml
        :linenos:
        :lineno-start: 2
        :emphasize-lines: 2-3

        method: highest_averages
        method_params:
            divisor_f: dhondt
        seats: 61

2. Since there is a multi-seat allocation, seats need to be provided:


    .. code-block:: yaml
        :linenos:
        :lineno-start: 3
        :emphasize-lines: 3

        method_params:
            divisor_f: dhondt
        seats: 61
        candidates:

3. Blank vote is added as a special candidate whose name has a prefix ``?``:

    .. code-block:: yaml
        :linenos:
        :lineno-start: 6
        :emphasize-lines: 4-5

        candidates:
        - name: "! invalid vote"
          votes: 124569
        - name: "? blank vote"
          votes: 124655
        ...

Now, all candidates should be included to the schema, but we will omit it for the sake of brevity.


Belgium (2012) - Local elections
================================

Let's do one more...

In Belgium, the local elections used the same system than the Spain EU Parliament elections, but the :func:`Imperiali divisor <interregnum.divisors.imperiali_divisor>` is used instead.

In 2012 47 seats were allocated to Anderlecht:

.. code-block:: yaml
    :linenos:
    :emphasize-lines: 4,5

    name: Commune d'Anderlecht - 2012
    method: highest_averages
    method_params:
        divisor_f: imperiali
    seats: 47
    candidates:
    - name: "N-VA"
      votes: 2258
    - name: "LB"
      votes: 11648
    - name: "FDF"
      votes: 3499
    - name: "ECOLO-GROEN"
      votes: 5057
    - name: "VLAAMS BELANG"
      votes: 1630
    - name: "PS-SP.A-CDH"
      votes: 16383
    - name: "PTB*PVDA+"
      votes: 755
    - name: "GAUCHES COMMUNES"
      votes: 278
    - name: "ISLAM"
      votes: 1839
    - name: "EGALITE"
      votes: 829
    - name: "BELG-UNIE"
      votes: 385
