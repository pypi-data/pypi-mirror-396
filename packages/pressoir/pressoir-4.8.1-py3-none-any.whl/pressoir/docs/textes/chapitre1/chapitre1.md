
::: {.introchapitre}
Installer le gestionnaire de paquets UV afin de créer avec le Pressoir la structure d'un livre, produire ses pages en html et les visualiser.
:::



## Pré-requis techniques

L'installation de [Python 3.8+](https://www.python.org/downloads/release/python-380/) sur votre ordinateur est requise pour pouvoir générer un livre.

Est également nécessaire l'installation de [Pandoc 3+](https://pandoc.org/installing.html).


## Installation 

Pour éviter d'installer et de mettre à jour Pressoir localement sur votre ordinateur, vous pouvez passer par le gestionnaire de paquets Python 'UV'. Vous trouverez des indications pour installer UV sur votre machine [à ce lien](https://docs.astral.sh/uv/getting-started/installation/). 

## Initialiser un livre

Initialiser un livre permet d'obtenir un modèle de livre prêt à remplir. Via le gestionnaire UV&nbsp;:
    
    $ uv run --with pressoir pressoir init 

la partie `uv run --with pressoir` permet d'appeler le paquet du Pressoir avec UV, puis celle `pressoir init` de lancer la commande de génération d'un livre 'coquille'.

Le modèle de livre est un dossier avec deux sous-dossiers --&nbsp;`textes` et `pressoir`&nbsp;-- comprenant l'ensemble des éléments nécessaires à la production d'un livre&nbsp;: sous-dossiers et fichiers prêts à remplir et/ou à personnaliser[^1].


## Construire un livre

Pour produire (`build`) les pages html du livre au complet&nbsp;:

    $ uv run --with pressoir pressoir build



Il est possible de produire la page html d'un seul chapitre&nbsp;:

    $ uv run --with pressoir pressoir build --chapter=introduction

    ou

    $ uv run --with pressoir pressoir build --chapter=chapitre1


Si vous êtes en local / développement, ajouter l’option `--local` pour que les liens de parcours du livre fonctionnent&nbsp;:

    $ pressoir build --local

Un dossier `public` est alors automatiquement créé dans `MonLivre`.


## Visualiser un livre

Pour visualiser (`serve`) les pages html précédemment produites&nbsp;:

    $ uv run --with pressoir pressoir serve

Cette commande produit des fichiers html qui sont déposés dans le dossier `public` créé par la précédente commande.


Le livre --&nbsp;ou site statique&nbsp;-- est prêt, selon les paramètres définis par défaut. Les syntaxes employées et les fonctionnalités disponibles sont illustrées dans le modèle de livre[^2]. À vous de jouer pour le personnaliser selon les besoins et les particularités de votre publication&nbsp;!




## Détail des commandes

Pour accéder à la liste des commandes principales&nbsp;:

    $ uv run --with pressoir pressoir --help

Pour obtenir la liste complète des commandes disponibles, se reporter au [README du dépôt](https://gitlab.huma-num.fr/ecrinum/pressoir/-/blob/main/README.md?ref_type=heads#help).


## Générer la documentation


Cette documentation a été produite par le Pressoir.

Pour la générer et la visualiser en local, sur votre ordinateur, utiliser la commande suivante&nbsp;:

    $ uv run --with pressoir pressoir docs serve


Elle sera visible à l’adresse suivante&nbsp;:

[http://127.0.0.1:8000/index.html](http://127.0.0.1:8000/index.html)


!contenuadd(./CreditsDoc)





[^1]: Pour en savoir plus, voir le chapitre [«&nbsp;Créer un livre&nbsp;»](chapitre2.html).

[^2]: Voir le chapitre [«&nbsp;Créer un livre&nbsp;»](chapitre2.html).
