NAME=epublibexample
PLUGIN_ZIP=$(NAME).zip

build_plugin:
	@echo "Building sigil plugin..."
	@zip -qr $(NAME).zip $(NAME)/*
	@if [ -d ~/.local/share/sigil-ebook/sigil/plugins/$(NAME) ]; then \
		 echo " -> Found sigil plugins folder. Overwriting..."; \
		 unzip -oq $(PLUGIN_ZIP) -d ~/.local/share/sigil-ebook/sigil/plugins/; \
	 fi
