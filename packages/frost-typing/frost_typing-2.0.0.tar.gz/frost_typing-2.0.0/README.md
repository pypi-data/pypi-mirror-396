# FrostTyping

It offers a **very** fast way to validate data using Python type hints.  
In addition to validation, it provides fast DataModels for any task!

## A Simple Example

```python
from datetime import datetime
from typing import Optional, Annotated
from frost_typing import ValidModel, Field

class User(ValidModel):
    id: int
    name: Annotated[str, Field("John Doe")]
    signup_ts: Optional[datetime]
    friends: list[int]

external_data = {'id': '123', 'signup_ts': '2017-06-01 12:22', 'friends': [1, '2', b'3']}
user = User(**external_data)
print(user)
#> User(id=123 name='John Doe' signup_ts=datetime.datetime(2017, 6, 1, 12, 22) friends=[1, 2, 3])
print(user.id)
#> 123
```

## Detailed documentation, as well as benchmarks, can be found here:

📄 [RU Русская документация](https://gitflic.ru/project/frostic/frost_typing/blob?file=docs%2Fru%2FREADME.md&branch=master&mode=markdown)  
📄 [EN English Documentation](https://gitflic.ru/project/frostic/frost_typing/blob?file=docs%2Fen%2FREADME.md&branch=master&mode=markdown)

## Quick start

You can install FrostTyping using pip:

```sh
pip install frost_typing
```
