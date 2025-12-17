.. SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
..
.. SPDX-License-Identifier: LGPL-3.0-or-later

Tutorial 7: Introduction to compensatory systems
************************************************

In this tutorial we will learn how to define compensatory systems, used to level seats according to a second criterion.

.. _tut-7-scottish-parliament:

Scotland - Scottish Parliament (Highlands and Islands)
======================================================

A voter must cast two ballots:

- First vote: an individual candidate will be chosen for a one-seat constituency, like in :ref:`tut_uk_general_election_const`, winners will be elected by :func:`first-past-the-post <interregnum.methods.WinnerTakesAllAllocator>`.
- Second vote: in order to improve the proportionality at a party level, a second part vote is performed for a region, comprised by several constituencies. The seats will be allocated using the :class:`highest averages <interregnum.methods.singlevote.HighestAveragesAllocator>` method with :func:`d'Hondt divisors <interregnum.divisors.dhondt_divisor>`, resuming the already allocate seats.

We will use only the *Highlands and Islands* region: 8 constituencies and 7 additional members.

1) Define the constituencies (first vote). Independent candidates can only win 1 seat.

    .. code-block:: yaml
        :linenos:
        :emphasize-lines: 3,19

        name: Scottish Parliament - 2011
        type: group
        method: first_past_the_post
        divisions:

        - name: Highlands and Islands
          type: group
          divisions:
          - name: mp_highlands_islands
              type: group
              divisions:
              - name: Argyll & Bute
                candidates:
                - {alliance: SNP, name: Michael William Russell, votes: 13390}
                - {alliance: Conservative, name: Jamie McGrigor, votes: 4847}
                - {alliance: Labour, name: Mick Rice, votes: 4041}
                - {alliance: Liberal Democrat, name: Alison Hay, votes: 3220}
                # independent
                - {max_seats: 1, name: George Doyle, votes: 542}
                - {alliance: Liberal Party (The), name: George Alexander White, votes: 436}
              - name: Caithness, Sutherland & Ross
              - name: Inverness & Nairn
              - name: Moray
              - name: Na h-Eileanan an Iar
              - name: Orkney Islands
              - name: Shetland Islands
              - name: Skye, Lochaber & Badenoch

2) Add a compensatory district for the *Highlands and Islands* region:

    .. code-block:: yaml
        :linenos:
        :emphasize-lines: 11,12,17,18

        name: Scottish Parliament - 2011
        type: group
        method: first_past_the_post
        divisions:

        - name: Highlands and Islands
          type: group
          divisions:
          # regional additional member district
          - name: am_highlands_islands
            type: compensatory
            mode: additional_member
            seats: 7
            method: highest_averages
            method_params:
              divisor_f: dhondt
            first_vote: "alliance[mp_highlands_islands:-1]"
            skip_initial_seats: yes
            candidates:
            - {name: SNP, votes: 85082}
            - {name: Labour, votes: 25884}
            - {name: Conservative, votes: 20843}
            - {name: Liberal Democrat, votes: 21729}
            - {name: Green, votes: 9076}
            - {name: Scottish Christian Party, votes: 3541}
            - {name: UK Independence Party, votes: 3372}
            - {name: All Scotland Pensioners Party, votes: 2770}
            - {name: Ban Bankers Bonuses, votes: 1764}
            - {name: Liberal Party (The), votes: 1696}
            - {name: Socialist Labour Party, votes: 1406}
            - {name: British National Party, votes: 1134}
            - {name: Scottish Socialist Party, votes: 509}
            - {name: Solidarity, votes: 204}
          # one-seat constituencies
          - name: mp_highlands_islands
            type: group
            divisions:
            - name: Argyll & Bute
            - name: Caithness, Sutherland & Ross
            - name: Inverness & Nairn
            - name: Moray
            - name: Na h-Eileanan an Iar
            - name: Orkney Islands
            - name: Shetland Islands
            - name: Skye, Lochaber & Badenoch


   The :class:`addtional_member <interregnum.methods.compensatory.AdditionalMemberAdapter>` adapter will resume a previous allocation using a different method. Setting :attr:`~interregnum.district.node.NodeContext.skip_initial_seats` to `true`, only the new allocated seats will be included in the node result.

   The first vote is taken from leaf nodes from ``mp_highlands_islands``, and transformed to taken the alliance as identifier.

New Zealand - General Elections
===============================

The system is really similar to the Scotland's one, but there are some differences:

- There is only one compensatory district for all the country.
- The compensatory district will not resume the previous allocation. A big number of seats are assigned so that the disproportionality will be absorbed. The seats won by constituencies will be subtracted from the result.
- For a party to participate in the compensatory allocation, it must reach a 5% of the formal votes. That won't apply to parties that won at least 1 constituency.

.. code-block:: yaml
    :linenos:
    :emphasize-lines: 7,8,13-16

    name: New Zealand General Elections - 2014
    method: first_past_the_post
    type: group
    divisions:
    # mixed member district
    - name: compensatory district
      type: compensatory
      mode: mixed member
      method: highest_averages
      method_params:
        divisor_f: sainte_lague
      seats: 120
      exclude: votes < 5%
      include: electorate vote.alliance_seats >= 1 => alliance
      first_vote: alliance[electorate vote:-1]
      skip_initial_seats: yes
      candidates:
      ...
    # constituencies
    - name: electorate vote
      type: group
      aggregate: true
      divisions:
      ...


The :class:`mixed_member <interregnum.methods.compensatory.MixedMemberAdapter>` adapter allocates again using the second vote, and it subtract the seats won by the first allocation.

----

Well... as you can see, this is escalating. Take some rest and bring a fresh change of clothes, because we are travelling to Northern Europe, home to complex compensatory systems. Things could happen...