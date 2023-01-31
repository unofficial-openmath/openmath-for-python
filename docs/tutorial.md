---
title: Tutorial
layout: docs
toc: true
---

<dialog id="constructionwarn" open>
<article>
<p> 🚧 Site under construction 🚧</p>
<p style="text-align:right">
<a role="button" href="#" onclick="document.getElementById('constructionwarn').close()">Ok</a>
</p>
</article>
</dialog>

## Quickstart

```python
from openmath as om
from openmath.cd import OFFICIALCDBASE

add = om.OMObject(
    om.OMApplication(
        om.OMSymbol("add", "arith1"),
        om.OMInteger(2),
        om.OMInteger(3)
    ),
    cdbase=OFFICIALCDBASE
)
```

## Simple values


## Composite values

## 
