.. SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
..
.. SPDX-License-Identifier: LGPL-3.0-or-later

Command Line Interface
**********************

.. code-block:: console

    $ interregnum-cli --help

    usage: interregnum-cli graph [-h] [--src-encoding SRC_ENCODING] source [dotfile]

    positional arguments:
    source                electoral system
    dotfile               dot file (default: None)

    options:
    -h, --help            show this help message and exit
    --src-encoding SRC_ENCODING
                            source char encoding (default: utf-8)
    (venv-310-sys) hector@amilcar:~/proyectos/interregnum/interregnum/src [git:t3-dot-format+? d77220e2acf0] $ interregnum-cli --help
    usage: interregnum-cli [-h] [--version] [--decimals DECIMALS] [-v] {calculate,c,calc,allocate,alloc,dump,d,list,l,collection,graph,g,dot,deps} ...

    Calculate election results

    positional arguments:
    {calculate,c,calc,allocate,alloc,dump,d,list,l,collection,graph,g,dot,deps}
        calculate (c, calc, allocate, alloc)
                            Allocate seats for an electoral system.
        dump (d)            Dump an electoral system schema to file.
        list (l, collection)
                            Enumerate a collection.
        graph (g, dot, deps)
                            Generate a dependency graph in dot format.

    options:
    -h, --help            show this help message and exit
    --version             show program's version number and exit
    --decimals DECIMALS   show rational numbers using floating point notation rounded to this number of decimals, otherwise use original fractions. (default: None)
    -v, --verbose         show additional info (default: False)



Calculate
=========

.. code-block:: console

    $ interregnum-cli calculate --help

    usage: interregnum-cli calculate [-h] [--src-encoding SRC_ENCODING] [--tgt-encoding TGT_ENCODING]
                                     [--decimals DECIMALS] [-c CANDIDATES [CANDIDATES ...]]
                                     [-p PREFERENCES [PREFERENCES ...]] [-r RESULTS]
                                     source target

    positional arguments:
      source                electoral system (supported formats: json, yaml)
      target                electoral system with results (supported formats: json, yaml)

    options:
      -h, --help            show this help message and exit
      --src-encoding SRC_ENCODING
                            source char encoding (default: utf-8)
      --tgt-encoding TGT_ENCODING
                            target char encoding (default: utf-8)
      --decimals DECIMALS   show rational numbers using floating point notation rounded to this number of decimals,
                            otherwise use original fractions. (default: None)

    optional input data:
      -c CANDIDATES [CANDIDATES ...], --candidates CANDIDATES [CANDIDATES ...]
                            Populate candidates with data from this files. If the target node is not specified in the
                            files, prefix the node key to the filename: <node key>:<file name>. If no node key is
                            found, all data will be populated to the root node. Supported formats: json, yaml, csv,
                            tsv. (default: None)
      -p PREFERENCES [PREFERENCES ...], --preferences PREFERENCES [PREFERENCES ...]
                            Populate preferences with data from this files. The target node can be specified prefixing
                            it to the filename: <node key>:<file name>. If no node key is found, all data will be
                            populated to the root node. Supported formats: pref, yaml, json. (default: None)

    optional output data:
      -r RESULTS, --results RESULTS
                            Dump results to this file. Supported formats: json, yaml, csv, tsv (default: None)


Examples
--------

Calculate a schema:

.. code-block:: console

    $ interregnum-cli calc freedonia.yaml results.yaml

Calculate a schema and write results to a separate file:

.. code-block:: console

    $ interregnum-cli calc freedonia.yaml -r results.csv

Calculate a schema and fill candidates from a different file:

.. code-block:: console

    $ interregnum-cli calc elecciones.yaml -c votes.csv

Calculate a schema and fill candidates for nodes identified as ``Sevilla`` and ``Madrid``:

.. code-block:: console

    $ interregnum-cli calc elecciones.yaml \
        -c Sevilla:votes_sev.csv Madrid:votes_mad.csv

Calculate a schema and fill preferences:

.. code-block:: console

    $ interregnum-cli calc au_northern_territory.yaml -p nt.pref


Calculate a schema and fill preferences for nodes identified as ``Northern Territory`` and ``Australian Capital Territory``:

.. code-block:: console

    $ interregnum-cli calc au.yaml \
        -p "Northern Territory:nt.pref" \
        "Australian Capital Territory:act.pref"


Dump schema
===========

Return a clean schema without results nor candidates.

.. code-block:: console

    $ interregnum-cli dump --help
    usage: interregnum-cli dump [-h] [-s] [--src-encoding SRC_ENCODING] [--tgt-encoding TGT_ENCODING] source target

    positional arguments:
      source                original electoral system
      target                destination file

    options:
      -h, --help            show this help message and exit
      -s, --skeleton        do not dump ballots or results (default: False)
      --src-encoding SRC_ENCODING
                            source char encoding (default: utf-8)
      --tgt-encoding TGT_ENCODING
                            target char encoding (default: utf-8)



List collections
================

.. code-block:: console

    $ interregnum-cli list --help
    usage: interregnum-cli list [-h]
                                [{allocators,divisor_iterators,divisors,quotas,ranks,roundings,signposts,transfers}]

    positional arguments:
      {allocators,divisor_iterators,divisors,quotas,ranks,roundings,signposts,transfers}
                            collection name (default: None)

    options:
      -h, --help            show this help message and exit


Examples
--------

List divisors:

.. code-block:: console

    $ interregnum-cli list divisors

    divisors
    --------
    * 'd'hondt','dhondt','greatest-divisors','greatest_divisors','jefferson'
    * 'sainte-lague','sainte-laguë','sainte_lague','sainte_laguë','webster'
    * 'sainte-lague-1.4','sainte-laguë-1.4','sainte_lague_1.4','sainte_laguë_1.4'
    * 'imperiali'
    * 'belgian-imperiali','belgian_imperiali'
    * 'danish'
    * 'dean','harmonic-mean','harmonic_mean'
    * 'equal-proportions','equal_proportions','huntington-hill','huntington_hill'
    * 'huntington-hill1','huntington_hill1'
    * 'modified-sainte-lague','modified-sainte-laguë','modified_sainte_lague','modified_sainte_laguë'
    * 'adams','smallest-divisors','smallest_divisors'



List everything:

.. code-block:: console

    $ interregnum-cli list

    allocators
    ----------
    * 'borda','borda_count'
    * 'condorcet_ranked_pairs','ranked_pairs'
    * 'condorcet_copeland','copeland'
    * 'condorcet_minimax','minimax'
    * 'single_transferable_vote'
    * 'alternative_voting','instant_run_off','instant_runoff','ranked_choice','ranked_choice_voting','transferable_voting'
    * 'highest-averages','highest_averages'
    * 'iterative-divisor','iterative_divisor'
    * 'largest-remainder','largest_remainder'
    * 'limited_voting','partial_block_voting'
    * 'first_past_the_post','winner_takes_all'
    * 'alternate_scaling','alternate_scaling_tie_transfer','biproportional'
    * 'additional_member','levelling_seats'
    * 'mixed_member'
    * 'no-op','noop','nop'

    divisor_iterators
    -----------------
    * 'd'hondt','dhondt','jefferson'
    * 'sainte-lague','sainte-laguë','sainte_lague','sainte_laguë','webster'
    * 'sainte-lague-1.4','sainte-laguë-1.4','sainte_lague_1.4','sainte_laguë_1.4'
    * 'imperiali'
    * 'belgian-imperiali','belgian_imperiali'
    * 'danish'
    * 'adams'

    divisors
    --------
    * 'd'hondt','dhondt','greatest-divisors','greatest_divisors','jefferson'
    * 'sainte-lague','sainte-laguë','sainte_lague','sainte_laguë','webster'
    * 'sainte-lague-1.4','sainte-laguë-1.4','sainte_lague_1.4','sainte_laguë_1.4'
    * 'imperiali'
    * 'belgian-imperiali','belgian_imperiali'
    * 'danish'
    * 'dean','harmonic-mean','harmonic_mean'
    * 'equal-proportions','equal_proportions','huntington-hill','huntington_hill'
    * 'huntington-hill1','huntington_hill1'
    * 'modified-sainte-lague','modified-sainte-laguë','modified_sainte_lague','modified_sainte_laguë'
    * 'adams','smallest-divisors','smallest_divisors'

    quotas
    ------
    * 'hare'
    * 'majority'
    * 'hagenbach-bischoffdroop_fractional','hagenbach_bischoff'
    * 'droop'
    * 'imperiali'
    * 'imperiali3','imperiali_3'
    * 'infinity'

    ranks
    -----
    * 'borda','n'
    * 'n-1','n_1','tournament'
    * 'dowdall','nauru'

    roundings
    ---------
    * 'round'
    * 'int'
    * 'floor'
    * 'ceil'
    * 'none','noop'
    * 'adams'
    * 'sainte_lague','sainte_laguë','webster'
    * 'dhondt','jefferson'

    signposts
    ---------
    * 'adams'
    * 'sainte_lague','sainte_laguë','webster'
    * 'dhondt','jefferson'

    transfers
    ---------
    * 'inclusive_gregory','unweighted_gregory','unweighted_inclusive_gregory'
    * 'weighted_gregory','weighted_inclusive_gregory'
    * 'gregory','last_parcel'


Graph
=====

Write a dependency graph using the Graphviz DOT format.

.. code-block:: console

    $ interregnum-cli graph --help

    usage: interregnum-cli graph [-h] [--src-encoding SRC_ENCODING] source [dotfile]

    positional arguments:
    source                electoral system
    dotfile               dot file (default: None)

    options:
    -h, --help            show this help message and exit
    --src-encoding SRC_ENCODING
                            source char encoding (default: utf-8)
