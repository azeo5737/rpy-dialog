# rpy-dialog
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