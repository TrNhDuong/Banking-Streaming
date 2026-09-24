# Infra

CLI-first local workflow:

```bash
python platform.py --env-file .env.local local up --db postgres
python platform.py --env-file .env.local cdc setup --db postgres
python platform.py --env-file .env.local connector apply --db postgres
```

Supported connector adapters: PostgreSQL, MySQL, SQL Server.

CDC specifics:
- PostgreSQL: logical WAL + replication user + publication.
- MySQL: ROW binlog + replication privileges.
- SQL Server: database CDC + per-table CDC.
