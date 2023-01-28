# rpy-dialog

Parses dialog from an [extracted](https://github.com/Shizmob/rpatool) and [decompiled](https://github.com/CensoredUsername/unrpyc) Ren'Py archive and outputs it as JSON.

Usage:
```console
python rpy-dialog --output dialog.json ./extracted-rpa-dir
```

Output is in this format: 
```json
{
  "characters": {
    "some character A": "information about them here",
    "some other character B": "information about them here"
  },
  "messages": [
    {"speaker": "some character A", "utterance": "thing they said"},
    {"speaker": "some other character B", "utterance": "their reply"},
    {"speaker": "some character A", "utterance": "conversation keeps going"},
    {"speaker": "some other character B", "utterance": "etc."}
  ]
}
```