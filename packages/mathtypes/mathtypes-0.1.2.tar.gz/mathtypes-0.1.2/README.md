# mathtypes

A simple package that provides you math types like fraction

## Installation
```bash
pip install mathtypes
```
## Usage
### Example 1:
```python
from mathtypes import Fraction
print(Fraction(1, 2) + Fraction(1, 3))
```
Output:

```bash
5
─
6
```
### Example 2:
```python
from mathtypes import Fraction
print(Fraction(4, 4) + Fraction(4, 8))
```
Output:

```bash
16
──
8
```
## You can use _.toLowestTerm_ to convert fraction into its lowest term

### For Example

```python
from mathtypes import Fraction
a = Fraction(2,4)
a.toLowestTerm()
print(a)
```

Output:

```bash
1
─
2