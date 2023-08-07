# qsub -q "gpu.q" -pe smp 1 -l h_rt=336:00:00 -cwd -j yes -o logs/run.log run.sh

export PATH=$PATH:~/anaconda3/bin
export PATH=$PATH:~/usr/lib64
source ~/anaconda3/etc/profile.d/conda.sh
conda activate gptextract
export PYTHONPATH=~/GptExtract/:$PYTHONPATH

CUDA_VISIBLE_DEVICES=$SGE_GPU python3 run_pn_benchmarking.py -model 'gpt-35-turbo'

CUDA_VISIBLE_DEVICES=$SGE_GPU python3 run_pn_benchmarking.py -model 'gpt-4'

CUDA_VISIBLE_DEVICES=$SGE_GPU python3 run_pn_benchmarking.py -model '/wynton/group/ichs/shared_models/flan-ul2/' --evaluate

