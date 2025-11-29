import sys

import json
import argparse

from agent.sla.lang.pretty_printer import SLAPrettyPrinter
from agent.sla.lang.metamodel import SLA
from agent.sla.lang.visitor import SLAVisitor


def parse_file(path: str) -> SLA:
    with open(path) as stream:
        try:
            struct = json.loads(stream.read())
            return create_model(struct)
        except json.JSONDecodeError as e:
            print("Invalid JSON syntax:", e)

    return None

def parse_str(content: str) -> SLA:
    try:
        struct = json.loads(content)
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
        return sla



if __name__ == '__main__':
    argparser = argparse.ArgumentParser(
        prog='AgentSLA Parser/Validator',
        description='Program validating, parsing and instantiating AgentSLA model')
    argparser.add_argument('path', help='Path of the file to parse/validate')
    args = argparser.parse_args()
    sla = parse_file(args.path)
    if sla is None:
        sys.exit(1)
    print("Model parsed and validated")
    print()
    print("Pretty printed version of the model:")
    print()
    json_pp = SLAPrettyPrinter(sla).json()
    print(json_pp)

    sla = parse_str(json_pp)
    if sla is None:
        sys.exit(1)