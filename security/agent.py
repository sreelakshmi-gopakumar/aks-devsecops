"""
Security agent for the AKS DevSecOps project.

This runs a ReAct loop — the LLM picks which tools to call,
we run them, feed the results back, and repeat until it's done.
The difference from a regular LLM call is that the model drives
the whole audit. It decides what to check, in what order, and
what to do about what it finds.
"""

import json
import os
import subprocess
import time
from kubernetes import client, config
from groq import Groq

# Connect to Kubernetes.
# load_incluster_config() works when running inside the cluster as a CronJob.
# load_kube_config() works when running locally from your Mac.
try:
    config.load_incluster_config()
except Exception:
    config.load_kube_config()

k8s_apps = client.AppsV1Api()
k8s_net  = client.NetworkingV1Api()
k8s_rbac = client.RbacAuthorizationV1Api()
k8s_core = client.CoreV1Api()

llm = Groq(api_key=os.environ["GROQ_API_KEY"])

# These are the tools the LLM can call.
# Each one describes what the tool does and what parameters it takes.
# The LLM reads these descriptions and decides which tool fits each situation.
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_deployments",
            "description": "Get Kubernetes Deployments and their security settings. Use this to check for missing resource limits, containers running as root, missing health probes, and privilege escalation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "namespace": {
                        "type": "string",
                        "description": "Namespace to check. Use 'all' to check every namespace."
                    }
                },
                "required": ["namespace"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_network_policies",
            "description": "Get all NetworkPolicy objects. Use this to check whether namespaces have network isolation. Missing network policies mean pods can talk to each other freely.",
            "parameters": {
                "type": "object",
                "properties": {
                    "namespace": {
                        "type": "string",
                        "description": "Namespace to check. Use 'all' for every namespace."
                    }
                },
                "required": ["namespace"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_rbac_bindings",
            "description": "Get ClusterRoleBindings to check for overly permissive RBAC, such as service accounts bound to cluster-admin.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "apply_fix",
            "description": "Apply a kubectl patch to fix a misconfiguration. Only use this for LOW or MEDIUM severity findings where the fix is safe.",
            "parameters": {
                "type": "object",
                "properties": {
                    "resource_type": {
                        "type": "string",
                        "description": "Kubernetes resource type, e.g. deployment"
                    },
                    "resource_name": {
                        "type": "string",
                        "description": "Name of the resource to patch"
                    },
                    "namespace": {
                        "type": "string",
                        "description": "Namespace the resource lives in"
                    },
                    "patch_json": {
                        "type": "string",
                        "description": "JSON patch string to apply"
                    }
                },
                "required": ["resource_type", "resource_name",
                             "namespace", "patch_json"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "report_finding",
            "description": "Record a security finding. Call this for every issue found.",
            "parameters": {
                "type": "object",
                "properties": {
                    "control_id": {
                        "type": "string",
                        "description": "CIS Kubernetes Benchmark control ID, e.g. 5.2.6"
                    },
                    "severity": {
                        "type": "string",
                        "enum": ["HIGH", "MEDIUM", "LOW", "INFO"],
                        "description": "How serious this finding is"
                    },
                    "finding": {
                        "type": "string",
                        "description": "What the problem is, in plain language"
                    },
                    "remediation": {
                        "type": "string",
                        "description": "How to fix it"
                    },
                    "auto_fixed": {
                        "type": "boolean",
                        "description": "Whether the agent already applied a fix"
                    }
                },
                "required": ["control_id", "severity",
                             "finding", "remediation", "auto_fixed"]
            }
        }
    }
]


# ── Tool implementations ──────────────────────────────────────────────────────

def get_deployments(namespace="all"):
    """Pull deployment specs and extract the security-relevant fields."""
    if namespace == "all":
        deps = k8s_apps.list_deployment_for_all_namespaces()
    else:
        deps = k8s_apps.list_namespaced_deployment(namespace)

    result = []
    for d in deps.items:
        for c in d.spec.template.spec.containers:
            sc = c.security_context
            result.append({
                "deployment": d.metadata.name,
                "namespace": d.metadata.namespace,
                "run_as_non_root": sc.run_as_non_root if sc else None,
                "allow_privilege_escalation": (
                    sc.allow_privilege_escalation if sc else None
                ),
                "has_resource_limits": (
                    c.resources.limits is not None
                    if c.resources else False
                ),
                "liveness_probe": c.liveness_probe is not None,
                "readiness_probe": c.readiness_probe is not None,
            })
    # keep only 5 results and skip indentation to save tokens
    return json.dumps(result[:5])


def get_network_policies(namespace="all"):
    """List network policies so the agent can spot unprotected namespaces."""
    if namespace == "all":
        nets = k8s_net.list_network_policy_for_all_namespaces()
    else:
        nets = k8s_net.list_namespaced_network_policy(namespace)

    return json.dumps([{
        "name": n.metadata.name,
        "namespace": n.metadata.namespace,
        "policy_types": n.spec.policy_types
    } for n in nets.items])


def get_rbac_bindings():
    """List cluster role bindings and flag anything bound to cluster-admin."""
    bindings = k8s_rbac.list_cluster_role_binding()
    return json.dumps([{
        "name": b.metadata.name,
        "role": b.role_ref.name,
        "subjects": [s.name for s in (b.subjects or [])]
    } for b in bindings.items[:10]])


def apply_fix(resource_type, resource_name, namespace, patch_json):
    """Run kubectl patch to apply a fix the agent decided on."""
    cmd = [
        "kubectl", "patch",
        resource_type, resource_name,
        "-n", namespace,
        "--type=merge",
        "--patch", patch_json
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        return json.dumps({"success": True,
                           "message": result.stdout.strip()})
    return json.dumps({"success": False,
                       "error": result.stderr.strip()})


findings = []

def report_finding(control_id, severity, finding,
                   remediation, auto_fixed=False):
    """Store a finding. Update existing entry instead of adding a duplicate."""
    for existing in findings:
        if existing["control_id"] == control_id and \
           existing["finding"] == finding:
            if auto_fixed:
                existing["auto_fixed"] = True
            return json.dumps({"logged": True})

    entry = {
        "control_id": control_id,
        "severity": severity,
        "finding": finding,
        "remediation": remediation,
        "auto_fixed": auto_fixed
    }
    findings.append(entry)
    fixed_tag = " [AUTO-FIXED]" if auto_fixed else ""
    print(f"  [{severity}] {control_id}: {finding}{fixed_tag}")
    return json.dumps({"logged": True})


def call_tool(name, args):
    """Route a tool call from the LLM to the right Python function."""
    if name == "get_deployments":
        return get_deployments(**args)
    elif name == "get_network_policies":
        return get_network_policies(**args)
    elif name == "get_rbac_bindings":
        return get_rbac_bindings()  # takes no args — ignore whatever LLM passes
    elif name == "apply_fix":
        return apply_fix(**args)
    elif name == "report_finding":
        return report_finding(**args)
    return json.dumps({"error": f"unknown tool: {name}"})


# ── Agent loop ────────────────────────────────────────────────────────────────

def run_agent():
    """
    The ReAct loop.

    Each iteration:
    1. Send the conversation history to the LLM
    2. LLM responds with tool_calls (what it wants to do next)
    3. We run those tools
    4. We add the results to the conversation
    5. Repeat until the LLM stops calling tools

    The LLM sees the full conversation history each time, so it knows
    what it already checked and what it found. This is what lets it
    make decisions rather than just follow a fixed script.
    """
    messages = [
        {
            "role": "user",
            "content": (
                "You are a Kubernetes security agent. "
                "Audit this cluster against CIS Kubernetes Benchmark v1.9. "
                "Do these three checks one at a time: "
                "1) get_deployments to check resource limits and security context. "
                "2) get_network_policies to check namespace isolation. "
                "3) get_rbac_bindings to check for over-permissive roles. "
                "For LOW or MEDIUM findings use apply_fix. "
                "Always call report_finding for every issue. "
                "Stop after all three checks are done."
            )
        }
    ]

    print("\n=== Security agent starting ===\n")
    MAX_ITERATIONS = 15

    for i in range(MAX_ITERATIONS):
        print(f"--- Iteration {i + 1} ---")

        # Wait 3 seconds between API calls to stay within
        # Groq's free tier rate limit of 12,000 tokens per minute
        if i > 0:
            time.sleep(3)

        try:
            response = llm.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
                max_tokens=1000,
                parallel_tool_calls=False
            )
        except Exception as e:
            # If we still hit the rate limit, wait longer and retry once
            if "rate_limit" in str(e).lower() or "429" in str(e):
                print(f"  Rate limit hit — waiting 15 seconds...")
                time.sleep(15)
                response = llm.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=messages,
                    tools=TOOLS,
                    tool_choice="auto",
                    max_tokens=1000,
                    parallel_tool_calls=False
                )
            else:
                raise

        msg = response.choices[0].message

        # Add the assistant's response to conversation history
        messages.append({
            "role": "assistant",
            "content": msg.content or "",
            "tool_calls": [
                tc.model_dump() for tc in (msg.tool_calls or [])
            ]
        })

        # If no tool calls, the agent decided it's done
        if not msg.tool_calls:
            print("\nAgent finished.")
            if msg.content:
                print(f"Summary: {msg.content}")
            break

        # Run each tool the agent requested
        for tc in msg.tool_calls:
            fn_name = tc.function.name

            # The LLM sometimes generates slightly malformed JSON.
            # Clean it up before parsing so the agent doesn't crash.
            try:
                raw_args = tc.function.arguments
                raw_args = raw_args.replace("\\'", "'")
                fn_args = json.loads(raw_args)
            except json.JSONDecodeError as e:
                print(f"  skipping {fn_name} — could not parse args: {e}")
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": json.dumps({
                        "error": "invalid arguments, skipping"
                    })
                })
                continue

            print(f"  calling {fn_name}({fn_args})")
            result = call_tool(fn_name, fn_args)

            # Feed the result back so the LLM can reason about it
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result
            })

    return findings


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    results = run_agent()

    print("\n=== Audit complete ===\n")
    print(json.dumps(results, indent=2))

    high   = sum(1 for f in results if f["severity"] == "HIGH")
    medium = sum(1 for f in results if f["severity"] == "MEDIUM")
    low    = sum(1 for f in results if f["severity"] == "LOW")
    info   = sum(1 for f in results if f["severity"] == "INFO")
    fixed  = sum(1 for f in results if f["auto_fixed"])

    print(f"\nTotal findings : {len(results)}")
    print(f"  HIGH         : {high}")
    print(f"  MEDIUM       : {medium}")
    print(f"  LOW          : {low}")
    print(f"  INFO         : {info}")
    print(f"  Auto-fixed   : {fixed}")