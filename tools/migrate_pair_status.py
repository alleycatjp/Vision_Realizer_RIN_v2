import json, shutil, pathlib
CFG = pathlib.Path(__file__).resolve().parent.parent / 'config/pair_status.json'
BAK = CFG.with_suffix('.bak')
with CFG.open() as f:
    old = json.load(f)
if old.get('schema_version') == 2:
    print('already v2'); exit()
new = {'cp': {'bitbank': old}, 'schema_version': 2}
shutil.copy(CFG, BAK)
with CFG.open('w') as f:
    json.dump(new, f, ensure_ascii=False, indent=2)
print('migrated -> v2 (backup:', BAK, ')')
