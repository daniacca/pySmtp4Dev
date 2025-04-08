# Pysmtp4dev

![CI](https://github.com/daniacca/pysmtp4dev/actions/workflows/deploy.yml/badge.svg)
![Docker Pulls](https://img.shields.io/docker/pulls/kaelisra/pysmtp4dev)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

A lightweight, Docker-friendly debug SMTP server written in Python — ideal for development and testing email-sending applications.

---

## 🚀 Features

- Minimalistic SMTP server for local email testing
- Supports SSL connections
- Logs emails to disk (optional)
- Stores emails in memory with circular buffer
- Configurable via command-line arguments
- Can forward emails to a remote SMTP server
- Interactive shell mode available

---

## 🐳 Run with Docker

You can run `pysmtp4dev` with Docker using the provided `docker-compose.yaml`.

```bash
docker compose up -d
```

By default, the server listens on port `2525` and stores received emails in the `./email_log` directory on the host.

---

### 🛠️ Custom Configuration

The server supports various CLI flags. To override the default behavior, pass flags as arguments to the container:

```bash
docker run -p 2525:2525 kaelisra/pysmtp4dev:v1.0.0 -f -ssl -max_email 100
```

**Available flags:**

| Flag                   | Description                                                  | Default       |
| ---------------------- | ------------------------------------------------------------ | ------------- |
| `-al`                  | IP address to bind locally                                   | `0.0.0.0`     |
| `-ar`                  | Remote IP to forward emails to                               | `None`        |
| `-pl`                  | Local port to listen on                                      | `2525`        |
| `-pr`                  | Remote SMTP port to forward to                               | `None`        |
| `-f`                   | Enable file logging                                          | `False`       |
| `-ld`                  | Directory to save email logs                                 | `./email_log` |
| `-max_email`           | Maximum number of emails to keep in memory (circular buffer) | `50`          |
| `-as` / `--auto_start` | Auto-start the server                                        | `False`       |
| `-sh` / `--shell`      | Start server in interactive shell mode                       | `False`       |
| `-ssl` / `--start_ssl` | Enable SSL                                                   | `False`       |

---

## ✉️ Sending a Test Email

You can test the server using this simple Python script:

```python
import smtplib
from email.mime.text import MIMEText

msg = MIMEText('This is the body of the message.')
msg['Subject'] = 'Test Email'
msg['From'] = 'sender@example.com'
msg['To'] = 'receiver@example.com'

server = smtplib.SMTP('localhost', 2525)
server.set_debuglevel(True)
server.sendmail(msg['From'], [msg['To']], msg.as_string())
server.quit()
```

---

## 🧪 Run Tests Locally

Install dependencies in a virtual environment and run unit tests:

```bash
make venv
make test
```

---

## 🏗️ Build & Push Docker Image

Build and publish the image manually with:

```bash
make build
make push
```

> Docker tags use the latest Git tag. If no tag exists, `latest` is used.

---

## 🔁 GitHub Actions

This repository uses GitHub Actions for:

- ✅ Running tests on every Pull Request
- 🚀 Building & deploying the Docker image on new Git tags

---

## 🐙 Docker Hub

Docker images are available at:

👉 [https://hub.docker.com/r/kaelisra/pysmtp4dev](https://hub.docker.com/r/kaelisra/pysmtp4dev)

---

## 📂 Project Structure

```
.
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yaml
├── requirements.txt
├── smtp_controller
│   └── controller for smtp server and message handler
├── smtp_user_interface
│   └── execution mode, interactive CLI or passive server loop
├── smtp_utils
│   └── generic utilities modules
├── tests/
│   └── test_*.py
├── PySmtpServer.py
├── Makefile
└── README.md
```

---

## 🧩 Planned Features

- Web UI to view received emails
- Live email viewer in browser
- Email queue export/download
- Configurable SMTP forwarding rules

---

## 📄 License

This project is licensed under the terms of the [GNU General Public License v3.0](./LICENSE).

See [https://www.gnu.org/licenses/gpl-3.0.html](https://www.gnu.org/licenses/gpl-3.0.html) for more information.

---

## 🤝 Contributing

Contributions, issues and feature requests are welcome!

Feel free to:

- 🐞 Report bugs
- 💡 Suggest features
- 📥 Open pull requests

Please follow the standard [GitHub Flow](https://docs.github.com/en/get-started/quickstart/github-flow) when submitting PRs.

---

Made by [@daniacca](https://github.com/daniacca)
