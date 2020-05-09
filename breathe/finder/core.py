
from . import index as indexfinder
from . import compound as compoundfinder

from breathe.parser import DoxygenParserFactory

from sphinx.application import Sphinx


class CreateCompoundTypeSubFinder:
    def __init__(self, app: Sphinx, parser_factory: DoxygenParserFactory):
        self.app = app
        self.parser_factory = parser_factory

    def __call__(self, project_info, *args):
        compound_parser = self.parser_factory.create_compound_parser(project_info)
        return indexfinder.CompoundTypeSubItemFinder(self.app, compound_parser,
                                                     project_info, *args)


class DoxygenItemFinderFactory(object):

    def __init__(self, finders, project_info):

        self.finders = finders
        self.project_info = project_info

    def create_finder(self, data_object):

        return self.finders[data_object.node_type](self.project_info, data_object, self)


class DoxygenItemFinderFactoryCreator:
    def __init__(self, app: Sphinx, parser_factory: DoxygenParserFactory):
        self.app = app
        self.parser_factory = parser_factory

    def create_factory(self, project_info) -> DoxygenItemFinderFactory:
        finders = {
            "doxygen": indexfinder.DoxygenTypeSubItemFinder,
            "compound": CreateCompoundTypeSubFinder(self.app, self.parser_factory),
            "member": indexfinder.MemberTypeSubItemFinder,
            "doxygendef": compoundfinder.DoxygenTypeSubItemFinder,
            "compounddef": compoundfinder.CompoundDefTypeSubItemFinder,
            "sectiondef": compoundfinder.SectionDefTypeSubItemFinder,
            "memberdef": compoundfinder.MemberDefTypeSubItemFinder,
            "ref": compoundfinder.RefTypeSubItemFinder,
            }
        return DoxygenItemFinderFactory(finders, project_info)


class FakeParentNode(object):

    node_type = "fakeparent"


class Finder(object):

    def __init__(self, root, item_finder_factory):

        self._root = root
        self.item_finder_factory = item_finder_factory

    def filter_(self, filter_, matches):
        """Adds all nodes which match the filter into the matches list"""

        item_finder = self.item_finder_factory.create_finder(self._root)
        item_finder.filter_([FakeParentNode()], filter_, matches)

    def root(self):

        return self._root


class FinderFactory:
    def __init__(self, app: Sphinx, parser_factory: DoxygenParserFactory):
        self.parser = parser_factory.create_index_parser()
        self.item_finder_factory_creator = DoxygenItemFinderFactoryCreator(app, parser_factory)

    def create_finder(self, project_info):
        root = self.parser.parse(project_info)
        item_finder_factory = self.item_finder_factory_creator.create_factory(project_info)
        return Finder(root, item_finder_factory)

    def create_finder_from_root(self, root, project_info):
        item_finder_factory = self.item_finder_factory_creator.create_factory(project_info)
        return Finder(root, item_finder_factory)
