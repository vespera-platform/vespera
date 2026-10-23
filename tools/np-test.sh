#!/usr/bin/env bash
# np-test.sh: sprawdza NetworkPolicy Vespery. Wiersz = źródło, cel, port, oczekiwanie.
set -u
NS=vespera-dev
fail=0

check() {  # $1 źródło, $2 host, $3 port, $4 ALLOW|DENY
  if ! kubectl exec -n "$NS" "$1" -- true >/dev/null 2>&1; then
    echo "ERROR $1: exec nie działa (test niewiarygodny)"; fail=1; return
  fi
  if kubectl exec -n "$NS" "$1" -- python -c "import socket; socket.create_connection(('$2',$3),timeout=3)" >/dev/null 2>&1
  then got=ALLOW; else got=DENY; fi
  if [ "$got" = "$4" ]; then echo "OK    $1 -> $2:$3 $4"
  else echo "FAIL  $1 -> $2:$3 oczekiwano $4, jest $got"; fail=1; fi
}

# --- dozwolone (tabela przepływów) ---
check deploy/api       postgres    5432 ALLOW
check pod/checker-0    postgres    5432 ALLOW
check pod/checker-0    redis       6379 ALLOW
check pod/checker-0    target-sim  8000 ALLOW
check pod/checker-0    example.com 443  ALLOW
check deploy/notifier  redis       6379 ALLOW
check deploy/notifier  target-sim  8000 ALLOW

# --- odrzucone ---
check pod/target-sim-0 postgres    5432 DENY   # przejęty pod -> baza
check pod/target-sim-0 redis       6379 DENY   # fałszywe zdarzenia
check deploy/api       example.com 443  DENY   # api do internetu
check deploy/notifier  postgres    5432 DENY   # notifier -> baza
check pod/checker-0    api         80   DENY   # checker -> api
check pod/checker-0    172.20.0.4  6443 DENY   # except: node / API klastra
check pod/checker-0    example.com 5432 DENY   # internet tylko 80/443

exit $fail
