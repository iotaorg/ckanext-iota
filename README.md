ckanext-iota
============

Plugin para sincronizar dados do [Iota] com uma instância do [CKAN].

Dependências
------------

* [CKAN] >= 2.0
* [ckanext-harvest]

Instalando
----------

1. Instale o plugin no seu ambiente python:

    pip install -e git+https://github.com/AwareTI/ckanext-iota.git#egg=ckanext-iota

2. Adicione na linha com ```ckan.plugins``` no arquivo de configuração
do CKAN os plugins ```harvest``` e ```iota_harvester```.

Usando
------

1. Vá até a página para criar um novo _Harvest Source_ no CKAN, normalmente
em ```/harvest/new```;

2. No campo URL, coloque o endereço do dataset que você quer importar do Iota.
   Por exemplo, para importar São Paulo, coloque
```http://indicadores.cidadessustentaveis.org.br/br/sp/sao-paulo``` (não
esqueça do ```http://```). Adicione o título e descrição que preferir;

3. Selecione o ```Iota``` em ```Source type```. Se ele não aparecer aqui, sua
   houve algum problema na sua instalação;

4. Clique em salvar.

Pronto, na próxima vez que o ```ckanext-harvest``` executar, os indicadores
serão importados e os datasets criados.

Adicionando os datasets a grupos
--------------------------------

É possível configurar o plugin para adicionar os datasets a um ou mais grupos
automaticamente, quando forem importados. Para isto, primeiro precisamos criar
um grupo. Depois de criado, anote seu ID. Você consegue descobrir indo na
página do grupo e olhando a URL. Ela deve ser algo como:

    http://demo.ckan.org/group/sao-paulo

Nesse caso, o ID do grupo é ```sao-paulo```. Anote os IDs de todos os grupos
que você queira usar. Daí, ao criar o _Harvest Source_ como explicado acima,
adicione no campo _Configuration_:

```json
{ "groups": ["brasil", "sao-paulo"] }
```

Nesse caso, todos os datasets carregados serão adicionados aos grupos
```brasil``` e ```sao-paulo```. Se, depois, você mudar de ideia e quiser
adicionar ou retirar algum grupo, basta modificar esse campo no _Harvest
Source_ que, quando o ```ckanext-harvest``` executar, ele irá atualizar os
datasets.

[CKAN]: http://ckan.org
[Iota]: https://github.com/AwareTI/Iota
[ckanext-harvest]: http://github.com/okfn/ckanext-harvest
