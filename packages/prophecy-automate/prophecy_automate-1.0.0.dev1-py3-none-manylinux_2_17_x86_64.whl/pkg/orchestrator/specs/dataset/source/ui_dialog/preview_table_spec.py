from prophecy.cb.server.base.ComponentBuilderBase import *
from prophecy.cb.ui.uispec import *
import random
class SpecBox():
    spec: Atom
    id: str
    title: str
    def __init__(self, spec: Atom, title: str):
        self.spec = spec
        self.title = title
        self.id = UISpec().getId()
    def json(self):
        return {
            "spec": self.spec.json(),
            "id": self.id,
            "title": self.title
        }



def dialog() -> PreviewTable:
    return SpecBox(PreviewTable("PREVIEW").bindProperty("format.schema"), "PREVIEW")