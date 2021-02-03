import importlib


def get_provider(name: str):
    module = importlib.import_module(f'.{name}', 'danmu_cli.providers')
    return getattr(module, f'{name.capitalize()}Provider')
