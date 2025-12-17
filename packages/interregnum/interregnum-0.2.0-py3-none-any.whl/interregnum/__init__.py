#!/usr/bin/source python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

r"""
Algorithms for comuting electoral systems.

Methods (:mod:`.methods`)
------------------------------------

Methods allocate seats given a set of votes.

Implemented methods are grouped by their required input:

- Single vote (:mod:`.methods.singlevote`)
- Preferential vote (:mod:`.methods.preferential`)
- Bi-proportional system (:mod:`.methods.biproportional`)
- Compensatory systems (:mod:`.methods.compensatory`)
- Adapters (:mod:`.methods.compensatory`)


Districts (:mod:`.district`)
---------------------------------------

This subpackage allows the seats allocation through multiple hierarchical districts.

- Nodes (:mod:`.district.node`):
    - District (:mod:`.district.district`)
    - Group (:mod:`.district.group`)
    - Compensatory (:mod:`.district.compensatory`)
    - Reapportionment (:mod:`.district.reapportionment`)
- Contenders (:mod:`.district.contenders`)
- Counting (:mod:`.district.counting`)
- References (:mod:`.district.references`)
- Restrictions (:mod:`.district.restriction`)
- Serialization (:mod:`.district.serialize`)
- I/O (:mod:`.district.io`)


:mod:`Collections <.collections>`
--------------------------------------------

Collections map functions to string identifiers. Additionally, new custom functions can be
registered as the user needs.

- Allocators (:data:`.methods.allocators`)
- Divisors (:data:`.divisors.divisors`)
- Divsor iterators (:data:`.divisors.divisor_iterators`)
- Quotas (:data:`.quotas.quotas`)
- Ranks (:data:`.ranks.ranks`)
- Rounding (:data:`.rounding.roundings`)
- Signposts (:data:`.rounding.signposts`)
- Transfers (:data:`.methods.preferential.transfers`)

.. _interregnum_biblio:

Bibliography
------------

.. [Gallagher:1992] Gallagher, M. (1992). Comparing proportional representation electoral systems:
   Quotas, thresholds, paradoxes and majorities. British Journal of
   Political Science, 22(4), 469–496.

.. code-block:: bibtex

    @article{Gallagher:1992,
        author = {Gallagher, Michael},
        journal = {British Journal of Political Science},
        number = {4},
        pages = {469--496},
        publisher = {Cambridge University Press},
        title = {{Comparing proportional representation electoral systems: Quotas, thresholds,
                  paradoxes and majorities}},
        volume = {22},
        year = {1992}
    }


.. [Denmark:2011] Elklit, J., Pade, A. B., & Miller, N. N. (Eds.). (2011). The Parliamentary
   Electoral System in Denmark. Guide to the Danish electoral system [Techreport]. Ministry of
   the Interior.

.. code-block:: bibtex

    @techreport{ElklitPadeMiller:2011,
        editor = {Elklit, J{\o}rgen and Pade, Anne Birte and Miller, Nicoline Nyholm},
        institution = {Ministry of the Interior and Health and The Danish Parliament},
        isbn = {978-87-7982-116-3},
        title = {{The Parliamentary Electoral System in Denmark.
                  Guide to the Danish electoral system}},
        year = {2011}
    }


.. [Norway:2023] Lov om valg til Stortinget, fylkesting og kommunestyrer (valgloven). (2023).
   [Techreport].

.. code-block:: bibtex

    @techreport{lovdata2023,
        address = {https://lovdata.no/dokument/NL/lov/2023-06-16-62},
        title = {{Lov om valg til Stortinget, fylkesting og kommunestyrer (valgloven)}},
        year = {2023}
    }

.. [KohlerZeh:2012] Kohler, U., & Zeh, J. (2012). Apportionment methods. The Stata Journal,
   12(3), 375–392.

.. code-block:: bibtex

    @article{KohlerZeh:2012,
        author = {Kohler, Ulrich and Zeh, Janina},
        journal = {The Stata Journal},
        number = {3},
        pages = {375--392},
        publisher = {SAGE Publications Sage CA: Los Angeles, CA},
        title = {{Apportionment methods}},
        volume = {12},
        year = {2012}
    }

.. [Reitzig:2014] Reitzig, R., & Wild, S. (2015). A practical and worst-case efficient algorithm
   for divisor methods of apportionment. ArXiv Preprint ArXiv:1504.06475.

.. code-block:: bibtex

    @article{ReitzigWild:2015,
        author = {Reitzig, Raphael and Wild, Sebastian},
        journal = {arXiv preprint arXiv:1504.06475},
        title = {{A practical and worst-case efficient algorithm for divisor methods of
                  apportionment}},
        year = {2015}
    }

.. [DorfleitnerKlein:1997] Dorfleitner, Gregor and Klein, Thomas (1997). Rounding with multiplier
   methods: An efficient algorithm and applications in statistics. Statistical Papers 40,
   143-157 (1999)

.. code-block:: bibtex

    @article{DorfleitnerKlein:1999,
        author = {Dorfleitner, Gregor and Klein, Thomas},
        journal = {Statistical Papers},
        pages = {143--157},
        publisher = {Springer},
        title = {{Rounding with multiplier methods: An efficient algorithm and applications in
                  statistics}},
        volume = {40},
        year = {1999}
    }


.. [Zachariasen:2006] Zachariasen, Martin (2006). Algorithmic Aspects of Divisor-Based
   Biproportional Rounding. ISSN 0107-8283

.. code-block:: bibtex

    @article{Zachariasen:2006,
        author = {Zachariasen, Martin},
        journal = {Typescript, April},
        title = {{Algorithmic aspects of divisor-based biproportional rounding}},
        year = {2006}
    }

.. [Loreg:1985] Ley Orgánica 5/1985, de 19 de junio, del Régimen Electoral General. (No. 147;
   Boletı́n Oficial Del Estado). (1985). Jefatura del Estado (España).

.. code-block:: bibtex

    @techreport{Loreg:1985,
        month = jun,
        number = {147},
        publisher = {Jefatura del Estado (Espa{\~n}a)},
        series = {{Bolet{\'\i}n Oficial del Estado}},
        title = {{Ley Org{\'a}nica 5/1985, de 19 de junio, del R{\'e}gimen Electoral General.}},
        year = {1985}
    }


.. [Schulze:2011] Schulze, M. (2011). A new monotonic, clone-independent, reversal symmetric, and
   condorcet-consistent single-winner election method. Social Choice and Welfare, 36(2), 267–303. http://dblp.uni-trier.de/db/journals/scw/scw36.html#Schulze11;%20http://dx.doi.org/10.1007/s00355-010-0475-4;%20https://www.bibsonomy.org/bibtex/2bf639adac1ce14c4a937a7b13ee640ba/dblp

.. code-block:: bibtex

    @article{journals/scw/Schulze11,
        author = {Schulze, Markus},
        journal = {Social Choice and Welfare},
        number = 2,
        pages = {267--303},
        timestamp = {2012-03-27T11:34:04.000+0200},
        title = {{A new monotonic, clone-independent, reversal symmetric, and condorcet-consistent
                  single-winner election method.}},
        url = {http://dblp.uni-trier.de/db/journals/scw/scw36.html#Schulze11;
               http://dx.doi.org/10.1007/s00355-010-0475-4; https://www.bibsonomy.org/bibtex/2bf639adac1ce14c4a937a7b13ee640ba/dblp},
        volume = 36,
        year = 2011
    }

.. [EireSTV] A Guide to Ireland's PR-STV Voting System. (n.d.). Department of Housing,
   Planning & Local Government. Rialtas na hÉireann.

.. code-block:: bibtex

    @booklet{STVEire,
        address = {https://assets.gov.ie/111110/03f591cc-6312-4b21-8193-d4150169480e.pdf},
        institution = {Department of Housing, Planning \& Local Government.
                       Rialtas na h{\'E}ireann},
        title = {{A Guide to Ireland{\rq}s PR-STV Voting System}}
    }

.. [AusProp] Proportional Representation Voting Systems of Australia’s Parliaments. (n.d.).
   Electoral Council of Australia.

.. code-block:: bibtex

    @booklet{AusProp,
        address = {https://www.ecanz.gov.au/electoral-systems/proportional},
        institution = {Electoral Council of Australia},
        title = {{Proportional Representation Voting Systems of Australia's Parliaments}}
    }

.. [Miragliotta2002] Miragliotta, N. (2002). Determining the result: Transferring Surplus Votes
   in the Western Australian Legislative Council [Techreport]. Western Australian Electoral
   Commission.

.. code-block:: bibtex

    @techreport{Miragliotta2002,
        address = {0-7307-5809-5},
        author = {Miragliotta, Narelle},
        institution = {Western Australian Electoral Commission},
        location = {Perth Western Australia},
        title = {{Determining the result: Transferring Surplus Votes in the Western Australian
                  Legislative Council}},
        year = {2002}
    }

.. [Iceland:2013] Helgason, T. (2013). Apportionment of Seats to Althingi, the Icelandic Parliament:
   Analysis of the Elections on May 10, 2003, May 12, 2007, April 25, 2009 and April 27, 2013
   [Techreport]. The National Electoral Commission of Iceland.

.. code-block:: bibtex

    @techreport{Helgason:2013,
        author = {Helgason, Thorkell},
        institution = {The National Electoral Commission of Iceland},
        title = {{Apportionment of Seats to Althingi, the Icelandic Parliament: Analysis of the
                  Elections on May 10, 2003, May 12, 2007, April 25, 2009 and April 27, 2013}},
        year = {2013}
    }

.. [Scotland:2024] Scottish Parliament electoral system (SPICe Fact Sheet). (2024). [Techreport].
   Scottish Parliament Information Centre. https://www.parliament.scot/-/media/files/spice/factsheets/parliamentary-business/scottish-parliament-electoral-system-12-may-2021.pdf

.. code-block:: bibtex

    @techreport{Scotland:2024,
        publisher = {Scottish Parliament Information Centre},
        series = {{SPICe Fact Sheet}},
        title = {{Scottish Parliament electoral system}},
        url = {https://www.parliament.scot/-/media/files/spice/factsheets/parliamentary-business/scottish-parliament-electoral-system-12-may-2021.pdf},
        year = {2024}
    }

.. [Germany:2025] Wahl zum 21. Deutschen Bundestag am 23. Februar 2025. (2025). [Techreport].
   Die Bundeswahlleiterin. https://www.bundeswahlleiterin.de/dam/jcr/5316c01c-8a1e-44d0-8075-eab495f466b6/btw25_heft3.pdf

.. code-block:: bibtex

    @techreport{bundeswahlleiterin2025,
        publisher = {Die Bundeswahlleiterin},
        title = {{Wahl zum 21. Deutschen Bundestag am 23. Februar 2025}},
        url = {https://www.bundeswahlleiterin.de/dam/jcr/5316c01c-8a1e-44d0-8075-eab495f466b6/btw25_heft3.pdf},
        year = {2025}
    }

.. [Pukelsheim:2013] Pukelsheim, F., & others. (2013). The ABC of Apportionment Numeracy: The
   Augsburg Bazi Pseudo-Code [Version 2013.07]. Bazi Team.

.. code-block:: bibtex

    @misc{Pukelsheim:2013,
        author = {Pukelsheim, Friedrich and others},
        institution = {Universit{\"a}t Augsburg},
        organization = {Bazi Team},
        title = {{The ABC of Apportionment Numeracy: The Augsburg Bazi Pseudo-Code
                  [Version 2013.07]}},
        year = {2013}
    }

.. [Oelbermann:2016] Oelbermann, K.-F. (2016). Alternate Scaling algorithm for biproportional
   divisor methods. Math. Soc. Sci., 80, 25–32. http://dblp.uni-trier.de/db/journals/mss/mss80.html#Oelbermann16;%20https://doi.org/10.1016/j.mathsocsci.2016.02.003;%20https://www.bibsonomy.org/bibtex/25eedf3fe678e4d47cdd9ef6eaf52809c/dblp

.. code-block:: bibtex

    @article{journals/mss/Oelbermann16,
        address = {http://dblp.uni-trier.de/db/journals/mss/mss80.html\#Oelbermann16},
        author = {Oelbermann, Kai-Friederike},
        journal = {Math. Soc. Sci.},
        pages = {25--32},
        timestamp = {2020-02-25T13:14:02.000+0100},
        title = {{Alternate Scaling algorithm for biproportional divisor methods}},
        url = {http://dblp.uni-trier.de/db/journals/mss/mss80.html#Oelbermann16;
               https://doi.org/10.1016/j.mathsocsci.2016.02.003; https://www.bibsonomy.org/bibtex/25eedf3fe678e4d47cdd9ef6eaf52809c/dblp},
        volume = 80,
        year = 2016
    }

"""

from importlib.metadata import version, PackageNotFoundError

try:
    from _version import __version__, __version_tuple__

    __all__ = ["__version__", "__version_tuple__"]
except ImportError:
    try:
        __version__ = version("interregnum")
        __all__ = ["__version__"]
    except PackageNotFoundError:
        __version__ = "0.0.1"
