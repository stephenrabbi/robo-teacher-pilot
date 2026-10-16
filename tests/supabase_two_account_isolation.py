"""Opt-in cross-account Supabase Auth + Data API smoke test.

Requires two PRE-EXISTING disposable users with separate verified synthetic
learner profiles and progress in the Robo-Teacher project. Do not point at
real learner accounts. Never prints passwords or tokens.
"""
import os
import sys
import httpx

KEYS=("ROBO_TEST_SUPABASE_URL","ROBO_TEST_SUPABASE_PUBLISHABLE_KEY",
      "ROBO_TEST_USER_A_EMAIL","ROBO_TEST_USER_A_PASSWORD",
      "ROBO_TEST_USER_B_EMAIL","ROBO_TEST_USER_B_PASSWORD")

def sign_in(client,base,key,email,password):
    r=client.post(base+"/auth/v1/token?grant_type=password",
        headers={"apikey":key,"Content-Type":"application/json"},
        json={"email":email,"password":password})
    r.raise_for_status()
    body=r.json()
    if not body.get("access_token") or not body.get("user",{}).get("id"):
        raise RuntimeError("Test login did not return a valid user session")
    return body["access_token"],body["user"]["id"]

def read_rows(client,base,key,token,table):
    r=client.get(base+"/rest/v1/"+table,params={"select":"*"},
        headers={"apikey":key,"Authorization":"Bearer "+token})
    r.raise_for_status()
    return r.json()

def main():
    absent=[x for x in KEYS if not os.environ.get(x)]
    if absent:
        print("NOT RUN: missing configured synthetic-account test environment")
        return 2
    base=os.environ["ROBO_TEST_SUPABASE_URL"].rstrip("/")
    if base!="https://gpshctxxgjvzplrbegwf.supabase.co":
        raise RuntimeError("Unexpected Supabase project; test intentionally pinned")
    key=os.environ["ROBO_TEST_SUPABASE_PUBLISHABLE_KEY"]
    with httpx.Client(timeout=20.0) as client:
        token_a,uid_a=sign_in(client,base,key,os.environ["ROBO_TEST_USER_A_EMAIL"],os.environ["ROBO_TEST_USER_A_PASSWORD"])
        token_b,uid_b=sign_in(client,base,key,os.environ["ROBO_TEST_USER_B_EMAIL"],os.environ["ROBO_TEST_USER_B_PASSWORD"])
        if uid_a==uid_b:
            raise RuntimeError("Test requires distinct Auth user IDs")
        a_profiles=read_rows(client,base,key,token_a,"robo_learner_profiles")
        b_profiles=read_rows(client,base,key,token_b,"robo_learner_profiles")
        a_progress=read_rows(client,base,key,token_a,"robo_learning_progress")
        b_progress=read_rows(client,base,key,token_b,"robo_learning_progress")
        # Both accounts MUST be enrolled with nonempty fixtures so empty
        # database results cannot count as successful isolation tests.
        if not all((a_profiles,b_profiles,a_progress,b_progress)):
            raise RuntimeError("Missing synthetic fixtures: cannot verify isolation")
        for name,rows,uid in (("A profiles",a_profiles,uid_a),("B profiles",b_profiles,uid_b),
                              ("A progress",a_progress,uid_a),("B progress",b_progress,uid_b)):
            if any(row.get("user_id")!=uid for row in rows):
                raise RuntimeError(name+" contained another user's record")
        print("PASS: two independently authenticated synthetic accounts isolated in profile and progress reads")
    return 0

if __name__=="__main__":
    try: sys.exit(main())
    except (httpx.HTTPError,RuntimeError) as exc:
        print("FAIL:",type(exc).__name__,str(exc).split("https://")[0][:140])
        sys.exit(1)
