def __find_protocols(root_dir):
    import os

    prot_dir = os.path.join(root_dir, "acellera-protocols")

    if os.path.exists(root_dir) and os.path.exists(prot_dir):
        from glob import glob
        import importlib
        import sys

        sys.path.insert(0, prot_dir)

        for file in glob(os.path.join(prot_dir, "**", "*.py"), recursive=True):
            if file.endswith("__init__.py"):
                continue
            rel_path = os.path.relpath(file[:-3], prot_dir)
            mod_name = rel_path.replace(os.path.sep, ".")
            parts = mod_name.split(".")

            for i in range(len(parts)):
                submod = ".".join(parts[: i + 1])
                sys.modules[__name__ + "." + submod] = importlib.import_module(
                    submod, package=__name__
                )

            # Append tutorials to the docs of the protocol
            dirname = os.path.dirname(file)
            pieces = rel_path.split(os.path.sep)
            # Check if the loaded module is the actual protocol file
            if len(pieces) == 4 and pieces[1] == pieces[3]:
                # Check if there are files/tutorials
                nb_tuts = glob(os.path.join(dirname, "files", "tutorials", "*.ipynb"))
                if len(nb_tuts):
                    # Modify the docs of the protocol
                    main_func = getattr(sys.modules[__name__ + "." + submod], pieces[1])
                    main_func.__doc__ = (
                        main_func.__doc__
                        + "\n\nNotes\n-----\nTutorials are available for this protocol:\n\n"
                        + "\n".join([f"    - {t}" for t in nb_tuts])
                    )

        return sys.modules[__name__ + ".protocols"]
    return None
