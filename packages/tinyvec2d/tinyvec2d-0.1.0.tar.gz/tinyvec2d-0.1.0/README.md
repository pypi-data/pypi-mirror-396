# tinyvec2d

Tiny 2D vector helpers for Python.

No NumPy.
No classes.
Just tuples and `math`.

---

## Why does this exist?

Because sometimes you just want to do simple 2D vector math without:

- installing NumPy
- dealing with arrays
- using classes or operator overloading
- pulling heavy dependencies

This is especially useful in constrained environments (for example, mobile Python like Pydroid3) or small scripts where NumPy is overkill.

This is a hobby project, made for convenience, not for performance or completeness.

---

## What is a vector?

A vector is simply a tuple:

(x, y)

Example:

v = (3.0, 4.0)

All functions:
- take tuples as input
- return new tuples
- never mutate data

---

## Features

- 2D vectors only
- pure Python
- depends only on the standard `math` module
- explicit, functional API
- predictable behavior

Included operations:
- vector addition and subtraction
- scalar multiplication and division
- dot product
- length and distance
- normalization

---

## Example usage

```PY
from tinyvec2d import add, length, normalize, scalar_mul

v = (3, 4)
w = (1, 2)

add(v, w)          # (4, 6)
length(v)          # 5.0
normalize(v)       # (0.6, 0.8)
scalar_mul(v, 2)   # (6, 8)
```

---

## Design choices

- No classes  
  Vectors are plain tuples. This keeps things simple and transparent.

- No operator overloading  
  Functions like add(v, w) are explicit and easy to read.

- No NumPy  
  This is not meant to replace NumPy. It exists for cases where NumPy is inconvenient or unavailable.

- Fail fast  
  Invalid inputs raise errors instead of trying to guess what you meant.

---

## What this is NOT

- A full linear algebra library
- A physics engine
- A performance-oriented solution
- A NumPy replacement

If you need high performance, broadcasting, or large arrays, use NumPy.

---

## Stability

The API is small and may change.
This project prioritizes simplicity over long-term backward compatibility.

---

## License

MIT License