#!/bin/env python

from jinja2 import Environment, PackageLoader, select_autoescape

from .metadata import load_metadata


class UnknownParameterKindException(Exception):
    pass


def raise_helper(msg):
    raise UnknownParameterKindException(msg)


def setup_templating():
    env = Environment(
        loader=PackageLoader("climix", "etc"),
        autoescape=select_autoescape(),
    )
    env.globals["raise"] = raise_helper
    return env


def main():
    catalog, config = load_metadata(None)
    distributions = {}
    for index in catalog.get_list():
        definition = catalog.get_index_definition(index)
        distribution = definition.distribution
        indices = distributions.setdefault(distribution, {})
        indices[index] = definition
    env = setup_templating()
    template = env.get_template("indices.md.jinja")
    print(template.render(distributions=distributions))


if __name__ == "__main__":
    main()
