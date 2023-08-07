import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load data from CSV
df = pd.read_csv('../../data/results.csv')

# Define the relation label groups
group1 = ['Biomarker Datetime', 'Grade Datetime', 'Histology Datetime', 'Metastasis Datetime', 'Metastasis Procedure', 'Metastasis Site', 'Stage Datetime', 'TNM Datetime']
group2 = ['Symptom Datetime', 'SymptomAtDiagnosis Datetime', 'SymptomDueToCancer Datetime']
group3 = ['RadiologyTest Datetime', 'RadiologyTest Reason', 'RadiologyTest Result', 'RadiologyTest Site']
group4 = ['ProcedureName Datetime', 'ProcedureName Reason', 'ProcedureName Result', 'ProcedureName Site']
group5 = ['GenomicTestName Datetime', 'GenomicTestName Result']
group6 = ['PrescribedMedicationName Begin', 'PrescribedMedicationName End', 'PrescribedMedicationName Continuity', 'PrescribedMedicationName PotentialAdverseEvent', 'PrescribedMedicationName ConfirmedAdverseEvent']
group7 = ['FutureMedicationName Consideration', 'FutureMedicationName PotentialAdverseEvent']

groups = [group1, group2, group3, group4, group5, group6, group7]
group_titles = ['Tumor Characteristics', 'Symptoms', 'Radiology', 'Procedure', 'Genomics',
                'Prescribed Medications', 'Future Medications']

# Set the figure size and create subplots
fig, axs = plt.subplots(nrows=len(group_titles), ncols=2, figsize=(20, 30))

# Set the seaborn style
sns.set_style('whitegrid')
sns.set(font_scale=2)

# Loop through each row and create the subplots
for i, group in enumerate(groups):
    # Subset the dataframe for the current relation label group
    group_df = df[df['Relation'].isin(group)].reset_index(drop=True)
    # Set the x-axis tick labels
    labels = group_df['Relation']
    x = range(len(labels))

    # Plot the data for each model on the current row
    axs[i][0].barh([j - 0.3 for j in x], group_df['BLEU-GPT4'], height=0.2, label='GPT4', color='#82AAE3')
    axs[i][0].barh([j - 0.1 for j in x], group_df['BLEU-GPT3.5'], height=0.2, label='GPT3.5', color='#91D8E4')
    axs[i][0].barh([j + 0.1 for j in x], group_df['BLEU-FLANUL2'], height=0.2, label='FLAN-UL2', color='#BFEAF5')

    axs[i][1].barh([j - 0.3 for j in x], group_df['ROUGE-GPT4'], height=0.2, label='GPT4', color='#ff5252')
    axs[i][1].barh([j - 0.1 for j in x], group_df['ROUGE-GPT3.5'], height=0.2, label='GPT3.5', color='#ff7b7b')
    axs[i][1].barh([j + 0.1 for j in x], group_df['ROUGE-FLANUL2'], height=0.2, label='FLAN-UL2', color='#ffbaba')

    # Set the x-axis tick labels and y-axis labels
    axs[i][0].set_yticks(x)
    axs[i][1].set_yticks(x)
    axs[i][0].set_yticklabels(labels, fontsize=16)
    axs[i][1].set_yticklabels(labels, fontsize=16)

    axs[i][0].set_xticks([0, 0.2, 0.4, 0.6, 0.8, 1])
    axs[i][1].set_xticks([0, 0.2, 0.4, 0.6, 0.8, 1])
    axs[i][0].set_xlim([0, 1])
    axs[i][1].set_xlim([0, 1])

    axs[i][0].set_xlabel('BLEU Scores', fontsize=14)
    axs[i][1].set_xlabel('ROUGE Scores', fontsize=14)

    # Set the plot titles and legends
    axs[i][0].set_title(group_titles[i], fontsize=16)
    axs[i][1].set_title(group_titles[i], fontsize=16)
    axs[i][0].legend(fontsize=12)
    axs[i][1].legend(fontsize=12)


# Adjust the spacing between subplots and save the plot
plt.subplots_adjust(hspace=0.4)
plt.tight_layout()
plt.savefig('../../output/relations_grouped.png')
