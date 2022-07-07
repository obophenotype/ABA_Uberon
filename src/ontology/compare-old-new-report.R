# Import reports
old_report <- read.table(file = '/Users/shawntan/documents/GitHub/ABA_Uberon/src/ontology/report/old-report.tsv')
new_report <- read.table(file = '/Users/shawntan/documents/GitHub/ABA_Uberon/src/ontology/report.tsv')

# lowercase everything

new_report <- data.frame(lapply(new_report, function(v) {
  if (is.character(v)) return(tolower(v))
  else return(v)
}))

old_report <- data.frame(lapply(old_report, function(v) {
  if (is.character(v)) return(tolower(v))
  else return(v)
}))

require(dplyr)

diff_old_new <- anti_join(old_report, new_report)
diff_new_old <- anti_join(new_report, old_report)

write.table(diff_old_new, file='/Users/shawntan/documents/GitHub/ABA_Uberon/src/ontology/report/in-old-not-new.tsv', quote=FALSE, sep='\t')
write.table(diff_new_old, file='/Users/shawntan/documents/GitHub/ABA_Uberon/src/ontology/report/in-new-not-old.tsv', quote=FALSE, sep='\t')
