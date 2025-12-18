"""
Doctest for speciesfinder_main.main()

>>> from speciesfinder import speciesfinder_main as main

>>> # Pretend speciesfinder() succeeds
>>> main.speciesfinder = lambda: 0
>>> main.main()
0

>>> # Pretend speciesfinder() fails
>>> main.speciesfinder = lambda: (_ for _ in ()).throw(RuntimeError("Boom"))
>>> main.main()
1

"""
