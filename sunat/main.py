"""Entrada del worker: API SOAP y padrón oficiales por defecto."""
import argparse

from sunat import browser, official
from sunat.browser import URL, restriction  # compatibilidad con la prueba puntual
from sunat.storage import worker_lock


def main():
    parser = argparse.ArgumentParser(description=__doc__, add_help=False)
    parser.add_argument('--source', choices=['oficial', 'formulario'], default='oficial')
    args, remaining = parser.parse_known_args()
    if args.source == 'oficial':
        official.main(remaining)
    else:
        browser.main(remaining)


if __name__ == '__main__':
    with worker_lock():
        main()
