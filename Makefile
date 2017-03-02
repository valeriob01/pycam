# export SVN_REPO_BASE=. if you want to use the local version instead of trunk
# from the subversion repository.

# use something like "VERSION=0.2 make" to override the VERSION on the command line
VERSION = $(shell python -c 'import pycam; print(pycam.VERSION)')
VERSION_FILE = pycam/Version.py
REPO_TAGS ?= https://pycam.svn.sourceforge.net/svnroot/pycam/tags
DIST_DIR = dist
DIST_PREFIX = pycam-
DIST_TGZ = $(DIST_DIR)/$(DIST_PREFIX)$(VERSION).tar.gz
DIST_WIN32 = $(DIST_DIR)/$(DIST_PREFIX)$(VERSION).win32.exe
PYTHON_EXE ?= python
# check if the local version of python's distutils support "--plat-name"
# (introduced in python 2.6)
DISTUTILS_PLAT_NAME = $(shell $(PYTHON_EXE) setup.py --help build_ext \
		      | grep -q -- "--plat-name" && echo "--plat-name win32")
PYTHON_CHECK_STYLE_TARGETS = pycam Tests pyinstaller/hooks/hook-pycam.py scripts/pycam setup.py

.PHONY: build clean dist tgz win32 clean \
	docs man upload-docs \
	check-style pylint-relaxed pylint-strict test \
	update-version update-deb-changelog

archive: tgz win32
	@# we can/should remove the version file in order to avoid a stale local version
	@rm -f "$(VERSION_FILE)"

clean:
	@rm -rf build
	@rm -f "$(VERSION_FILE)"

man:
	@make -C man

$(DIST_DIR):
	@mkdir -p "$@"

tgz: $(DIST_TGZ)

$(DIST_TGZ): $(DIST_DIR) build
	$(PYTHON_EXE) setup.py sdist --format gztar --dist-dir "$(DIST_DIR)"

win32: $(DIST_WIN32)

$(DIST_WIN32): $(DIST_DIR) build
	# this is a binary release
	$(PYTHON_EXE) setup.py bdist_wininst --user-access-control force \
		--dist-dir "$(DIST_DIR)" $(DISTUTILS_PLAT_NAME)

update-deb-changelog:
	@# retrieve the log of all commits since the latest release and add it to the deb changelog
	if ! grep -qFw "$(subst -,.,VERSION)" debian/changelog; then \
		git log --pretty=format:%s "$(shell echo "v$(VERSION)" | cut -f 1 -d -).." | \
			DEBFULLNAME="PyCAM Builder" DEBEMAIL="builder@pycam.org" \
			xargs -r -d '\n' -n 1 -- debchange --newversion "$(subst -,.,$(VERSION))"; \
	fi

update-version:
	@echo 'VERSION = "$(VERSION)"' >| "$(VERSION_FILE)"

check-style:
	scripts/run_flake8 $(PYTHON_CHECK_STYLE_TARGETS)

pylint-strict:
	pylint $(PYTHON_CHECK_STYLE_TARGETS)

pylint-relaxed:
	pylint -d missing-docstring,invalid-name,pointless-string-statement,fixme,no-self-use \
		-d global-statement,unnecessary-pass,too-many-arguments,too-many-branches \
		-d too-many-instance-attributes,too-many-return-statements \
		-d too-few-public-methods,too-many-locals,using-constant-test \
		-d attribute-defined-outside-init,superfluous-parens,too-many-nested-blocks \
		-d too-many-statements,unused-argument,too-many-lines \
		-d too-many-boolean-expressions,too-many-public-methods \
		$(PYTHON_CHECK_STYLE_TARGETS)


## Building the documentation/website
docs:
	mkdocs build
	
upload-docs: docs
	rsync -avz --delete --exclude=.DS_Store -e ssh site/ web.sourceforge.net:/home/project-web/pycam/htdocs/
