### This makefile requires python3 & pip3 mapped as such

JOBS = 1 17 10 16 8
TARGETS = mba dmba

ROBOT = robot
LINKML = linkml-data2owl

URIBASE = http://purl.obolibrary.org/obo

STRUCTURE_GRAPHS = $(patsubst %, sources/%.json, $(JOBS))
ALL_GRAPH_ONTOLOGIES = $(patsubst sources/%.json,sources/%.ofn,$(STRUCTURE_GRAPHS))
SOURCE_TEMPLATES = $(patsubst %, ../robot_templates/%_CCF_to_UBERON_source.tsv, $(TARGETS))
NEW_BRIDGES = $(patsubst %, new-bridges/new-uberon-bridge-to-%.owl, $(TARGETS))


all: dependencies $(ALL_GRAPH_ONTOLOGIES) aba_uberon.owl report.xlsx $(NEW_BRIDGES)

# Installing depedencies so it can run in ODK container
.PHONY: dependencies
dependencies:
	pip3 install -r ../../requirements.txt

IMP=true # Global parameter to bypass import generation
MIR=true # Global parameter to bypass mirror generation

#  Pulling full Uberon for now and using
mirror/uberon.owl:
	@if [ $(MIR) = true ] && [ $(IMP) = true ]; then $(ROBOT) convert -I $(URIBASE)/uberon.owl -o $@.tmp.owl && mv $@.tmp.owl $@; fi

# TODO: move to making uberon slice.

sources/%.json:
	curl -o $@ $(subst %,$(subst sources/,,$@),"http://api.brain-map.org/api/v2/structure_graph_download/%")

../linkml/data/template_%.tsv: sources/%.json
	python3 ../scripts/structure_graph_template.py -i $< -o $@

sources/%.ofn: ../linkml/data/template_%.tsv
	$(LINKML) -C Class -s ../linkml/structure_graph_schema.yaml $< -o $@
.PRECIOUS: sources/%.ofn

# download bridges

sources/uberon-bridge-to-aba.obo:
	curl -o sources/uberon-bridge-to-aba.obo "https://raw.githubusercontent.com/obophenotype/uberon/master/src/ontology/bridge/uberon-bridge-to-aba.obo"

sources/uberon-bridge-to-dhba.obo: 
	curl -o sources/uberon-bridge-to-dhba.obo "https://raw.githubusercontent.com/obophenotype/uberon/master/src/ontology/bridge/uberon-bridge-to-dhba.obo"

sources/uberon-bridge-to-dmba.obo:
	curl -o sources/uberon-bridge-to-dmba.obo "https://raw.githubusercontent.com/obophenotype/uberon/master/src/ontology/bridge/uberon-bridge-to-dmba.obo"

sources/uberon-bridge-to-hba.obo:
	curl -o sources/uberon-bridge-to-hba.obo "https://raw.githubusercontent.com/obophenotype/uberon/master/src/ontology/bridge/uberon-bridge-to-hba.obo"

sources/uberon-bridge-to-mba.obo:
	curl -o sources/uberon-bridge-to-mba.obo "https://raw.githubusercontent.com/obophenotype/uberon/master/src/ontology/bridge/uberon-bridge-to-mba.obo"

sources/uberon-bridge-to-pba.obo:
	curl -o sources/uberon-bridge-to-pba.obo "https://raw.githubusercontent.com/obophenotype/uberon/master/src/ontology/bridge/uberon-bridge-to-pba.obo"

all_bridges:
	make sources/uberon-bridge-to-aba.obo sources/uberon-bridge-to-dhba.obo sources/uberon-bridge-to-dmba.obo sources/uberon-bridge-to-hba.obo sources/uberon-bridge-to-mba.obo sources/uberon-bridge-to-pba.obo -B

# Make new bridges
# Not sure if the robot commands can be squashed down - happy for you to rewrite neater hkir
# Still need to integrate makefile from src/bridge - will leave that to you hkir 

%_old_mapping.tsv: sources/legacy/uberon-bridge-to-%.obo
	$(ROBOT) query --input $< --query ../sparql/bridge_mappings.sparql $@

../robot_templates/%_CCF_to_UBERON_source.tsv: %_old_mapping.tsv  ../robot_templates/%_CCF_to_UBERON.tsv
	python ../scripts/mapping_source_template_generator.py -i1 $< -i2 $(word 2, $^) -o $@

new-bridges/new-uberon-bridge-to-%.owl: ../robot_templates/%_CCF_to_UBERON.tsv ../robot_templates/%_CCF_to_UBERON_source.tsv
	$(ROBOT) template --input mirror/uberon.owl --template $< --output tmp/sourceless-new-uberon-bridge.owl
	$(ROBOT) template --input mirror/uberon.owl --template $(word 2, $^) --output tmp/CCF_to_UBERON_source.owl
	$(ROBOT) merge --input tmp/sourceless-new-uberon-bridge.owl --output tmp/CCF_to_UBERON_source.owl --output $@

new_bridges: $(NEW_BRIDGES)

# Merge sources. # crudely listing dependencies for now - but could switch to using pattern expansion
sources_merged.owl: all_bridges
	robot merge --input sources/1.ofn --input sources/17.ofn --input sources/10.ofn --input sources/16.ofn --input sources/8.ofn --input sources/uberon-bridge-to-aba.obo --input sources/uberon-bridge-to-dhba.obo --input sources/uberon-bridge-to-dmba.obo --input sources/uberon-bridge-to-hba.obo --input sources/uberon-bridge-to-mba.obo --input sources/uberon-bridge-to-pba.obo annotate --ontology-iri $(URIBASE)/$@ -o $@


# Generate seed for pulling relevant subset of Uberon
terms.txt: sources_merged.owl
	$(ROBOT) query --use-graphs true -f csv -i $< --query ../sparql/terms.sparql $@

# Generate slice of uberon, removing disjoints
# Using BOT for now - but this could potentially be more minimal

uberon_slice.owl: mirror/uberon.owl terms.txt
	$(ROBOT) extract --method BOT --input mirror/uberon.owl --term-file terms.txt --force true remove --axioms disjoint --output $@


# merge uberon + sources, reason & relax (EC -> SC)

tmp.owl: uberon_slice.owl sources_merged.owl
	robot merge --input uberon_slice.owl --input sources_merged.owl relax annotate --ontology-iri $(URIBASE)/$@ -o $@

# Make a json file for use in geneating ROBOT template
tmp.json: tmp.owl
	$(ROBOT) convert --input tmp.owl -f json -o tmp.json

# Build robot  template - with linkouts and prefLabels

../robot_templates/linkouts.tsv: tmp.json
	python3 ../scripts/gen_linkout_template.py $<

# generate OWL from template

linkouts.owl: tmp.owl ../robot_templates/linkouts.tsv
	robot template --template ../robot_templates/linkouts.tsv --input $< --prefix=OboInOwl:http://www.geneontology.org/formats/oboInOwl# -o $@

# Generate release file by  merging in OWL from template
aba_uberon.owl: linkouts.owl
	robot merge --input $< --input tmp.owl annotate --ontology-iri $(URIBASE)/$@ convert -f ofn -o $@

report.tsv: aba_uberon.owl
	robot query -i $< -f tsv -q ../sparql/aba_mapping_report.sparql $@

report.xlsx: report.tsv
	python3 ../scripts/mapping_spreadsheet_gen.py $< $@

# Compress for release to get below GitHub file size restrictions.
# aba-uberon.owl.gz: aba_uberon.owl
#	gzip $<

prepare_release: aba_uberon.owl
	cp $< ../../.






