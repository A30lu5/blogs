# No Vulnerable Services

Solution

## Stage 1:

dynamic subdomain generation in records from served-by header, footer p, etc. (X-Served-By: d8a50228.ip.no.vulnerable.services resolves to 216.165.2.40)

CSP to only allow JS from http://\*.no.vulnerable.services (and recaptcha stuff)

contact us for pricing page -> XSS

leak admin cookies by script src'ing something hosted on a VM (accessible at {ip_hex_encoded}.rev.no.vulnerable.services)

## STAGE 2:
loadbalancer running at 216.165.2.41

find that loadbalancer won't proxy support page (403) but will proxy arb IPs

find that the LB gratuitously follows redirects but doesn't whitelist check against the redirect IP

setup http server that responds with a 302 to support.no.vulnerable.services

exploit support page's ping tool (command execute)
```
127.0.0.`ls`
```
