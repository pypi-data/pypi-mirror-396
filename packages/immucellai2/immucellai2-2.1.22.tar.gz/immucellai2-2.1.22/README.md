# ImmuCellAI2.0

ImmuCellAI2.0
ImmuCellAI2 is a novel computational framework to accurately infer the abundance of 9 major and 53 minor types of immune cells from bulk RNA-seq.

ImmuCellAI Portal Website
The ImmuCellAI Portal serves as a comprehensive companion platform for ImmuCellAI2. Furthermore, the ImmuCellAI Portal offers an intuitive online service for ImmuCellAI2, allowing users to perform immune cell infiltration analysis without local installation. To access this online service, simply click here (https://guolab.wchscu.cn/ImmuCellAI2/#/).

PyPI Page
ImmuCellAI 2.0 homepage on PyPI: https://pypi.org/project/immucellai2/

Install ImmuCellAI2

```bash
pip install immucellai2

Usage
ImmuCellAI 2.0 expects a TPM matrix as input and can be implemented with only two lines of code in Python.

Basic Usage Code
import immucellai2
reference_data = immucellai2.load_tumor_reference_data()

result = immucellai2.run_ImmuCellAI2(
    reference_file=reference_data,
    sample_file=<file_path>,    #  User-defined
    output_file=<file_path>,    #  User-defined
    thread_num=8
)

Citation
If you use ImmuCellAI2 in your research, please cite the following publication:
