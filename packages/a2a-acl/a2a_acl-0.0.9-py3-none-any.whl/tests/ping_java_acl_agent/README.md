Send achieve/ping ACL request to a "pingable" agent, and checks that a tell/pong ACL message is received.

This test is run with a Pingable A2A/ACL agent implemented in Java.

To launch this test, you must first run the Pingable Java agent.
```bash
  cd PATH/TO/pingable
  mvn quarkus:dev
```
The pingable agent listens on port 9998.

Then run the test client :

```bash
  python3 run_test_client.py
```

Note that the HTTP client used in the Pingable agent to send tell/pong message must use HTTP 1.1 to talk with
the uvicorn server run in the test python agent (default Client builder in a2a-java uses HTTP 2).

