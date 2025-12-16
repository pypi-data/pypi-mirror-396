*A simple but flexible handler of the SUSY Les Houches Accord (SLHA) data format.*

pyslha is a parser/writer module for particle physics SUSY Les Houches Accord
(SLHA) supersymmetric spectrum/decay files, and a collection of scripts which
use the interface, e.g. for conversion to and from the legacy ISAWIG format, or
to plot the mass spectrum and decay chains.

The current release supports SLHA version 1, and as far as I'm aware is also
fully compatible with SLHA2: the block structures are read and accessed
generically. If you have any problems, please provide an example input file and
I'll happily investigate. SLHA3 is not yet supported (or standardised) but in
recent releases the new structures will not crash the parser. Support will be
added once the format is standardised (and in response to demand!)

The plotting script provides output in PDF, EPS and PNG via LaTeX and the TikZ
graphics package, and as LaTeX/TikZ source for direct embedding into documents or
user-tweaking of the generated output.

Users of version 2.x should note that the interface has changed a little in
version 3.0.0 and onward: there are now generic read()/write() functions which
can operate on filenames or file objects, and all I/O functions now
return/accept a single Doc object rather than a tuple of blocks, decays,
etc. dicts. This single-object interface to the SLHA document allows for more
coherent handling of the data, as well as better robustness against future
changes in the format and planned support for documentation comments.


## API example

```python
>>> import pyslha
>>> # generic read from file:
>>> d = pyslha.read('spcfiles/sps1a.spc')
>>> d
<PySLHA Doc: 22 blocks, 35 decays, 0 xsections>
>>> # or, to ignore blocks known to be e.g. badly formatted:
>>> d = pyslha.read('spcfiles/sps1a.spc', ignoreblocks=['DCINFO'])
>>> d
<PySLHA Doc: 21 blocks, 35 decays, 0 xsections>
>>> d.blocks
Blocks
  SPINFO { 1 : SOFTSUSY; 2 : 2.0.5 }
  MODSEL { 1,1 : sugra }
  SMINPUTS { 1 :  1.27934000e+02; 2 :  1.16637000e-05; ...
  ...
>>> d.blocks.has_key('MODSEL')
True
>>> d.blocks['MODSEL']
MODSEL { 1,1 : sugra }
>>> d.blocks['MODSEL'][1,1]
'sugra'
>>> d.blocks['MODSEL'][1,2] = 'foo'
>>> d.blocks['MODSEL']
MODSEL { 1,1 : sugra; 1,2 : foo }
```

The `Block` interface also supplies dict-like `has_key()`, `keys()`, and `items()`
methods, as well as more specialist `value()`, `set_value()` and `is_single_valued()`
methods for improved access to `ALPHA` and any other unindexed blocks.

The decay system has a similar interface to that of the generic `Block` for
accessing particle decay-channel information:

```python
>>> d.decays.keys()
[23, 24, 6, 25, 35, 36, 37, 1000021, 1000006, 2000006, 1000005, 2000005, ...
>>> d.decays[1000021]
1000021 : mass = 6.07713704e+02 GeV : total width = 5.50675438e+00 GeV
   1.05840237e-01 [1000005, -5]
   1.05840237e-01 [-1000005, 5]
   ...
```

The `DECAY` blocks in SLHA files are in fact mapped into `Particle` objects, each of
which contains multiple `Decay` objects. Check the Python documentation for `Doc`,
`Block`, `Particle` and `Decay`, plus the `pyslha` module free functions for I/O.


## Citation

If you use PySLHA, for either model data handling or spectrum visualisation,
please cite the paper: http://arxiv.org/abs/1305.4194
