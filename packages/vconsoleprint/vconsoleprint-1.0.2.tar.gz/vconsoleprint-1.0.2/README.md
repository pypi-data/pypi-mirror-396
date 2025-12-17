# vconsoleprint

A Python package that automatically replaces the built-in `print` function with a better, colorful, developer-friendly console output — similar to `console.log` in JavaScript.

## 🚀 Features

- Automatically color-coded output by data type.
- Pretty-print lists, tuples, and nested dictionaries.
- Cleaner readability for debugging.
- No need to manually call the function — `print()` is auto-overwritten on import.

## 📦 Installation


## 🧠 Usage

Just import the package:

```python
import vconsoleprint

print("Hello", 10, 3.14, True, None)

Example Output:

Strings → green

Integers → yellow

Floats → cyan

Boolean → magenta

None → blue

Lists / Dicts → white (pretty formatted)

🛠 How it Works

When you import the package:

import vconsoleprint


It automatically overrides the built-in print with a cleaner, styled output function.

🤝 Contributing

Pull requests are welcome.
For major changes, please open an issue first.

📄 License

This project is licensed under the MIT License — see the LICENSE file.



---

# 🎯 Final Folder Structure

Make sure your project looks like this:

vconsoleprint/
init.py
printer.py
setup.py
README.md
LICENSE


---

# 🔥 Want me to generate **printer.py** and **__init__.py** again under this structure?  
Just say **"generate printer.py + init"** and I’ll provide clean versions suitable for a PyPI package.


