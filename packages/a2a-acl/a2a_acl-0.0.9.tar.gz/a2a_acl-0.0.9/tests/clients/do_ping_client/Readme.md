A client that just sends an achieve/do_ping ACL message to a pinger agent at port 9999.

You can use this client with any A2A/ACL agent listening on port 9999.

Tested against a Java A2A/ACL agent (pinger agent, that sends message to a pingable agent).

First run your other agents, then run the client :

```bash
  python3 run_test_client.py
```
