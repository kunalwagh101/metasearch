# 📁 MetaSearch

MetaSearch is a powerful file metadata search and annotation engine. It enables blazing-fast file indexing, querying, and metadata enrichment — all from Python 🐍.

Whether you're managing documents, auditing file systems, or just need a better way to find "that one file", MetaSearch helps you search smarter, not harder.

---

## 🚀 Installation (TestPyPI)

To install MetaSearch from **TestPyPI**, use the following command:

```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple agasearch
```

or use 

```bash
pip install --extra-index-url https://test.pypi.org/simple/ agasearch
```
> ⚠️ The `--no-deps` flag is used to skip dependency resolution from TestPyPI. Install dependencies separately if needed.

---

## 🧠 Features

✅ Smart and lazy file indexing  
✅ Full-text search with plugins  
✅ Annotate files with custom metadata  
✅ Search using powerful Lucene-like queries  
✅ Filter by size, timestamps, author, company, and more  
✅ Support for various file formats: PDF, DOCX, TXT, MP3, MP4, PPTX, XLSX  
✅ File creation/modification time range search  
✅ Easy-to-extend architecture with plugin support

---

## 📦 Usage

### 1. Basic Setup

```python
import metasearch

config = metasearch.Config(
    scan_paths=["H:\\trail", "H:\\exam", "H:\\job"]
)

engine = metasearch.Engine(config)
```
advance config options:

```python
 config = metasearch.Config(
        scan_paths=["H:\\trail"],
        enable_watchdog=False,   # Change to True to enable real-time monitoring if desired.
        db_path="metasearch.db",
        lazy_indexing=True
    )

```
### 2. Searching Files

#### 🔍 Search by file metadata

```python
engine.search('author:"Kunal Wagh"')
engine.search('producer:"Microsoft: Print To PDF"')
```

#### 🔎 Search by file name

```python
engine.search("file_name:Approach")
```

#### 🔧 Annotate and then search

```python
engine.annotate("H:\\trail\\extrail.txt", {
    "company": "abc",
    "description": "Example annotation for testing"
})

engine.search('company:"abc"')
```

---

## 📂 Extra Functions & Utilities

### ✅ `annotate(file_path, metadata_dict)`
Adds custom metadata to a file.

```python
engine.annotate("file.txt", {"team": "AI", "priority": "high"})
```

---

### ❌ `remove_file(file_path)`
Removes the file from the index.

```python
engine.remove_file("file.txt")
```

---

### 🔍 `search_first_match(query)`
Returns the first matching file.

```python
result = engine.search_first_match('company:"abc"')
```

---

### 📑 `get_metadata(file_path)`
Returns metadata for a specific file.

```python
meta = engine.get_metadata("file.txt")
print(meta)
```

---

### 📏 `search_by_size(min_bytes, max_bytes)`
Find files within a size range.

```python
results = engine.search_by_size(0, 2 * 1024 * 1024)  # Files < 2MB
```

### 📏 `search_by_time(type, seconds)`
Find files within a size range.

```python
    results = engine.search_by_time("modified", 3600)  # Files < 2MB
```


---

## 🧪 Full Example

Create a file `example_app.py` with this content to test the library:

```python
import os
import datetime
from pathlib import Path
import metasearch

def main():
    config = metasearch.Config(
        scan_paths=["H:\\trail", "H:\\exam", "H:\\job"]
    )
    engine = metasearch.Engine(config)

    # Basic Search
    result = engine.search_first_match('producer:"Microsoft: Print To PDF"')
    print("Found:", result if result else "No match found.")

    # Annotate
    sample_file = os.path.join("H:\\trail", "extrail.txt")
    engine.annotate(sample_file, {
        "company": "abc",
        "description": "Example annotation added for testing."
    })

    # Search annotated files
    result = engine.search('company:"abc"')
    for r in result:
        print("Company Tag Match:", r)

    # Check metadata
    meta = engine.get_metadata(sample_file)
    print("Metadata:", meta)

    # Recent modification/creation time
    now = datetime.datetime.now()
    five_hours_ago = now - datetime.timedelta(hours=5)
    
    mod_results = engine.search(f"modified:[{five_hours_ago.isoformat()} TO {now.isoformat()}]")
    print("Recently Modified:", mod_results)

    create_results = engine.search(f"created:[{five_hours_ago.isoformat()} TO {now.isoformat()}]")
    print("Recently Created:", create_results)

    # File size search
    five_mb = 5 * 1048576
    big_files = engine.search(f"size_bytes:[{five_mb + 1} TO ]")
    print("Files > 5MB:", big_files)

    small_files = engine.search(f"size_bytes:[0 TO {five_mb}]")
    for r in small_files:
        print("File < 5MB:", r)

    # Range search via helper
    two_mb = 2 * 1024 * 1024
    size_results = engine.search_by_size(0, two_mb)
    for r in size_results:
        print("File < 2MB:", r)

    results = engine.search_by_time("modified", 3600)
    
    if results:
        for file_meta in results:
            print("Modified files found:", file_meta)
    else:
        print("No files found in the given time range.")

    # Remove from index
    engine.remove_file(sample_file)
    engine.shutdown()

if __name__ == "__main__":
    main()
```

---

## 🧩 Plugins

Want full-text search support for `.txt`, `.docx`, or `.pdf`?

### Add a file to text index:

```python
from metasearch.plugins.text_search import add_file_to_text_index

meta = engine.get_metadata("file.txt")
add_file_to_text_index(meta)
```

---

## 🛠 Supported File Types

- `.txt`, `.docx`, `.pdf`
- `.xlsx`, `.pptx`
- `.mp3`, `.mp4`
- `.jpg`, `.png`
- `.csv`, `.json`

---

## 💡 Pro Tips

- Use `Engine.shutdown()` to gracefully close resources.
- Use Lucene syntax for more powerful searches.
- Use annotations to enrich search with custom tags like `department`, `priority`, etc.

---







