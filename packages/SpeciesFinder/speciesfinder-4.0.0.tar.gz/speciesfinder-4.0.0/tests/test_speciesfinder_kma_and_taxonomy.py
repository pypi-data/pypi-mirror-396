"""
Doctests for speciesfinder_kma_and_taxonomy

Testing `run_kma()` function:

>>> from speciesfinder.speciesfinder_kma_and_taxonomy import run_kma
>>> import tempfile, os
>>> import subprocess

>>> # Mock subprocess to simulate KMA execution  with single and double reads testing
>>> tmpdir = tempfile.mkdtemp()

>>> class MockProcess:
...     def __init__(self): self.returncode = 0
...     def communicate(self): return (b'output', b'error')
>>> subprocess.Popen = lambda *args, **kwargs: MockProcess()

>>> run_kma(["file1.fq", "file2.fq"], ["db1"], "/path/to/kma", tmpdir)  
>>> run_kma(["file1.fq"], ["db1"], "/path/to/kma", tmpdir)


Testing `generate_json_output()` function.

>>> from speciesfinder.speciesfinder_kma_and_taxonomy import generate_json_output
>>> import tempfile, os, json
>>> from types import SimpleNamespace

>>> # Generate output json by mocking a hits dict testing
>>> tmpdir = tempfile.mkdtemp()
>>> args = SimpleNamespace(infile=["input.fasta"], tax="tax.txt", db_path="db/path/file.db", extended_output=True)
>>> hits = {
...     "AK41": {"Species": "E.coli", "Assembly": "AK41", "Accession Number": "ACC1",
...              "Score": 100, "Depth": 5.0, "Query_Coverage": 80.0,
...              "Template_length": 1000, "Template_Coverage": 90.0}
... }
>>> generate_json_output(hits, args, tmpdir, "bacteria", "/path/to/kma","1.0", "abc123", "abcdef123456")
>>> os.path.exists(os.path.join(tmpdir, "data.json"))
True
>>> with open(os.path.join(tmpdir, "data.json")) as f:
...     data = json.load(f)
>>> sorted(list(data["seq_region"].keys()))
['AK41']
>>> data["result_summary"][0].startswith("E.coli")
True

"""
