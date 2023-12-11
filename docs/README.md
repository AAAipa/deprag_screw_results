# Documenting deprag_screw_results

## Changelog generation

### Requirements

```shell
pip install git-changelog
```

### Generating the changelog

```shell
cd PATH/TO/deprag_screw_results
git-changelog -o CHANGELOG.md -s conventional -t path:docs/changelog_templates .
```
