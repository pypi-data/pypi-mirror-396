import os

old_header = r"""# (c) 2015-2012 Acellera Ltd http://www.acellera.com
# All Rights Reserved
# Distributed under HTMD Software License Agreement
# No redistribution in whole or part
#
"""

new_header = r"""# (c) 2015-2023 Acellera Ltd http://www.acellera.com
# All Rights Reserved
# Distributed under HTMD Software License Agreement
# No redistribution in whole or part
#
"""

exclusions = "playmolecule/_version.py"

for root, dirs, files in os.walk("playmolecule"):
    for i, fname in enumerate(
        [
            os.path.join(root, file)
            for file in files
            if not any(exclusion in root for exclusion in exclusions)
        ]
    ):
        if fname in exclusions:
            continue

        if fname.endswith((".py", ".sh", ".jinja")):
            try:
                print(f"-------------------------- {fname} ---------------------------")
                with open(fname) as f:
                    print("".join(f.readlines()[:6]))
                with open(fname) as f:
                    text = f.read()

                if old_header in text:
                    text = text.replace(old_header, new_header)
                else:
                    text = new_header + text
                print("XXXXXXXXXXXXXXXX")
                print("\n".join(text.split("\n")[:10]))
                with open(fname, "w") as fout:
                    fout.write(text)
            except Exception as e:
                print(f"ERROR: {e}")
