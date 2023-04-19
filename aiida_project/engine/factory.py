def get_engine(engine_name, project_path):
    if engine_name == "virtualenv":
        from .virtualenv import VirtualenvEngine

        return VirtualenvEngine(project_path)
    elif engine_name == "conda":
        from .conda import CondaEngine

        return CondaEngine(project_path)
