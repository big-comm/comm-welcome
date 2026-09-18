PREFIX ?= /usr
PYTHON ?= python3

.PHONY: all check install
all:
	$(PYTHON) scripts/i18n.py compile

check:
	$(PYTHON) -m pytest -q
	desktop-file-validate usr/share/applications/org.bigcommunity.CommWelcome.desktop
	desktop-file-validate etc/xdg/autostart/org.bigcommunity.CommWelcome.desktop

install: all
	install -Dm755 usr/bin/comm-welcome $(DESTDIR)$(PREFIX)/bin/comm-welcome
	install -Dm644 usr/share/comm-welcome/main.py $(DESTDIR)$(PREFIX)/share/comm-welcome/main.py
	install -Dm644 usr/share/comm-welcome/style.css $(DESTDIR)$(PREFIX)/share/comm-welcome/style.css
	install -d $(DESTDIR)$(PREFIX)/share/comm-welcome/comm_welcome $(DESTDIR)$(PREFIX)/share/comm-welcome/assets
	install -m644 usr/share/comm-welcome/comm_welcome/*.py $(DESTDIR)$(PREFIX)/share/comm-welcome/comm_welcome/
	install -m644 usr/share/comm-welcome/assets/*.svg $(DESTDIR)$(PREFIX)/share/comm-welcome/assets/
	install -Dm644 usr/share/applications/org.bigcommunity.CommWelcome.desktop $(DESTDIR)$(PREFIX)/share/applications/org.bigcommunity.CommWelcome.desktop
	for size in 16 24 32 48 64 128 256 512 1024; do \
		install -Dm644 usr/share/icons/hicolor/$${size}x$${size}/apps/org.bigcommunity.CommWelcome.png \
			$(DESTDIR)$(PREFIX)/share/icons/hicolor/$${size}x$${size}/apps/org.bigcommunity.CommWelcome.png; \
	done
	install -Dm644 etc/xdg/autostart/org.bigcommunity.CommWelcome.desktop $(DESTDIR)/etc/xdg/autostart/org.bigcommunity.CommWelcome.desktop
	install -Dm644 etc/skel/.config/comm-welcome/autostart-enabled $(DESTDIR)/etc/skel/.config/comm-welcome/autostart-enabled
	install -d $(DESTDIR)$(PREFIX)/share/locale
	cp -a usr/share/locale/. $(DESTDIR)$(PREFIX)/share/locale/
	install -Dm644 LICENSE $(DESTDIR)$(PREFIX)/share/licenses/comm-welcome/LICENSE
	install -Dm644 docs/ASSETS.md $(DESTDIR)$(PREFIX)/share/licenses/comm-welcome/ASSETS.md
	install -Dm644 README.md $(DESTDIR)$(PREFIX)/share/doc/comm-welcome/README.md
	install -d $(DESTDIR)$(PREFIX)/share/doc/comm-welcome/docs
	install -m644 docs/*.md $(DESTDIR)$(PREFIX)/share/doc/comm-welcome/docs/
