# sudo test

```bash{sudo=yes,run="Who am I?"}
whoami
```

```json{file=/tmp/test.json,sudo=yes}
{
  "name": "John",
  "age": 30
}
```

```bash{run="View the JSON file"}
ls -l /tmp/test.json
```

```bash{sudo=yes,run="Delete the JSON file"}
rm /tmp/test.json
```
