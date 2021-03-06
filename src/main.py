#!/usr/bin/env python3

import sys
from os.path import dirname, join

try:
	import gnank
	gnank_dir = dirname(sys.argv[0])
except ImportError:
	prefix = dirname(dirname(sys.argv[0]))
	gnank_dir = join(prefix, "share", "gnank")
	sys.path.insert(0, gnank_dir)
	import gnank

gnank.main(gnank_dir)
