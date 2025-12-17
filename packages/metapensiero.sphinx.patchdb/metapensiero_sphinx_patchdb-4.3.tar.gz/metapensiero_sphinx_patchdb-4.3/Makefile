# -*- coding: utf-8 -*-
# :Project:   PatchDB -- Main Makefile
# :Created:   mar 03 giu 2014 17:33:11 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2014, 2015, 2016, 2017, 2022, 2023, 2024, 2025 Lele Gaifax
#

# List of Python versions to test against, keep it in sync with flake.nix
SNAKES = 312 313

.PHONY: test

define test-snake
test:: test-python$(1)

.PHONY: test-python$(1)
test-python$(1):
	nix develop '.#test-python$(1)' -c just check
endef

$(foreach snake,$(SNAKES),$(eval $(call test-snake,$(snake))))
