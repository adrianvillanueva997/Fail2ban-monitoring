# Fail2ban-monitoring

![Dashboard](https://raw.githubusercontent.com/adrianvillanueva997/Fail2ban-monitoring/master/dashboard.png)

## Datamodel

```mermaid
erDiagram
    FAIL2BAN {
        id BIGINT
        ip VARCHAR(255)
        isp VARCHAR(255)
        city VARCHAR(255)
        zip VARCHAR(255)
        latitude FLOAT
        longitude FLOAT
        PRIMARY KEY(id)
    }
```
