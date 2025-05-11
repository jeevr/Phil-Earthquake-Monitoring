# 🚀 Philippine Earthquake Monitoring

This project aims to have a monitoring tool using **Power BI** to visualize the old and recent earthquakes in the Philippines.

---
## ✨ Tech Stack (Services) used to Build this Tool

- Azure Storage (Raw Data Storage)
- Azure Virtual Machine (web Scraper)
- Azure Data Factory (Ingestion)
- Azure SQL Database (Structured Data Storage)
- Azure Databrics (Data Transformation)
- Azure Synapse Analytics (Analystics Data)
- Power BI (Visualization)

![alt text](documents/project_model.png)

---



## 📂 Folder Structure
<pre><code>
Repository
├── main.py
├── Database Script
│   └── database
│   │       ├── __init__.py
│   │       ├── db_manager.py
│   │       └── queries.py
│   └── utils
│       ├── __init__.py
│       └── populate_table_widgets.py
├── Web Scraper
│   ├── main.py          ← global styles
│   ├── requirements.txt      ← optional page override
│   ├── 
│   └── page_two.qss
├── requirements.txt
└── README.md

- app_functions
    - database
    - utils
</code></pre>

- config
- styles


---

## Web Scraper


--- 

## Azure Data Pipeline


---

## 🔧 Clone Repository

### 1. Virtual Environment
> **Command Prompt** 

- **Create:** ``python -m venv venv_AppOne``
- **Activate:** ``venv_AppOne\Scripts\activate``
- **Deactivate:** ``deactivate``
- **Freezing App Dependencies (Libraries):** ``pip freeze > requirements.txt ``
- **Installing Libraries from Requirements.txt:** ``pip install -r requirements.txt``

### 2a. Accessing QS Designer
> **QS Designer** is part of the Library **PySide6** and automatically downloaded during pip install.

To find the **QS Designer**, navigate to this directory:
```C:\Users\Lenovo\AppData\Local\Programs\Python\Python311\Lib\site-packages\PySide6``` and file the green app **Designer.exe**

You can create a shortcut for ease of access next time.


### 2b. Generating .py files  from QS Designer
- **Run:** ``pyside6-uic <qs designer file>.ui -o ui/<output file>.py``
- **Sample:** ``pyside6-uic page_one.ui -o ui/page_one_ui.py``

### 2c. Generating .py files for Images/Icons needed for QSS
- **Make a file named:** ``resources.qrc``
- **Edit in Text Editor/notepad:** 
    ```bash
    <RCC>
        <qresource prefix="/">
            <file>icons/arrow_down.png</file>
            <file>styles/style.qss</file>
        </qresource>
    </RCC>
    ```
- **The `<file>` paths are relative to the .qrc file location**
- **The `<prefix>` sets the virtual folder (often /)**
- **Use the pyside6-rcc or pyrcc6 tool to convert it to Python:** ``pyside6-rcc resources.qrc -o resources_rc.py``
- **This generates a resources_rc.py file that you import in your Python code.**
- **Import the compiled file:** `import resources_rc`

### 3. Executing the App (via Editor)
> **VSCode**
- **Run:** ``python main.py``
