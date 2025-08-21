# ansible-n7k-port-audit
Gathering interface status and other outputs via Ansible to export to CSV or Excel

### Running an ansible playbook against a device list or group
ansible-playbook -i ./inventory/hosts.ini main.yaml --limit 'cisco_nxos' --vault-password-file ./vault/vault_pass -vvv >> ./logs/YYYY-MM-DD_XX.log

``` Example ````
ansible-playbook -i ./inventory/hosts.ini main.yaml --limit 'cisco_nxos' --vault-password-file ./vault/vault_pass -vvv >> ./logs/2025-08-20_01.log