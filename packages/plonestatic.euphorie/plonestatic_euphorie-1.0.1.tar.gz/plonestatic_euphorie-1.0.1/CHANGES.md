# Changelog

<!--
You should *NOT* be adding new change log entries to this file.
You should create a file in the news directory instead.
For helpful instructions, please see:
https://github.com/plone/plone.releaser/blob/master/ADD-A-NEWS-ITEM.rst
-->

<!-- towncrier release notes start -->

## 1.0.1 (2025-12-09)

### Bug fixes:

- Update Prototype to fix a problem with some previews not shown in help pages.

  Note: This uses the submodule "\_includes/patterns" branch "reverse-sentinel"
  from https://github.com/Patternslib/patterns-includes/pull/3

  Ref: scrum-3430
  [thet]

### Internal:

- Fix towncrier config.


## 1.0.0 (2025-07-15)

### Bug fixes:

- Add missing example report images (used by `@@register_session`)
  Also extend the Makefile to automatically include these images when building plonestatic.euphorie. (#3709)
- Script replacement: Also support version/release-level specific subdirectories of the Patternslib script in prototype like alpha/, beta/, etc.
  [thet]


## 1.0.0a5 (2025-03-27)


- Add a missing image used by the Euphorie package

- Use gitman if it is available
  [ale-rt]

- major update of help, fixing broken links, missing images and pages, new illustration files
  [pilz]


## 1.0.0a4 (2025-02-20)


- Update to the most recent markup


## 1.0.0a3 (2025-02-04)


- Fix link to patternslib


## 1.0.0a2 (2025-02-04)


- Add missing resources


## 1.0.0a1 (2025-02-03)

- Initial release
