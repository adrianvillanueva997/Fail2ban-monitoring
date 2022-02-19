# Fail2ban-monitoring

Scripts to monitor SSH banned ips with fail2ban and display all the data in grafana. The database is not created by default, you need to create it, the package contains mysql but feel free to change it to any other db.

The default database is Grafana and the table is ips, the default table schema is: ip,country, city, zip, lat, lng, isp, curdate()

![Dashboard](https://raw.githubusercontent.com/adrianvillanueva997/Fail2ban-monitoring/master/dashboard.png)
