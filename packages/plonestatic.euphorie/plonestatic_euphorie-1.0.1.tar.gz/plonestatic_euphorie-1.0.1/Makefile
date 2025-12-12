.DEFAULT_GOAL := help


all: ## Update proto, compile it and install the resources
	@make update-proto
	@make jekyll
	@make resources-install

##

var/prototype: # Get the latest version of the prototype
	mkdir -p var
	@if [ ! -d "var/prototype" ]; then \
		gitman update || (git clone git@github.com:syslabcom/oira.prototype.git var/prototype); \
	else \
		gitman update || (cd var/prototype && git pull); \
	fi;

.PHONY: update-proto
update-proto: var/prototype  ## Update the prototype
	@gitman update || (cd var/prototype && git pull)

.PHONY: jekyll
jekyll: ## Compile the prototype with Jekyll
	@if [ ! -d "var/prototype" ]; then make var/prototype; fi;
	@echo 'DO: rm prototype/stamp-bundler to force Jekyll re-install'
	@cd var/prototype && make jekyll


.PHONY: resources-install
resources-install:  ## Install the resources from the prototype folder to the plone static resources folder
	@if [ ! -d "var/prototype/_site/assets" ]; then make jekyll; fi;

	@echo "🧪 Copy resources from prototype."
	@rm -rf src/plonestatic/euphorie/resources/*
	@mkdir -p src/plonestatic/euphorie/resources/

	@# The following command will copy the main assets from the compiled prototype to the resources folder
	@rsync -a --delete var/prototype/_site/assets/ src/plonestatic/euphorie/resources/assets/ \
		--exclude="/daimler/" \
		--exclude="/oira/certificates/" \
		--exclude="/oira/i18n/" \
		--exclude="/oira/script" \
		--exclude="/oira/style/*.gif" \
		--exclude="/oira/style/*.jpg" \
		--exclude="/oira/style/*.png" \
		--exclude="/oira/style/*.svg" \
		--exclude="/oira/style/fontello-*/" \
		--exclude="/oira/style/fonts/" \
		--exclude="/oira/style/photoswipe/" \
		# end of rsync command

	@# Copy example report images
	@rsync -a --delete var/prototype/_site/media/example-* src/plonestatic/euphorie/resources/media

	@# The following commands will copy the resources linked from the assets and excluded in the rsync command above
	@cp var/prototype/_site/assets/oira/style/oira-logo-dp.svg src/plonestatic/euphorie/resources/assets/oira/style/oira-logo-dp.svg
	@cp var/prototype/_site/assets/oira/style/placeholder-1x1.png src/plonestatic/euphorie/resources/assets/oira/style/placeholder-1x1.png
	@cp var/prototype/_site/assets/oira/style/placeholder-21x9.png src/plonestatic/euphorie/resources/assets/oira/style/placeholder-21x9.png
	@cp var/prototype/_site/assets/oira/style/defaultUser-168.png src/plonestatic/euphorie/resources/assets/oira/style/defaultUser-168.png
	@./scripts/copy_resources.py

##

.PHONY: clean-proto
clean-proto: var/prototype  ## Clean the prototype
	cd var/prototype && make clean

help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "The available targets are:"
	@echo ""
	@gawk -vG=$$(tput setaf 2) -vR=$$(tput sgr0) ' \
	  match($$0, "^(([^#:]*[^ :]) *:)?([^#]*)##([^#].+|)$$",a) { \
	    if (a[2] != "") { printf "    make %s%-18s%s %s\n", G, a[2], R, a[4]; next }\
	    if (a[3] == "") { print a[4]; next }\
	    printf "\n%-36s %s\n","",a[4]\
	}' $(MAKEFILE_LIST)
