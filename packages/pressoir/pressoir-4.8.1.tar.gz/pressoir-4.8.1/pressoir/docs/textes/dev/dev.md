::: {.introchapitre}
Cette section s'adresse aux développeurs et développeuses qui souhaiteraient bidouiller le Pressoir.
:::

Vous pouvez travailler avec et sur le Pressoir sans le gestionnaire de paquets UV. Pour cela, il vous faudra vous créer un environnement virtuel sur votre machine.

!contenuadd(./EnvironnementVirtuel)

Une fois l'environnement virtuel créé, voici la commande pour installer directement le paquet Python du Pressoir sur sa machine&nbsp;:

    $ pip install pressoir

Et pour mettre à jour le paquet sur sa machine&nbsp;: 

    $ pip install -U pressoir

Puis, pour toute commande Pressoir sur la ligne de commande, vous pouvez faire les même que celles indiquées dans [prise en main](chapitre1.html), sans indiquer `uv run --with pressoir` avant une commande (telle que `pressoir init`).
