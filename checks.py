# Copyright 2017 Platform9 Systems Inc. (http://www.platform9.com)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import client as k8s

def scheduledjob():
    url = '/apis/batch/v2alpha1/scheduledjobs'
    r = k8s.get(url)
    if r.status_code == 404:
        return True, "Resource not found"
    if r.status_code != 200:
        return False, "Unexpected HTTP error: %s" % r.status_code
    sjobs = r.json()['items']
    if sjobs:
        return False, "You must delete all PodDisruptionBudget objects that you have created. It is not possible to delete these objects after you upgrade, and their presence will prevent you from using the beta PodDisruptionBudget feature in 1.5."
    else:
        return True, "No ScheduledJob objects found"

def petset():
    url = '/apis/apps/v1alpha1/petsets'
    r = k8s.get(url)
    if r.status_code == 404:
        return True, "Resource not found"
    if r.status_code != 200:
        return False, "Unexpected HTTP error: %s" % r.status_code
    petsets = r.json()['items']
    if petsets:
        return False, "PetSet has been renamed to StatefulSet. You must perform extra migration steps both before and after upgrading to convert them to StatefulSets. See http://kubernetes.io/docs/tasks/manage-stateful-set/upgrade-pet-set-to-stateful-set"
    else:
        return True, "No PetSet objects found"

def poddisruptionbudget():
    url = '/apis/extensions/v2alpha1/poddisruptionbudgets'
    r = k8s.get(url)
    if r.status_code == 404:
        return True, "Resource not found"
    if r.status_code != 200:
        return False, "Unexpected HTTP error: %s" % r.status_code
    budgets = r.json()['items']
    if budgets:
        return False, "You must delete all PodDisruptionBudget objects that you have created. It is not possible to delete these objects after you upgrade, and their presence will prevent you from using the beta PodDisruptionBudget feature in 1.5."
    else:
        return True, "No PodDisruptionBudget objects found"

def certificatesigningrequest():
    url = '/apis/certificates.k8s.io/v1alpha1/certificatesigningrequests'
    r = k8s.get(url)
    if r.status_code == 404:
        return True, "Resource not found"
    if r.status_code != 200:
        return False, "Unexpected HTTP error: %s" % r.status_code
    csrs = r.json()['items']
    if csrs:
        return False, "You must delete all CertificateSigningRequest objects that you have created, then re-create them after upgrading."
    else:
        return True, "No CertificateSigningRequest objects found"


def deployments_overlapping_selectors():
    url = '/apis/extensions/v1beta1/deployments'
    r = k8s.get(url)
    if r.status_code == 404:
        return True, "Resource not found"
    if r.status_code != 200:
        return False, "Unexpected HTTP error: %s" % r.status_code
    d_objs = r.json()['items']
    if not d_objs:
        return True, "No Deployment objects found"

    deployments_by_namespace_and_selector = {}
    for d in d_objs:
        dname = d['metadata']['name']
        dns = d['metadata']['namespace']
        for k, v in d['spec']['selector']['matchLabels'].iteritems():
            sel = k + ":" + v
            if dns not in deployments_by_namespace_and_selector:
                deployments_by_namespace_and_selector[dns] = {}
            if sel not in deployments_by_namespace_and_selector[dns]:
                deployments_by_namespace_and_selector[dns][sel] = []
            deployments_by_namespace_and_selector[dns][sel].append(dname)
    msgs = []
    for ns, ss in deployments_by_namespace_and_selector.iteritems():
        for sel, ds in ss.iteritems():
            if len(ds) > 1:
                msgs.append("%s in namespace %s overlap selector %s" % (ds, ns, sel))
    if msgs:
        return False, ", ".join(msgs)
    else:
        return True, "Deployments have disjoint selectors"

def kubelet_pre_1_0():
    url = '/api/v1/nodes'
    r = k8s.get(url)
    if r.status_code == 404:
        return True, "Resource not found"
    if r.status_code != 200:
        return False, "Unexpected HTTP error: %s" % r.status_code
    nodes = r.json()['items']
    pre_1_0_nodes = []
    for node in nodes:
        if node['status']['nodeInfo']['kubeletVersion'] < "v1.0.0":
            pre_1_0_nodes.append(node['metadata']['name'])
    if pre_1_0_nodes:
        return False, "Nodes %s run kubelet < v1.0.0. Upgrade directly from pre-1.0 to 1.6 kubelet is not supported." % pre_1_0_nodes
    else:
        return True, "All nodes run kubelet >= v1.0.0"

# affected version, action required, check function
checks = [
        ("1.5", True, petset),
        ("1.5", True, poddisruptionbudget),
        ("1.6", True, certificatesigningrequest),
        ("1.6", False, scheduledjob),
        ("1.6", True, deployments_overlapping_selectors),
        ("1.6", True, kubelet_pre_1_0),
        ("1.7", False, scheduledjob),
        ("1.8", True, scheduledjob),
        ]
