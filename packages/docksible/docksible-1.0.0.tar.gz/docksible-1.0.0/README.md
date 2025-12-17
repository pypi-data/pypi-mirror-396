# Docksible

## About

Install a Dockerized web app on a given remote VPS, with a single command
in your local CLI - powered by Ansible.

Supports SSL, so it's perfect for quick demo servers, or even lightweight production
environments.

You can also install on localhost or local VMs, perfect for local experiments
with different types of apps.

## Features

* WordPress
* Joomla
* Redmine (open source issue tracker)
* "Custom app" - you simply provide a valid container name (from Docker Hub),
  and any required app specific environment variables (via `--extra-env-vars`), and it should work.
* SSL certs, including test certs
* SSH proxy to tunnel hidden services like database
* phpMyAdmin container
* Hopefully more soon ;-)

## Requirements

* Local: Unix with Python 3.9 or newer. Tested this on Gentoo and Ubuntu Linux.
  Might work on macOS, but I don't know. Won't work on Windows, because it uses
  Ansible under the hood, which AFAIK is not supported for Windows.
* Remote: VPS running Ubuntu, or maybe other Debian based flavor, reachable via SSH.
  It should probably work on all Debian distros, but I have only tested on Ubuntu.

## Installing

Intall with Pip: `python -m pip install docksible`

## Usage

These examples should be self explanatory:

* `docksible user@example.com wordpress --letsencrypt --email admin@example.com`
* `docksible user@example.com redmine --letsencrypt --email admin@example.com`

Run the `--help` flag for all supported options.

### Using the SSH proxy

You can include a [simple SSH proxy](https://github.com/belal-i/simple-ssh-proxy)
into your app's Docker network, by passing the `--ssh-proxy` flag. This will drop in
a small container that you can use to port forward some hidden services, like the
database. Here's how to do it:

* Include `--ssh-proxy` in the Docksible command (ex: `docksible user@host wordpress --ssh-proxy`)
* Set up the proxy service's `authorized_keys` file. This will be improved in the future,
  but until then:
  * SSH into your server as root
  * Copy root's `.ssh/authorized_keys` into `docksible-volumes/ssh-proxy-data/`
  * Shell into the proxy container, and basically `chown -R proxy_user:proxy_user /home/proxy_user`.
    This could also be improved, but for now, just needs to be done once.
* Now the proxy service is ready to use. For example:
  * Set up the tunnel to proxy the database:
  ```
  ssh -p 2222 proxy_user@yourserver.com -L 9000:docksible_db:3306
  ```
  * Connect to the database:
  ```
  mysql -u your_db_user -p --port=9000 --host=localhost --protocol=TCP
  ```
