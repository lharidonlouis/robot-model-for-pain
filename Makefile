

.PHONY: all doc clean depend transfer

model: 

doc:
	doxygen doc
	clear

all: 	doc model

clean : 
	@echo "Cleaning"
	@rm -r html
	@rm -r latex

