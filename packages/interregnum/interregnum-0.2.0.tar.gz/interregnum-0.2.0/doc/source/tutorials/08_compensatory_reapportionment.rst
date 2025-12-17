.. SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
..
.. SPDX-License-Identifier: LGPL-3.0-or-later

Tutorial 8: Compensatory systems with re-apportionment
******************************************************

In this tutorial we will learn how to re-locate seats obtained in compensatory districts to the original districts.


Norway - Stortinget
===================

The country is divided among 19 multi-seat constituencies using the :class:`highest averages <interregnum.methods.singlevote.HighestAveragesAllocator>` method with :func:`modified Sainte-Laguë divisors <interregnum.divisors.sainte_lague_14_divisor>` (first divisor 1.4).

A compensatory district based on special mixed member system will allocate a maximum of 169 seats:

- Each constituency can only be adjusted by 1 extra seat.
- A party must reach a 4% of the valid vote and must be present in th 19 constituencies.
- Seats won by any excluded party will be subtracted from the levelling seats.
- If a party gains more seats than the ones indicated by the mixed member allocation (overhang seats), that party is excluded, and the extra seats will be subtracted from the levelling seats.
- The adjustment allocation will be repeated until no party is excluded.
- The adjustment will re-use the first vote aggregated by name and alliance.

Once the levelling seats have been computed, the system requires the seats to be re-apportioned to the original constituencies. The seats are reallocated using the original :class:`Sainte-Laguë <interregnum.divisors.sainte_lague_divisor>` divisor method. Instead of absolute votes, this step uses the party/district votes divided by the district quota.


1) Define the multi-seat constituencies: the property :attr:`~interregnum.district.Node.max_adjustment_seats` is set to 1 to limit the number of seats the district will be compensated with.

    .. code-block:: yaml
        :linenos:
        :emphasize-lines: 7,12

        - name: valgdistrikter
          type: group
          aggregate: true
          divisions:
          - name: : Østfold [1]
            seats: 8
            max_adjustment_seats: 1
            candidates: ...
          ...
          - name: Finnmark Finnmárku [20]
            seats: 4
            max_adjustment_seats: 1
            candidates: ...

2) Add the compensatory district:

    .. code-block:: yaml
        :linenos:
        :emphasize-lines: 3,5-6,9

        - name: compensatory
          type: compensatory
          mode: exclude_overhang_parties
          exclude: any{ valid_votes < 4% | valgdistrikter.districts < 19 => id }
          first_vote: id[valgdistrikter:-1]
          candidates: id[valgdistrikter:-1]
          seats: 169
          skip_initial_seats: yes
          subtract_excluded_candidates: yes


   The mode :attr:`~interregnum.district.compensatory.CompensatoryType.EXCLUDE_OVERHANG_PARTIES` will exclude partis with overhang seats from the compensatory allocation. This is complemented with :attr:`~interregnum.district.Compensatory.subtract_excluded_candidates`, which will subtract the seats obtained by parties excluded by restrictions.


3) Now, the seats computed in the compensatory district need to be assigned to the original constituencies. We will use a node of type :class:`reapportionment <interregnum.district.Reapportionment>`:

    .. code-block:: yaml
        :linenos:
        :emphasize-lines: 2, 7, 9, 11, 13, 15

        - name: reapportionment
          type: reapportionment
          method: highest_averages
          method_params:
            divisor_f: sainte_lague
          # the score is votes / district quota
          relative: quota
          # the quota is relative to valid vote
          total_votes: valid_votes
          # look for adjustment seats in the node `compensatory`
          adjustment: compensatory
          # look for the original candidates in `valgdistrikter`
          candidates: valgdistrikter
          # use this node to compute the score
          first_vote: valgdistrikter


4) That's it, we can compose the full schema:

    .. code-block:: yaml
        :linenos:
        :emphasize-lines: 5, 8, 18, 34

        name: Stortinget 2021
        type: group
        method: highest_averages
        method_params:
          divisor_f: sainte_lague_1.4
        divisions:

        - name: compensatory
          type: compensatory
          mode: exclude_overhang_parties
          exclude: any{ valid_votes < 4% | valgdistrikter.districts < 19 => id }
          first_vote: id[valgdistrikter:-1]
          candidates: id[valgdistrikter:-1]
          seats: 169
          skip_initial_seats: yes
          subtract_excluded_candidates: yes

        - name: reapportionment
          type: reapportionment
          method: highest_averages
          method_params:
            divisor_f: sainte_lague
          # the score is votes / district quota
          relative: quota
          # the quota is relative to valid vote
          total_votes: valid_votes
          # look for adjustment seats in the node `compensatory`
          adjustment: compensatory
          # look for the original candidates in `valgdistrikter`
          candidates: valgdistrikter
          # use this node to compute the score
          first_vote: valgdistrikter

        - name: valgdistrikter
          type: group
          aggregate: true
          divisions:
          - name: : Østfold [1]
            seats: 8
            max_adjustment_seats: 1
            candidates: ...
          ...
          - name: Finnmark Finnmárku [20]
            seats: 4
            max_adjustment_seats: 1
            candidates: ...


Iceland - Alþingi
=================

The Icelandic system is similar to the one used in Norway, with some differences:

- There are 6 multi-seat constituencies, allocated by d'Hondt divisors method.
- There are 9 levelling seats that are allocated resuming the previous allocation.
- Any party that reaches the 5% of total vote can partipate in the adjustment process.
- The re-apportionment of a seats occurs just after a new levelling seat is allocated.
- The re-apportionment score is relative to the district vote.


1) Define the multi-seat constituencies: the property :attr:`~interregnum.district.Node.max_adjustment_seats` is set to 1 to limit the number of seats the district will be compensated with.

    .. code-block:: yaml
        :linenos:

        - name: kjördæmi
          type: group
          aggregate: yes
          divisions:

          - name: Norðvesturkjördæmi [Northwest]
            seats: 7
            max_adjustment_seats: 1
            candidates: ...
          ...
          - name: Reykjavíkurkjördæmi Norður [Reykjavik North]
            seats: 9
            max_adjustment_seats: 2
            candidates: ...

2) Add the compensatory district:

    .. code-block:: yaml
        :linenos:
        :emphasize-lines: 3,6

        - name: compensatory district
          type: compensatory
          mode: additional_member
          seats: 9
          skip_initial_seats: yes
          exclude: votes < 5%
          first_vote: alliance[kjördæmi:-1]
          candidates: alliance[kjördæmi]

3) Add the re-apportionment district:

    .. code-block:: yaml
        :linenos:
        :emphasize-lines: 4,6

        - name: adjustment seats to constituencies
          type: reapportionment
          # seats are re-located one by one
          strategy: parallel
          # score relative to district vote
          relative: votes
          adjustment: compensatory district
          candidates: kjördæmi
          first_vote: kjördæmi

4) Now, the full schema:

    .. code-block:: yaml
        :linenos:
        :emphasize-lines: 5,8,17,27

        name: Alþingi Íslendinga - 2013
        type: group
        method: highest_averages
        method_params:
            divisor_f: dhondt
        divisions:

        - name: compensatory district
          type: compensatory
          mode: additional_member
          seats: 9
          skip_initial_seats: yes
          exclude: votes < 5%
          first_vote: alliance[kjördæmi:-1]
          candidates: alliance[kjördæmi]

        - name: adjustment seats to constituencies
          type: reapportionment
          # seats are re-located one by one
          strategy: parallel
          # score relative to district vote
          relative: votes
          adjustment: compensatory district
          candidates: kjördæmi
          first_vote: kjördæmi

        - name: kjördæmi
          type: group
          aggregate: yes
          divisions:

          - name: Norðvesturkjördæmi [Northwest]
            seats: 7
            max_adjustment_seats: 1
            candidates: ...
          ...
          - name: Reykjavíkurkjördæmi Norður [Reykjavik North]
            seats: 9
            max_adjustment_seats: 2
            candidates: ...


Denmark - Folketing
===================

The Danish system uses two levels of districts: provinces and constituencies.

The first step allocates seats at each constituency using the d'Hondt divisors method. No threshold restrictions apply. Independent candidates are allowed.

The levelling seats will compensate for the whole country using the largest remainder method with a Hare quota. In order to participate in the process, a candidate must comply some restrictions:

- The party must reach 2% of vote.
- If a party has won 1 constituency seat, it will be allowed to participate.
- If a party reaches a Hare quota in 2 of the 3 provinces (at least the provincial votes/seats ratio), it will be allowed to participate.

Those levelling seats will be re-apportioned to provinces first, and then from provinces to constituencies.

The re-apportionment from levelling seats to provinces will use the Sainte-Laguë divisors methods, and each province is limited to a maximum of adjustment seats. The score is not relative. There is one step per district:

+----------------+----------------------+
| leveling seats | provinces            |
+================+======================+
| party 1        | party 1 @ province 1 |
+                +----------------------+
|                | ...                  |
+                +----------------------+
|                | party 1 @ province N |
+----------------+----------------------+
| ...            | ...                  |
+----------------+----------------------+
| party P        | party P @ province N |
+----------------+----------------------+

The re-apportionment from provinces to constituencies will use the :func:`Danish <interregnum.divisors.danish_divisor>` divisors method. There is one step per candidate.

+----------------------+------------------------+
| provinces            | district               |
+======================+========================+
| party 1 @ province 1 | party 1 @ district 1.1 |
+                      +------------------------+
|                      | ...                    |
+                      +------------------------+
|                      | party 1 @ district 1.D |
+----------------------+------------------------+
| party 2 @ province 1 | party 2 @ district 1.1 |
+----------------------+------------------------+
| ...                  | ...                    |
+----------------------+------------------------+
| party P @ province N | party P @ district N.D'|
+----------------------+------------------------+


1) Root node: default method is defined here.

    .. code-block:: yaml
        :linenos:
        :emphasize-lines: 4,5

        name: Folketing - 2015
        type: group
        method: highest_averages
        method_params:
            divisor_f: dhondt
        divisions:


2) Provinces and constituencies. Independent candidates should set ``max_seats: 1``.

    .. code-block:: yaml
        :linenos:
        :emphasize-lines: 9-11, 17-19, 25-27

        - name: provinces
          type: group
          aggregate: yes
          divisions:

          - name: "Hovedstaden (Capital)"
            key: Hovedstaden
            type: group
            aggregate: yes
            groupby: id
            max_adjustment_seats: 11
            divisions: ...

          - name: "Sjælland-Syddanmark (Zealand and South Denmark)"
            key: Sjælland-Syddanmark
            type: group
            aggregate: yes
            groupby: id
            max_adjustment_seats: 15
            divisions: ...

          - name: "Midtjylland-Nordjylland (Central and North Jutland)"
            key: Midtjylland-Nordjylland
            type: group
            aggregate: yes
            groupby: id
            max_adjustment_seats: 14
            divisions: ...

   Each province will generate aggregated results by party ids. A maximum number of adjustment seats is specified.


3) Compensatory district. 175 seats will be allocated nation-wide to parties using a mixed-member strategy (allocation from scratch where already allocated seats will be subtracted).

    .. code-block:: yaml
        :linenos:
        :emphasize-lines: 3,9,12,13,14

        - name: compensatory district
          type: compensatory
          mode: mixed_member
          seats: 175
          method: largest_remainder
          method_params:
            quota_f: hare
          # threshold 2
          exclude: votes < 2%
          # quota 1
          # hare quorum 2 (TODO)
          include: provinces.alliance_seats >= 1 => alliance
          first_vote: alliance[provinces:-1]
          candidates: alliance[provinces:-1]
          skip_initial_seats: yes

   The second criterion for inclusion can't be represented as a restriction yet (my apologies), but don't worry, it has never been used until today (as far as I know).


4) First re-apportionment: compensatory to provinces.

    .. code-block:: yaml
        :linenos:
        :emphasize-lines: 6,9,11,13,15

        - name: global adjustment seats to provinces
          key: reapp1
          type: reapportionment
          strategy: district
          # score is not relative
          relative: no
          method: highest_averages
          method_params:
            divisor_f: sainte_lague
          # levelling seats to parties
          adjustment: compensatory district
          # the score will be taken from provinces
          candidates: provinces
          # adjustment seats will be projected to provinces
          first_vote: provinces


5) Second re-apportionment: provinces to constituencies.

    .. code-block:: yaml
        :linenos:
        :emphasize-lines: 6,9,11,13,15

        - name: province adjustment seats to constituencies
          key: reapp2
          type: reapportionment
          strategy: candidate
          # the score is not relative
          relative: no
          method: highest_averages
          method_params:
            divisor_f: danish
          # we take the seats from the first re-apportionment
          adjustment: reapp1
          # the score will be taken from constituencies
          candidates: provinces:-1
          # seats will be projected to constituencies
          first_vote: provinces:-1


Final schema:

.. code-block:: yaml
    :linenos:
    :emphasize-lines: 8, 24, 40, 56

    name: Folketing - 2015
    type: group
    method: highest_averages
    method_params:
        divisor_f: dhondt
    divisions:

    - name: compensatory district
      type: compensatory
      mode: mixed_member
      seats: 175
      method: largest_remainder
      method_params:
        quota_f: hare
      # threshold 2
      exclude: votes < 2%
      # quota 1
      # hare quorum 2 (TODO)
      include: provinces.alliance_seats >= 1 => alliance
      first_vote: alliance[provinces:-1]
      candidates: alliance[provinces:-1]
      skip_initial_seats: yes

    - name: global adjustment seats to provinces
      key: reapp1
      type: reapportionment
      strategy: district
      # score is not relative
      relative: no
      method: highest_averages
      method_params:
        divisor_f: sainte_lague
      # levelling seats to parties
      adjustment: compensatory district
      # the score will be taken from provinces
      candidates: provinces
      # adjustment seats will be projected to provinces
      first_vote: provinces

    - name: province adjustment seats to constituencies
      key: reapp2
      type: reapportionment
      strategy: candidate
      # the score is not relative
      relative: no
      method: highest_averages
      method_params:
        divisor_f: danish
      # we take the seats from the first re-apportionment
      adjustment: reapp1
      # the score will be taken from constituencies
      candidates: provinces:-1
      # seats will be projected to constituencies
      first_vote: provinces:-1

    - name: provinces
      type: group
      aggregate: yes
      divisions:

      - name: "Hovedstaden (Capital)"
        key: Hovedstaden
        type: group
        aggregate: yes
        groupby: id
        max_adjustment_seats: 11
        divisions: ...

      - name: "Sjælland-Syddanmark (Zealand and South Denmark)"
        key: Sjælland-Syddanmark
        type: group
        aggregate: yes
        groupby: id
        max_adjustment_seats: 15
        divisions: ...

      - name: "Midtjylland-Nordjylland (Central and North Jutland)"
        key: Midtjylland-Nordjylland
        type: group
        aggregate: yes
        groupby: id
        max_adjustment_seats: 14
        divisions: ...
