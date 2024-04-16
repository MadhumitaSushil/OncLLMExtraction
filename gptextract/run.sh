# qsub -q "gpu.q" -pe smp 1 -l h_rt=336:00:00 -cwd -j yes -o logs/run.log run.sh

export PATH=$PATH:~/anaconda3/bin
export PATH=$PATH:~/usr/lib64
source ~/anaconda3/etc/profile.d/conda.sh
conda activate gptextract
export PYTHONPATH=~/GptExtract/:$PYTHONPATH

coral_dir='../coral/annotated/'
model_name_or_path='/wynton/group/ichs/shared_models/flan-ul2/'
python3 run_pn_benchmarking.py -annotations_path $coral_dir -model $model_name_or_path --evaluate

