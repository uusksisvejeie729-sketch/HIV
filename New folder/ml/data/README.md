# Dataset Instructions

Place your Kaggle/UCI HIV dataset as `hiv_dataset.csv` in this folder.

## Required columns (after rename or via COLUMN_MAP in `data_loader.py`)

| Column | Description |
|--------|-------------|
| age | Integer |
| gender | male / female / other |
| bmi | Float |
| sti_history | 0 or 1 |
| cd4_count | Integer |
| behavioral_score | 0–5 |
| risk_class | 0=Low, 1=Medium, 2=High (or text labels) |

Train with:

```bash
python train.py --csv data/hiv_dataset.csv
```
