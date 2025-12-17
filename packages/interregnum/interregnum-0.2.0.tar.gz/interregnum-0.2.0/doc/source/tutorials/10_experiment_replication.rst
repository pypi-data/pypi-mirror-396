.. SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
..
.. SPDX-License-Identifier: LGPL-3.0-or-later

Tutorial 10: Experiment replication
***********************************

In order to resolve ties, an allocator could use a random generator to break it. In this tutorial we will learn how we can replicate some computation.

Let's create a one-seat constituency where the winner is chosen by :class:`first-past-the-post <interregnum.methods.WinnerTakesAllAllocator>` and all the candidates received the same amount of vote:

.. code-block:: yaml
    :linenos:
    :emphasize-lines: 5,7,9

    name: Spider-Man Pointing
    method: first_past_the_post
    candidates:
    - name: Spiderman 1
      vote: 2000
    - name: Spiderman 2
      vote: 2000
    - name: Spiderman 3
      vote: 2000


If we compute the result, all of candidates can be chosen with the same probability:

.. code-block:: console

    $ interregnum-cli calc spiderman-pointing.yaml spiderman-pointing-result.yaml


Let's examine the result:

.. code-block:: yaml
    :linenos:
    :emphasize-lines: 17-21, 45-46

    # spiderman-pointing-result.yaml

    type: district
    name: Spider-Man Pointing
    method: first_past_the_post
    initial_seats: min_seats
    resume_allocation: false
    candidates:
    - name: Spiderman 1
      groups: []
    - name: Spiderman 2
      groups: []
    - name: Spiderman 3
      groups: []
    result:
      allocation:
      - name:
          name: Spiderman 2
          alliance: Spiderman 2
        votes: 0
        seats: 1
      data:
        log:
        - EVENT: tie
          candidates:
          - name: Spiderman 1
            alliance: Spiderman 1
          - name: Spiderman 2
            alliance: Spiderman 2
          - name: Spiderman 3
            alliance: Spiderman 3
          condition:
            best_score: 0
        - EVENT: winner
          target:
            name: Spiderman 1
            alliance: Spiderman 1
          criterion: tie_break_random
          quota: 0
        threshold: 0
        remaining_seats: 0
        rounds: 1
      deterministic: false
      random_state:
        deterministic: false
        uses: 1
        seed: 1839732977
        original_state: null

In this case the winner is ``Spiderman 2``, but the result was non-deterministic.

If we look at the event log, we can see that there is a tie between the 3 Spidermen, and then a winner was chosen randomly.

.. code-block:: yaml
    :linenos:
    :lineno-start: 23
    :emphasize-lines: 4,14,18

    log:
    - EVENT: tie
      candidates:
      - name: Spiderman 1
        alliance: Spiderman 1
      - name: Spiderman 2
        alliance: Spiderman 2
      - name: Spiderman 3
        alliance: Spiderman 3
      condition:
        best_score: 0
    - EVENT: winner
      target:
        name: Spiderman 1
        alliance: Spiderman 1
      criterion: tie_break_random
      quota: 0
    threshold: 0
    remaining_seats: 0
    rounds: 1

If we want to reproduce this result, we can use the seed provided in the section ``random_state``:

.. code-block:: yaml
    :linenos:
    :lineno-start: 44
    :emphasize-lines: 4

    random_state:
      deterministic: false
      uses: 1
      seed: 1839732977
      original_state: null


Now let's add that random generator seed to our initial schema:


.. code-block:: yaml
    :linenos:
    :emphasize-lines: 3

    name: Spider-Man Pointing
    method: first_past_the_post
    random_seed: 1839732977
    candidates:
    - name: Spiderman 1
      vote: 2000
    - name: Spiderman 2
      vote: 2000
    - name: Spiderman 3
      vote: 2000


Now, the result should be the same every time it is computed. Be aware that the implementation of this feature can vary depending of the allocator, so you should consult the :doc:`API documentation <../modules/modules>` in each case.