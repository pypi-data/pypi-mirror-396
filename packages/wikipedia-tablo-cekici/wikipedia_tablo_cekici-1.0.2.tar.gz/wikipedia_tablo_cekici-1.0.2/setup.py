from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="wikipedia-tablo-cekici",
    version="1.0.2",  # Versiyonu artırdım
    
    author="Özgür Özen",
    author_email="oozen760@gmail.com",
    
    description="Wikipedia sayfalarından tablo verilerini çeken Python kütüphanesi",
    long_description=long_description,
    long_description_content_type="text/markdown",
    
    url="https://github.com/ozgurrozennn/my_project",
    
    packages=find_packages(),
  
    
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
        "beautifulsoup4>=4.9.0",
        "pandas>=1.2.0",
        "lxml>=4.6.0",
        "openpyxl>=3.0.0",
    ],
    keywords="wikipedia table scraper data extraction tablo çekici",
)

