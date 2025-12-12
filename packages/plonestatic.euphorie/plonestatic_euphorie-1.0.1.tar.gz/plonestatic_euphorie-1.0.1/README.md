# Static resources for the Euphorie project

This repository contains static resources for the [Euphorie](https://github.com/euphorie/Euphorie) project.

## Updating the package

In order to properly update the package, you will need some development tools to be installed, i.e:

- `git`
- `make`
- `rsync`
- `Ruby`

Optionally, you can install [`gitman`](https://gitman.readthedocs.io/en/latest/) to manage the checkouts.

Updating the site is a three-step process.

1. you need to fetch a fresh clone of the Euphorie prototype.
2. you need to compile the resources.
3. you need to install the resources in the Euphorie package.

This can be done by running the following command:

```bash
make all
```

Run:

```bash
make help
```

to see all available commands and fine tune the build experience.

### Fetching a fresh clone of the Euphorie prototype

To update the repository, run the command:

```bash
make update-proto
```

The clone will be placed in the `var/prototype` directory.

Running `make all` will take care of running this command for you.

### Compiling the resources

The resources are compiled using the static site generator `Jekyll`. The compiled site can be found in the `var/prototype/_site` directory.

To compile the resources, run the command:

```bash
make jekyll
```

This command will also clone (but not update) the Euphorie prototype if it is not already present.

Running `make all` will take care of running this command for you.

### Installing the resources in the Euphorie package

The compiled prototype in `var/prototype/_site` needs to be copied in this package. Only selected resources will be copied and they will end up in the `src/plonestatic/euphorie/resources` directory.

The `resources` directory will be served by `Plone` as a static resource folder under the path `++resource++euphorie.resource`.

While doing the copy, some references to the other resources in CSS and HTML files have to be rewritten to adjust to the new location, e.g. `/assets/...` will be rewritten to `/++resource++euphorie.resource/assets/...`.

The command to install the resources is:

```bash
make resources-install
```

Running `make all` will take care of running this command for you.
