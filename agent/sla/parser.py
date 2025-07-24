import sys

import json
import argparse

from metamodel import SLA
from visitor import SLAVisitor


def parse(path: str) -> SLA:
    with open(path) as stream:
        try:
            struct = json.loads(stream.read())
            return create_model(struct)
        except json.JSONDecodeError as e:
            print("Invalid JSON syntax:", e)

    return None

def create_model(struct) -> SLA:
    visitor = SLAVisitor()
    sla = visitor.visit_SLA(struct)
    if len(visitor.errors) > 0:
        for error in visitor.errors:
            print(str(error), file=sys.stderr)
    else:
        print("Model parsed and validated")
        return sla



if __name__ == '__main__':
    argparser = argparse.ArgumentParser(
        prog='AgentSLA Parser/Validator',
        description='Program validating, parsing and instantiating AgentSLA model')
    argparser.add_argument('path', help='Path of the file to parse/validate')
    args = argparser.parse_args()
    card = parse(args.path)
    if card is None:
        sys.exit(1)