#  **UPDATED — With Improved Future Roadmap**

# BotoEase

BotoEase is a smart, lightweight file storage library for Python that gives you a **unified API** for working with both **Local Storage** and **AWS S3**.  
It removes the complexity of `boto3` and lets developers upload, delete, sync, and generate URLs in a clean and simple way.

Perfect for backend developers working with FastAPI, Flask, Django, or CLI tools.

---

## 🚀 Features

- Upload files to **Local Storage** with one line  
- Upload files to **AWS S3** without writing boto3 logic  
- Delete files (local & S3)  
- Generate S3 pre-signed URLs  
- Auto-create local upload directories  
- Clean unified API for both storage types  

---

## 📦 Installation

```bash
pip install botoease
````

---

## 🔧 Usage

```python
from botoease import Storage
```

### 🗂️ 1. Local Storage (Default)

```python
storage = Storage(backend="local", folder="my_uploads")
storage.upload("example.png")
```

### ☁️ 2. AWS S3 Storage

```python
storage = Storage(
    backend="s3",
    bucket="my-bucket-name",
    region="us-east-1",
    access_key="YOUR_AWS_ACCESS_KEY",
    secret_key="YOUR_AWS_SECRET_KEY"
)

storage.upload("image.jpg")
```

### 🔗 Generate a URL

```python
storage.generate_url("image.jpg")
```

### 🧹 Delete a File

```python
storage.delete("example.png")
```

---

## 🔒 Security Notes

* Use environment variables for AWS credentials
* Never commit secrets to GitHub

---

# 📈 Upcoming Features (Future Releases)

Below is the **updated roadmap** based on real developer needs and market gaps.
These additions will make BotoEase far more powerful and practical than a simple boto3 wrapper.

---

## 🟦 **v0.1.0 – Core Usability Boost**

* [ ] Automatic UUID renaming (prevent file name collisions)
* [ ] Automatic folder structure (`YYYY/MM/DD/filename`)
* [ ] File type (MIME) validation
* [ ] File size validation

---

## 🟩 **v0.2.0 – High-Demand S3 Utilities**

These are the most requested S3 helpers developers constantly rewrite.

* [ ] **Safe Uploads**
  Auto-retry logic, MD5 checksum verification, and automatic multipart uploads.
* [ ] **Local ↔ S3 Sync**
  Rsync-style folder sync (upload only changed files, delete removed files).
* [ ] **Advanced File Listing**
  List objects with filters:
  - extension
  - min/max size
  - date range
  - recursive or non-recursive
* [ ] **Improved Pre-signed URL Helpers**
  Restrict file size, content-type, and expiry.

---

## 🟧 **v0.3.0 – Backup, Compression & Secure Uploads**

* [ ] **Bucket Backup & Restore**
  Copy bucket → backup bucket, and restore on demand.
* [ ] **Optional Compression** (gzip / zip / brotli) before upload
* [ ] **Client-side Encrypted Uploads**
  AES encryption before sending the file.

---

## 🟥 **v0.4.0 – Storage Backend Plugins**

Introduce a clean storage backend architecture:

* [ ] FileSystem backend (local)
* [ ] S3 backend
* [ ] Custom backend (user supplies save/load functions)
* [ ] Ready for future Azure/GCP integration

---

## 🟪 **v0.5.0 – Erasure Coding (Advanced Feature)**

For users needing redundancy, multi-cloud durability, or distributed storage.

* [ ] Erasure Coding support (XOR or Reed–Solomon)
* [ ] Encode file → return shards
* [ ] Optional: store shards using any backend
* [ ] Pluggable backends (S3, local, DB, multi-cloud)
* [ ] Metadata generation + reconstruction helpers

> This is a **unique**, specialized feature no other boto3 wrapper provides.

---

## 🟨 **v1.0.0 – Async + Performance**

Perfect for FastAPI and modern async Python.

* [ ] Fully async API (upload, delete, sync, list)
* [ ] Background uploads
* [ ] High-performance multipart upload engine

---

## 🤝 Contributing

Pull requests and feature suggestions are welcome!

---

## 📜 License

MIT License.



