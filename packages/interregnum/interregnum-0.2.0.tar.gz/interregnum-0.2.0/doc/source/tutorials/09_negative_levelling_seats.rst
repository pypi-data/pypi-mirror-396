.. SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
..
.. SPDX-License-Identifier: LGPL-3.0-or-later

Tutorial 9: Subtractive compensatory system
*******************************************

In this tutorial we will learn how to compute and re-apportion negative adjustment seats to compensate overhang seats.


Germany 2025 - Bundestag
========================

Mmmhh, err... yeah... Germany... this is gonna be hard...

Each *Land* is divided into one-seats constituencies where a candidate is elected using the *first vote*. A candidate can be allied to a party or can be independent.

.. code-block:: yaml
    :linenos:
    :emphasize-lines: 3, 13-14, 18

    - name: Länder
      type: group
      method: first_past_the_post
      meta:
        notes: |
            Wahlkreise.
            First vote: mandates for state districts.
      divisions:

      - name: Schleswig-Holstein
        type: group
        # we will need this later
        aggregate: yes
        groupby: id
        divisions:
        - name: Flensburg – Schleswig
          # constituencies are tagged for future references
          groups: [mandates]
        ...
      ...

In a similar way to :ref:`tut-7-scottish-parliament`, each Land has a second vote where only parties can be chosen. But instead of adjusting seats at the Land level, seats will be compensated once for all Germany (known as *Oberverteilung*, upper distribution).

.. code-block:: yaml
    :linenos:
    :emphasize-lines: 3

    - name: Zweistimme
      type: group
      method: noop
      meta:
        notes: |
            second votes: party lists for each state
      divisions:
      - name: Landesliste - Schleswig-Holstein
      - name: Landesliste - Hamburg
      - name: Landesliste - Niedersachsen
      - name: Landesliste - Bremen
      - name: Landesliste - Nordrhein-Westfalen
      - name: Landesliste - Hessen
      - name: Landesliste - Rheinland-Pfalz
      - name: Landesliste - Baden-Württemberg
      - name: Landesliste - Bayern
      - name: Landesliste - Saarland
      - name: Landesliste - Berlin
      - name: Landesliste - Brandenburg
      - name: Landesliste - Mecklenburg-Vorpommern
      - name: Landesliste - Sachsen
      - name: Landesliste - Sachsen-Anhalt
      - name: Landesliste - Thüringen


630 seats will be allocated in the upper distribution among the parties with at least 5% of votes, or parties with at least 3 constituencies or parties from minority groups.

Seats won by first vote by parties or independent candidates that can't participate in the upper distribution will be subtracted from the initial 630 seats.

This is the definitive allocation, so if a party won more seats than the upper distribution says it should have, the seats surplus will be subtracted later.

.. code-block:: yaml
    :linenos:
    :emphasize-lines: 5,7,9,11,13,15

    - name: Oberverteilung
      type: compensatory
      mode: mixed_member
      seats: 630
      exclude: votes < 5%
      # 3 constituencies or minority groups are allowed
      include: "any{ #mandates.alliance_quorum >= 3 => alliance | #mandates.alliance_group = minority => alliance }"
      # mandates from first vote will be compensated
      first_vote: "alliance[#mandates]"
      # the adjustment process will use the aggregated second vote
      candidates: alliance[Zweistimme]
      # seats from non-participant candidates will be subtracted
      subtract_excluded_candidates: yes
      # return both the levelling seats and the mandates
      skip_initial_seats: no
      meta:
        notes: |
            Federal party seats allocation using second vote.


Once the definitive seats have been allocated to parties, it's time to give it back to *Länder* and constituencies. This process is known as *Unterverteilung* (sub-distribution).

.. code-block:: yaml
    :linenos:
    :emphasize-lines: 4,6,8,10

    - name: Unterverteilung
      type: reapportionment
      strategy: candidate
      adjustment: Oberverteilung
      # the score comes from unaggregated second vote
      candidates: Zweistimme:-1
      # the party vote will be injected to Länder
      first_vote: Zweistimme:-1
      # change the names from second vote districts to first vote districts
      map_districts:
        Landesliste - Schleswig-Holstein: Schleswig-Holstein
        Landesliste - Hamburg: Hamburg
        Landesliste - Niedersachsen: Niedersachsen
        Landesliste - Bremen: Bremen
        Landesliste - Nordrhein-Westfalen: Nordrhein-Westfalen
        Landesliste - Hessen: Hessen
        Landesliste - Rheinland-Pfalz: Rheinland-Pfalz
        Landesliste - Baden-Württemberg: Baden-Württemberg
        Landesliste - Bayern: Bayern
        Landesliste - Saarland: Saarland
        Landesliste - Berlin: Berlin
        Landesliste - Brandenburg: Brandenburg
        Landesliste - Mecklenburg-Vorpommern: Mecklenburg-Vorpommern
        Landesliste - Sachsen: Sachsen
        Landesliste - Sachsen-Anhalt: Sachsen-Anhalt
        Landesliste - Thüringen: Thüringen
      meta:
        notes: |
            State seats allocation for each party.


The attribute :attr:`~interregnum.district.Node.map_districts` allows to rename districts in the result.


Once the seats have been distributed to each Land, the levelling seats are subtracted from mandates.

.. code-block:: yaml
    :linenos:
    :emphasize-lines: 4,6,8,10,12,14,16

    - name: levelling seats
      type: compensatory
      # produce negative seats for overhang seats
      mode: subtract_overhang_seats
      # reuse what we have
      method: noop
      # noop needs initial seats from first vote
      propagate_initial_seats: yes
      # mandates
      first_vote: Länder:1
      # sub-distribution
      candidates: Unterverteilung
      # we take seats from the Unterverteilung result
      initial_seats: from_results
      # return new seats only
      skip_initial_seats: yes
      meta:
        notes: |
            Allocate levelling seats (subtract mandates from Unterverteilung)


Overhang seats will be subtracted from the mandates.

.. code-block:: yaml
    :linenos:
    :emphasize-lines: 3-4,6,8-9,13,15,17,18,20,22

    - name: negative levelling seats
      # we take parties with negative seats (overhang seats)
      exclude: levelling seats.seats >= 0
      include: levelling seats.seats < 0
      # we are just filtering out
      method: noop
      # we use the levelling seats
      candidates: levelling seats
      initial_seats: from_results

    - name: mandates surplus
      type: reapportionment
      method: limited_voting
      strategy: candidate
      relative: votes
      # only parties that are losing mandates
      exclude: "#mandates.seats < 1"
      adjustment: negative levelling seats
      # the score
      candidates: "#mandates"
      # the destination
      first_vote: "#mandates"


Now, the final schema:

.. code-block:: yaml
    :linenos:
    :emphasize-lines: 3,5,8,28,52,71,101,121,131

    name: Bundestag 2025
    type: group
    method: iterative_divisor
    method_params:
        signpost_f: sainte_lague
    divisions:

    - name: Länder
      type: group
      method: first_past_the_post
      meta:
        notes: |
            Wahlkreise.
            First vote: mandates for state districts.
      divisions:
      - name: Schleswig-Holstein
        type: group
        # we will need this later
        aggregate: yes
        groupby: id
        divisions:
        - name: Flensburg – Schleswig
          # constituencies are tagged for future references
          groups: [mandates]
        ...
      ...

    - name: Zweistimme
      type: group
      method: noop
      meta:
        notes: |
            second votes: party lists for each state
      divisions:
      - name: Landesliste - Schleswig-Holstein
      - name: Landesliste - Hamburg
      - name: Landesliste - Niedersachsen
      - name: Landesliste - Bremen
      - name: Landesliste - Nordrhein-Westfalen
      - name: Landesliste - Hessen
      - name: Landesliste - Rheinland-Pfalz
      - name: Landesliste - Baden-Württemberg
      - name: Landesliste - Bayern
      - name: Landesliste - Saarland
      - name: Landesliste - Berlin
      - name: Landesliste - Brandenburg
      - name: Landesliste - Mecklenburg-Vorpommern
      - name: Landesliste - Sachsen
      - name: Landesliste - Sachsen-Anhalt
      - name: Landesliste - Thüringen

    - name: Oberverteilung
      type: compensatory
      mode: mixed_member
      seats: 630
      exclude: votes < 5%
      # 3 constituencies or minority groups are allowed
      include: "any{ #mandates.alliance_quorum >= 3 => alliance | #mandates.alliance_group = minority => alliance }"
      # mandates from first vote will be compensated
      first_vote: "alliance[#mandates]"
      # the adjustment process will use the aggregated second vote
      candidates: alliance[Zweistimme]
      # seats from non-participant candidates will be subtracted
      subtract_excluded_candidates: yes
      # return both the levelling seats and the mandates
      skip_initial_seats: no
      meta:
        notes: |
            Federal party seats allocation using second vote.

    - name: Unterverteilung
      type: reapportionment
      strategy: candidate
      adjustment: Oberverteilung
      # the score comes from unaggregated second vote
      candidates: Zweistimme:-1
      # the party vote will be injected to Länder
      first_vote: Zweistimme:-1
      # change the names from second vote districts to first vote districts
      map_districts:
        Landesliste - Schleswig-Holstein: Schleswig-Holstein
        Landesliste - Hamburg: Hamburg
        Landesliste - Niedersachsen: Niedersachsen
        Landesliste - Bremen: Bremen
        Landesliste - Nordrhein-Westfalen: Nordrhein-Westfalen
        Landesliste - Hessen: Hessen
        Landesliste - Rheinland-Pfalz: Rheinland-Pfalz
        Landesliste - Baden-Württemberg: Baden-Württemberg
        Landesliste - Bayern: Bayern
        Landesliste - Saarland: Saarland
        Landesliste - Berlin: Berlin
        Landesliste - Brandenburg: Brandenburg
        Landesliste - Mecklenburg-Vorpommern: Mecklenburg-Vorpommern
        Landesliste - Sachsen: Sachsen
        Landesliste - Sachsen-Anhalt: Sachsen-Anhalt
        Landesliste - Thüringen: Thüringen
      meta:
        notes: |
            State seats allocation for each party.

    - name: levelling seats
      type: compensatory
      # produce negative seats for overhang seats
      mode: subtract_overhang_seats
      # reuse what we have
      method: noop
      # noop needs initial seats from first vote
      propagate_initial_seats: yes
      # mandates
      first_vote: Länder:1
      # sub-distribution
      candidates: Unterverteilung
      # we take seats from the Unterverteilung result
      initial_seats: from_results
      # return new seats only
      skip_initial_seats: yes
      meta:
        notes: |
            Allocate levelling seats (subtract mandates from Unterverteilung)

    - name: negative levelling seats
      # we take parties with negative seats (overhang seats)
      exclude: levelling seats.seats >= 0
      include: levelling seats.seats < 0
      # we are just filtering out
      method: noop
      # we use the levelling seats
      candidates: levelling seats
      initial_seats: from_results

    - name: mandates surplus
      type: reapportionment
      method: limited_voting
      strategy: candidate
      relative: votes
      # only parties that are losing mandates
      exclude: "#mandates.seats < 1"
      adjustment: negative levelling seats
      # the score
      candidates: "#mandates"
      # the destination
      first_vote: "#mandates"