**dtbag** is a comprehensive Python library designed for efficient text processing and data cleaning. It provides robust tools for identifying and unifying similar text entries, making it ideal for preprocessing textual data in data science and machine learning pipelines.

## Core Features

### 1. **Text Similarity & Clustering**
- Advanced Levenshtein distance implementation for accurate string matching
- Automatic clustering of similar text entries based on configurable thresholds
- Group-based text unification for consistent data representation

### 2. **Data Cleaning & Normalization**
- Intelligent duplicate detection and removal
- Text unification based on frequency analysis
- Support for multilingual text processing

### 3. **Production-Ready Tools**
- Scikit-learn compatible API design
- Memory-efficient algorithms for large datasets
- Easy integration with existing data pipelines



#What's Inside:

  *CatLists
   Identifies clusters of similar text entries and returns grouped lists with their most frequent representatives.

  *CatUnifier  
   Transforms lists by replacing similar items with their most common representative, maintaining original list structure.



#Quick Start

```python
from dtbag import CatUnifier

"Clean inconsistent data entries"
data = ["Yassine", "Parrise", "Yasin", "Pris", "PParis" "Yasine", "yasyne", "Paris"]
unifier = CatUnifier()
clean_data = unifier.fit_transform(data, threshold=0.7)
*Result: ["Yassine", "Paris"]



#Installation

```bash
pip install dtbag