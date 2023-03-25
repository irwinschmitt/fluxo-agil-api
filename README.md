# Fluxo Ágil's API

## Setup

Python 3.11 is required.

1. Create new poetry env.

   ```bash
   poetry env use python3.11 # or another 3.11 path
   ```

2. Install dependencies with poetry

   ```bash
   poetry install
   ```

3. Set up databases.
   ```bash
   docker compose up
   ```
4. Set up initial data.
   ```bash
   poetry run bash init.sh
   ```
5. Run the app.
   ```bash
   poetry run uvicorn app.main:app --reload
   ```

## Database

You can access the database diagram in this [link](https://dbdiagram.io/d/6340f3c3f0018a1c5fbdb6c5).

![Database](/images/db_model.png)

## Scraper

To recommend discipline flows, it is necessary to have information on the structure of departments, disciplines, curricula, etc.

As SIGAA does not provide an API to get the data, it is necessary to use a scraper.

The diagram below shows from which SIGAA pages data can be obtained from (you can also access the diagram through the [link](https://whimsical.com/scraper-3bBi6EMqxtq6z6HzdtGDQk@2Ux7TurymMmNus31JQQL)).

In the future, scraper should have its own repository.

![Image](/images/scraper-diagram.png)

### Components

#### How to find the department of a component?

It's not that simple to know the department of a component just by its code. For example, both components `PPG0105` and `PPG/MUS2727` are administered by the same department [`PPG/MUS`](https://sigaa.unb.br/sigaa/public/departamento/componentes.jsf?id=873). So it's not enough to store the prefix in the Department model.

One of the ways to find out which department is responsible for a component is to open the component's page and search for both the department's `title` and `acronym`.

Another way is to search for the code on the [component search page](https://sigaa.unb.br/sigaa/public/componentes/busca_componentes.jsf), but it is necessary to search at each level of education (graduation, stricto sensu, lato sensu etc).

## Future

In the future, scraper should be moved to its own repository, rewritten with Puppeteer (pyppeteer just replicates Puppeteer), to become a standalone API for multiple apps.

But, you know... first we'll make the project work, then we'll improve.
