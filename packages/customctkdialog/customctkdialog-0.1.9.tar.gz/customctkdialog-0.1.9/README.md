# 🎉 **CustomCTkDialog**

### *Beautiful dialogs, alerts, and native file pickers for CustomTkinter — powered by a lightweight Electron executable.*

<p align="center">
  <img src="https://img.shields.io/badge/python-3.11%2B-blue?style=for-the-badge" />
  <img src="https://img.shields.io/badge/customtkinter-5.2%2B-green?style=for-the-badge" />
  <img src="https://img.shields.io/badge/platform-windows-lightgray?style=for-the-badge" />
</p>

## ✨ Features

✔️ **Modern dialogs** that blend perfectly with CustomTkinter
✔️ **Custom alert boxes** with multiple alert types
✔️ **Native-feeling folder picker** powered by a lightweight Electron executable
✔️ Plug-and-play — no configuration required
✔️ Clean, Pythonic API
✔️ Automatic runtime download — no large `.exe` included in the package

## 🚀 Installation

```
pip install customctkdialog
```

## 📦 Project Structure

```
CustomCTkDialog/
│
├── CustomCTkDialog/              # Python package
│   ├── __init__.py
│   ├── electron_loader.py        # Downloads Electron runtime on import
│   ├── dialog_main.py            # Main dialog system
│
├── js-folder-picker/             # JS workspace (developers only)
│   ├── folder-picker.js
│   ├── package.json
│   └── build scripts
│
├── example/
│   └── app.py                    # Example usage
│
├── images/                       # UI preview images
│   ├── prompt.png
│   ├── confirm.png
│   └── alert.png
│
├── README.md
└── pyproject.toml
```

📝 **Note:**
The `js-folder-picker/` folder is **not included** in the published Python package.

## 🔄 Runtime Logic with `electron_loader`

Previously, the Python package included a **large bundled `.exe`**, which made installation heavy and slow.

`CustomCTkDialog` now uses a **dynamic runtime loader**:

1. On package import, `electron_loader.ensure_electron()` runs automatically.
2. It checks whether the **Electron folder picker runtime** is already present.
3. If missing, the user is prompted:

```
Some necessary files are required for CustomCTkDialog.folder_picker to work.
Download these files now? (Y/n):
```

4. If the user agrees, the ZIP is downloaded from **GitHub Releases**.
5. The ZIP is extracted into the package directory.
6. Future imports detect the runtime and do **not** download again.

### ✔️ Benefits

* Very lightweight PyPI package
* Automatic runtime management
* Easy to release updates via GitHub

## 🧪 Example Usage

Here are the UI components included in the package:

![confirm](images/Confirm.png)
![alert](images/Alert.png)
![prompt](images/Prompt.png)

```python
from CustomCTkDialog import Dialog, folder_picker, file_picker, AlertType

# Prompt input
try:
    name = Dialog.prompt("Enter your name:", default_text="Alice")
    print("Prompt returned:", name)
except ValueError as error:
    print("Prompt canceled:", error)

# Confirm dialog
confirmed = Dialog.confirm("Do you want to continue?")
print("Confirm returned:", confirmed)

# Alert
Dialog.alert(AlertType.SUCCESS, "Test Alert", "This is a success alert!")

# File picker
files = file_picker(initialdir="D:/")
print("Selected files:", files)

# Folder picker (Electron runtime downloads automatically on first run)
directories = folder_picker(initialdir="D:/")
print("Selected folders:", directories)
```

## 🧰 API Reference

### `Dialog` class

| Method      | Description                                                   |
| ----------- | ------------------------------------------------------------- |
| `prompt()`  | Shows an input dialog, returns string or raises `ValueError`. |
| `confirm()` | Shows a yes/no dialog, returns boolean.                       |
| `alert()`   | Shows an alert with the specified `AlertType`.                |

### `folder_picker()`

```python
paths = folder_picker()
```

### `file_picker()`

```python
files = file_picker()
```

## 🛠 Development

### Install dependencies

```
pip install -r requirements.txt
```

### Run example

```
python example/app.py
```

### Rebuild JS folder picker

```
cd js-folder-picker
npm install
npm run build
```

Upload the resulting ZIP to **GitHub Releases**.

## 📦 Build & Publish (maintainers only)

### Build

```
python -m build --no-isolation
```

### Upload to TestPyPI

```
python -m twine upload --verbose --repository testpypi dist/*
```

## 🔒 TestPyPI & PyPI Upload Permissions

To protect users and maintain high-quality releases, upload permissions for both **TestPyPI** and **PyPI** are limited to the **project owner** and approved **maintainers**.

This ensures:

* Secure, trusted releases
* Proper version control
* A consistent publishing workflow

### Want to become a maintainer?

1. Open an issue on GitHub expressing your interest.
2. Contact the project owner.
3. Once approved, your account will be added under **Settings → Collaborators**, enabling you to publish updates.

Your contributions are valued — thank you for helping improve the project!

## 🤝 Contributing

* Pull requests welcome!
* JS improvements must be rebuilt before packaging.
* Release updates through GitHub to support the runtime downloader.

## 📝 License

### **Creative Commons Attribution–NonCommercial 4.0 (CC BY-NC 4.0)**
