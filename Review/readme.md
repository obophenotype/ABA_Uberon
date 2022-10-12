# Reviewing Bridge Files

## Content 

1. mba_CCF_to_UBERON.tsv -> template for bridge
2. terms_in_json_not_bridge.txt -> terms that are not in bridge and what uberon term they map to

## Instructions

### TSV

The tsv file has all the explicit mappings in it. 
It is split into 3 different type of mappings (see header)
1. Subclass part of -> the mba term will be mapped as "part of" of the uberon term
2. Equivalent -> the mba term will be mapped as a 1:1 equivalent of the uberon term
3. Multi-structure equivalence -> the mba term will be mapped as equialent to the term in column E and part of some term in column F

In the status column, there are two statuses:
1. Verified
2. Curated 

Verified terms can be skipped in checking - these come directly from terms mapped/verified in previous rounds
Curated terms need to be verified. To verify, please change curated to Verified, and add your ORCID in the Approved by column. 

### Terms not in Bridge (TXT)

The terms_in_json_not_bridge.txt file contains terms that are not explicitly mapped.
Two options here: 
1. Just go through the list and make sure it is ok (they tend to be broader)
2. Map them explicitly in TSV file (this would probably require a whole lot of term creation too)

### Need to discuss

We should have a workflow of terms that need term creation and mapping them during the review process. TBD. 