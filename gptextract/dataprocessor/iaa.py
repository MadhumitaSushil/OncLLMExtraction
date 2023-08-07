import bratiaa as biaa

coll_dir = '../../data/Onco-ProgressNotes/IAA/'

f1_agreement = biaa.compute_f1_agreement(coll_dir)

# print agreement report to stdout
biaa.iaa_report(f1_agreement)
