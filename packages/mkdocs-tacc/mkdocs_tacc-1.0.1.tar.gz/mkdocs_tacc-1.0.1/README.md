# MkDocs TACC Theme

A [TACC](https://www.tacc.utexas.edu/)-styled [MkDocs](https://www.mkdocs.org/) theme based on **MkDocs**' own [ReadTheDocs theme](https://www.mkdocs.org/user-guide/choosing-your-theme/#readthedocs).

- **Either** [Create a New MkDocs-TACC Project](#create-a-new-mkdocs-tacc-project)
- **Or** [Install Theme Into Existing MkDocs Project](#install-theme-into-existing-mkdocs-project)

## Create a New MkDocs-TACC Project

1. Create a repository from our [`mkdocs-tacc-client`](https://github.com/TACC/mkdocs-tacc-client) template. [How?][create-from-template]
2. In your new repository:
    - Rename [`mkdocs_tacc_client` directory](https://github.com/TACC/mkdocs-tacc-client/tree/main/mkdocs_tacc_client) to `your_project_name`.
    - Rename [all instances of `TACC/mkdocs-tacc-client`](https://github.com/search?q=repo%3ATACC%2Fmkdocs-tacc-client+%22TACC%2Fmkdocs-tacc-client%22&type=code) to `YourOrgOrUser/your-repo-name`.
    - In `pyproject.toml`, change:
        - the `name` to `your-project-name`
        - the `description`
        - the `homepage` URL
    - In `CONTRIBUTING.md`, change:
        - the `[issues]:` URL
        - the `[proposals]:` URL
    - In `README.md`, change the title.

## Install Theme Into Existing MkDocs Project

1. Enter the directory of your MkDocs project e.g.

    ```shell
    cd path/to/your/mkdocs/project
    ```

2. Install the theme (and optional dependencies) e.g.

    ```shell
    pip install "mkdocs-tacc[all]"
    ```

> [!NOTE]
> We also offer [detailed instructions](https://tacc.github.io/mkdocs-tacc/) instead.

## How to Use

3. In your `mkdocs.yml`:

    - Set theme name as `tacc_readthedocs`.
    - Set [typical extensions for this theme](./docs/extensions.md#typical).

## Known Clients

| Status | Repository |
| - | - |
| Active | [TACC-Docs](https://github.com/TACC/TACC-Docs)<br>[digital-porous-media/dpm_docs](https://github.com/digital-porous-media/dpm_docs) |
| Upcoming | [DesignSafe-CI/DS-User-Guide](https://github.com/DesignSafe-CI/DS-User-Guide) |
| Potential | [TACC/containers_at_tacc](https://github.com/TACC/containers_at_tacc)<br>[TACC/life_sciences_ml_at_tacc](https://github.com/TACC/life_sciences_ml_at_tacc) |

## Contributing

We welcome contributions. Read ["How to Contribute"](./CONTRIBUTING.md).

[create-from-template]: https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-repository-from-a-template#creating-a-repository-from-a-template
