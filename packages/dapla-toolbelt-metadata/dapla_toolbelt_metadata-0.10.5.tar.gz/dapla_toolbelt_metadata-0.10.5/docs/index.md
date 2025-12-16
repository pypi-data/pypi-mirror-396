<!--
Use the following command to regenerate .rst files. This is necessary when adding
new files or modules or restructuring the project.

uv run sphinx-apidoc -T -f -t ./docs/templates -o ./docs ./src
-->

```{include} ../README.md
---
end-before: <!-- github-only -->
---
```

[license]: license
[contributor guide]: contributing
[API reference]: dapla_metadata
[vardef client]: ../src/dapla_metadata/variable_definitions/generated/README.md

```{toctree}
---
hidden:
maxdepth: 1
---

dapla_metadata
contributing
Code of Conduct <codeofconduct>
License <license>
Changelog <https://github.com/statisticsnorway/dapla-toolbelt-metadata/releases>
```
