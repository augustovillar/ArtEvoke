# ArtEvoke Dataset Downloader

This part of the repository provides scripts to download and organize datasets used in the **ArtEvoke** platform. It supports data collection from:

- **Royal Museums of Fine Arts of Belgium**
- **SemArt**
- **WikiArt**

## 📁 Project Structure

```
.
├── Museum/
│   └── fab_dump.py
|   ... files provides by the museum 
├── SemArt/
│   ├── Images/
│   ├── semart_info/
│   └── download_and_filter.py
├── WikiArt/
│   └── download_and_filter.py
├── README.md
└── requirements.txt
```

## ⚙️ Environment Setup

1. **Navegate to the data directory:**
```bash
   cd project_assets/data
   ```

2. **Create and activate a virtual environment**:
```bash
   python -m venv data_env
   source data_env/bin/activate  # On Windows use `data_env\Scripts\activate`
```

3. **Install dependencies**:
```bash
   pip install -r requirements.txt
```

## ⬇️ Download Datasets
The datasets that are publicly avaialable have a script to handle download and filtering:

### SemArt
```bash
python SemArt/download_and_filter.py
```

### WikiArt
```bash
python WikiArt/download_and_filter.py
```

## 🧹 Cleanup (Optional)
Some scripts may include functions to clean up directories after filtering and organizing data.
