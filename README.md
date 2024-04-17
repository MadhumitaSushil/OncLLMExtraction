# CORAL

This repository contains the code and guidelines for replicating the annotations and analysis in the manuscript 
[CORAL: Expert-Curated Oncology Reports to Advance Language Model Inference](https://ai.nejm.org/doi/full/10.1056/AIdbp2300110).
If you are mainly interested in benchmarking newer open source models on this dataset, please use code in [this](https://github.com/MadhumitaSushil/coral) repository instead.

Dataset of 20 breast cancer and 20 pancreatic cancer progress notes were annotated comprehensively by medical experts to encode information of clinical interest from clinical notes. The annotations encompassed 9028 entities, 9986 modifiers, and 5312 relationships. This dataset was further used to benchmark zero-shot, oncology-specific relational information extraction capability of closed and open source LLMs. The dataset can be downloaded [here](https://physionet.org/content/curated-oncology-reports/1.0/) for non-commercial research purposes. Please note that if the dataset is being used to evaluate any proprietary models for example OpenAI models or Google models, it needs to be done within a secure, HIPAA-compliant framework such that no data is ever permanently transferred to or monitored by the underlying company. Azure OpenAI studio with all data transfer, monitoring, and filtering turned off may be a compatible solution.

If you use the dataset or any parts of this code for your research, please cite the corresponding paper, the dataset, and PhysioNet as the following:

CORAL paper and code bibtex citation:
```
@article{doi:10.1056/AIdbp2300110,
author = {Madhumita Sushil  and Vanessa E. Kennedy  and Divneet Mandair  and Brenda Y. Miao  and Travis Zack  and Atul J. Butte },
title = {CORAL: Expert-Curated Oncology Reports to Advance Language Model Inference},
journal = {NEJM AI},
volume = {0},
number = {0},
pages = {AIdbp2300110},
year = {},
doi = {10.1056/AIdbp2300110},

URL = {https://ai.nejm.org/doi/abs/10.1056/AIdbp2300110},
eprint = {https://ai.nejm.org/doi/pdf/10.1056/AIdbp2300110}
,
    abstract = { We curated and assessed a comprehensive dataset of breast and pancreatic cancer oncology progress notes for benchmarking oncology information extraction abilities of large language models. This new dataset has been made available to further advance large language models research in oncology. }
}

```

Dataset citation:

```
Sushil, M., Kennedy, V., Mandair, D., Miao, B., Zack, T., & Butte, A. (2024). CORAL: expert-Curated medical Oncology Reports to Advance Language model inference (version 1.0). PhysioNet. https://doi.org/10.13026/v69y-xa45.
```

PhysioNet citation:

```
Goldberger, A., Amaral, L., Glass, L., Hausdorff, J., Ivanov, P. C., Mark, R., ... & Stanley, H. E. (2000). PhysioBank, PhysioToolkit, and PhysioNet: Components of a new research resource for complex physiologic signals. Circulation [Online]. 101 (23), pp. e215–e220.
```

### LICENSE
The code and annotation schema is shared under Creative Commons Attribution-NonCommercial-ShareAlike (CC BY-NC-SA)
Further details can be found on [this](https://creativecommons.org/licenses/by-nc-sa/4.0/) page. 
Additionally, the dataset derived from this schema is shared under the PhysioNet Credentialed Health Data License 1.5.0, which is intended to be used only within non-commercial, sharealike setups similar to the CC BY-NC-SA license.

