```bash{run="Working directory of the task"}
pwd
```

```bash{run="fail test"}
echo failing
sleep 1
false
```

```json{file=/tmp/test.json}
{
  "name": "John",
  "age": 30
}
```

```bash{run="View the JSON file"}
cat /tmp/test.json
```

```bash{run="Delete the JSON file"}
rm /tmp/test.json
```
