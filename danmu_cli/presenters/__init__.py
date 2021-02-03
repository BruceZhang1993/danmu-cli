import importlib


def get_presenter(name: str):
    module = importlib.import_module(f'.{name}', 'danmu_cli.presenters')
    return getattr(module, f'{name.capitalize()}Presenter')
