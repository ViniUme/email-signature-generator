# Email Signature Generator

Automatically generates employee email signatures from HTML templates and an Excel spreadsheet. Outputs HTML, PDF, or JPG files.

---

## 📁 Folder Structure

```
EmailSignatureGenerator/
├── EmailSignatureGenerator(.exe)  ← Standalone executable (after build)
├── email_signature_generator.py   ← Main script
├── build.py                       ← Builds the standalone executable
├── create_sample_excel.py         ← Creates sample Excel files for testing
│
├── templates/                     ← HTML signature templates
│   ├── modern_blue.html
│   ├── corporate_gold.html
│   └── minimal_green.html
│
├── data/                          ← Place your Excel files here (multiple supported)
│   ├── employees_technology.xlsx
│   └── employees_all.xlsx
│
└── output/                        ← Generated signatures are saved here
```

---

## 🚀 How to Run

### Option A — Standalone executable (no Python needed)
```bash
# Linux / macOS
./EmailSignatureGenerator

# Windows
EmailSignatureGenerator.exe
```

### Option B — With Python installed
```bash
pip install openpyxl Pillow
python email_signature_generator.py
```

---

## 📊 Excel File Format

The first row must be the **header row**. The program auto-detects columns with names similar to:

| Field       | Accepted column names                                   |
|-------------|---------------------------------------------------------|
| Name        | `name`, `nome`                                          |
| Position    | `position`, `title`, `role`, `cargo`, `função`          |
| Phone       | `phone`, `tel`, `telefone`, `celular`, `whatsapp`       |
| Email       | `email`, `e-mail`, `mail`                               |
| Department  | `department`, `dept`, `departamento`, `setor`, `área`   |

**Multiple Excel files are supported** — all `.xlsx` files in the `data/` folder are listed at startup so you can choose which one to use.

---

## 🎨 Creating Templates

Templates are `.html` files placed in the `templates/` folder. Use double-brace placeholders for dynamic data:

```html
<div>{{name}}</div>
<div>{{position}}</div>
<div>{{phone}}</div>
<div>{{email}}</div>
<div>{{department}}</div>
```

Any Excel column name can also be used directly as a placeholder (e.g. `{{custom_field}}`).

---

## 📦 Building the Executable

```bash
pip install pyinstaller openpyxl Pillow
python build.py

# With clean slate
python build.py --clean
```

The complete package will be at `dist/EmailSignatureGenerator_package/`. Zip and distribute — nothing else needs to be installed.

---

## 📄 Output Formats

| Format | Notes |
|--------|-------|
| **HTML** | Ready to paste into email clients |
| **PDF**  | Install `weasyprint` or `reportlab` for best results |
| **JPG**  | Install `html2image` for accurate rendering; built-in fallback always available |

---

## 💡 Tips

- Add multiple `.xlsx` files to `data/` — the program always asks which one to use
- The generator supports selecting **all**, a **range**, or a **single** employee per run
