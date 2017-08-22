# KARBU: Kubernetes Action Required Before Upgrade

*CAUTION: This is currently a working proof-of-concept, but lots of work is
planned (see the ROADMAP). Versions 1.5 and 1.6 are supported.*

Before upgrading to the next minor release of Kubernetes, cluster admins and
users are expected to check the "Action Required" section[0] in the change log for
steps they may need to take before and after upgrading. The actual steps vary
from cluster to cluster; often, it is possible to use the Kubernetes API to
identify these of steps.

KARBU is a simple command-line tool that uses the Kubernetes API to
automatically identify these steps.

## Usage
All you need is a proxied connection[1] to the cluster that will be upgraded, and
the version to which it will be upgraded (the "to" version).

```
# Establish a proxied connection to the cluster
kubectl proxy &
# Run KARBU with 1.6 as the "to" version
karbu 1.6
```

## ROADMAP
- Distribute as a single binary without dependencies (likely by rewriting in
  Go)
- Make the tool extensible so that support for an additional "Action Required"
  can be contributed without merge conflicts

----
[0] Example: https://github.com/kubernetes/kubernetes/blob/master/CHANGELOG.md#action-required-9

[1] The use of a proxied connection is by design: we want to delegate
authentication and authorization to a separate tool.
