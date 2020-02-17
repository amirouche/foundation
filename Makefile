FILENAME=copernic-awesome-data-store

all: README.md
	cp README.md $(FILENAME).md
	pandoc README.md -o $(FILENAME).pdf
	pandoc README.md -o $(FILENAME).html
