# Simple makefile for debian packaging system

INSTALLFILES := $(shell find . \
                        \( \
                        -path '.git' -prune -or \
                        -path './debian' -prune -or \
                        -path './dependencies' -prune -or \
                        -not -name '*.log' -and \
                        -not -name 'Makefile' -and \
                        -not -name 'README' -and \
                        -not -name 'pgsql.sql' -and \
                        -not -name 'credentials_template.py' -and \
                        -not -name 'credentials.py' -and \
                        -not -name 'configure-stamp' -and \
                        -not -name 'build-stamp' \
                        \) \
                        -print | cut -c3- )

POSTINSTALL := $(shell find postinstall -maxdepth 1 -type f )

default: all

install: $(INSTALLFILES)
	list='$(INSTALLFILES)'; \
        for p in $$list; do \
          if test -f $$p; then \
            echo install -D -m 0644 $$p ${DESTDIR}/usr/share/webpy-example/$$p ;\
            install -D -m 0644 $$p ${DESTDIR}/usr/share/webpy-example/$$p ;\
          fi \
        done

all:

clean:

