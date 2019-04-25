# sqpy (pronounced skippy)
##### is a CSV exporter from MSSQL using pyodbc
It's meant to replace sqsh, but is much poorer in features and much less complex

## Prerequisites
This package uses [MS ODBC driver](https://docs.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server?view=sql-server-2017). 

#### On Debian or Ubuntu, this should be sufficient:

```sh
sudo su 
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -

#Download appropriate package for the OS version
#Choose only ONE of the following, corresponding to your OS version

#Debian 8
curl https://packages.microsoft.com/config/debian/8/prod.list > /etc/apt/sources.list.d/mssql-release.list

#Debian 9
curl https://packages.microsoft.com/config/debian/9/prod.list > /etc/apt/sources.list.d/mssql-release.list

#Ubuntu 14.04
curl https://packages.microsoft.com/config/ubuntu/14.04/prod.list > /etc/apt/sources.list.d/mssql-release.list

#Ubuntu 16.04
curl https://packages.microsoft.com/config/ubuntu/16.04/prod.list > /etc/apt/sources.list.d/mssql-release.list

#Ubuntu 18.04
curl https://packages.microsoft.com/config/ubuntu/18.04/prod.list > /etc/apt/sources.list.d/mssql-release.list

#Ubuntu 18.10
curl https://packages.microsoft.com/config/ubuntu/18.10/prod.list > /etc/apt/sources.list.d/mssql-release.list

exit
sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install msodbcsql17
```

#### On RHEL

```sh
sudo su

#Download appropriate package for the OS version
#Choose only ONE of the following, corresponding to your OS version

#RedHat Enterprise Server 6
curl https://packages.microsoft.com/config/rhel/6/prod.repo > /etc/yum.repos.d/mssql-release.repo

#RedHat Enterprise Server 7
curl https://packages.microsoft.com/config/rhel/7/prod.repo > /etc/yum.repos.d/mssql-release.repo

exit
sudo yum remove unixODBC-utf16 unixODBC-utf16-devel #to avoid conflicts
sudo ACCEPT_EULA=Y yum install msodbcsql17
# optional: for bcp and sqlcmd
sudo ACCEPT_EULA=Y yum install mssql-tools
echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bash_profile
echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc
source ~/.bashrc
# optional: for unixODBC development headers
sudo yum install unixODBC-devel
```

#### On Mac OS

```sh
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
brew update
brew install msodbcsql17
```

#### On Arch Linux

```sh
yay -S mssql-tools
```

## Setup

### Dev libraries for Linux:
```sh
# Debian only
sudo apt-get install g++

# Ubuntu / Debian
sudo apt install unixodbc-dev

# RHEL, CentOS
sudo yum install gcc-c++ python-devel unixODBC-devel

# Fedora
sudo dnf install redhat-rpm-config gcc-c++ unixODBC-devel

# OpenSUSE
sudo zypper install gcc-c++ unixODBC-devel
```


#### Option 1: In a virtual environment:

```sh
python setup.py install
```

#### Option 2: Install globally

```sh
sudo pip install git+https://github.com/kfzteile24/sqpy.git
```

## Usage example

Using freetds-compatible aliases, defined in `/etc/freetds/freetds.conf`

```sh
echo "SELECT TOP 10 * FROM my_table" | sqpy -U sqpy_user -P 'very secret' -S my_db_alias -D my_db -m csv > result.csv
```

for other usages consult help:

```sh
sqpy --help
```

---

Note that this library will remove the extra `\go` from the end of the query, and also clears the escape sequences for the `$` symbol that was necessary for sqsh. It doesn't support sqsh parameters.

If you're having trouble with encoding of queries or of the formation of the output, set the `PYTHONIOENCODING` environment variable when calling this script. Example:

```sh
cat query.sql | PYTHONIOENCODING=UTF-8 sqpy [...] -m csv
```
